# Voice Modality Diagnostic and Testing Strategy

## Executive Summary

The voice modality is currently non-functional due to an intentional backend limitation. While all audio processing components exist and are tested individually, they are not integrated into the main API flow. The backend explicitly returns HTTP 501 (Not Implemented) for audio data sent to the standard messaging endpoint.

## Current State Analysis

### Working Components

1. **Text Mode**: Fully functional with comprehensive test coverage
   - Frontend: UI components, forms, and SSE streaming
   - Backend: Complete conversation flow with all phases
   - E2E Tests: Multiple scenarios covered

2. **Audio Infrastructure**: Components exist but are disconnected
   - Audio pipeline orchestrator (`AudioPipeline`)
   - Speech-to-text service (Google Cloud Speech)
   - Text-to-speech service (Google Cloud TTS)
   - Audio format converters (WAV to PCM)
   - Unit tests for all components

### Non-Working Components

1. **Voice Mode Integration**: Missing connection between frontend and backend
   - Frontend sends audio to `/api/send/{session_id}` endpoint
   - Backend rejects audio with 501 status code
   - Audio pipeline not integrated with main conversation flow

## Root Cause Analysis

### Frontend Behavior
```javascript
// use-natural-conversation.ts
const sendAudioData = async (base64Audio: string) => {
  await apiClient.sendMessage(sessionId, {
    mime_type: 'audio/pcm',
    data: base64Audio,
  });
};
```

### Backend Response
```python
# main.py lines 623-634
elif mime_type == "audio/pcm":
    # For now, audio is not supported in non-live mode
    raise HTTPException(
        status_code=501,
        detail="Audio processing not yet implemented in request-response mode",
    )
```

The backend explicitly states that audio processing is "not yet implemented in request-response mode," suggesting the architecture was designed for a different communication pattern (likely WebSockets or dedicated streaming endpoints).

## Test Coverage Analysis

### Text Mode Testing
- ✅ Frontend unit tests: Components, forms, utilities
- ✅ Backend unit tests: All conversation phases
- ✅ Integration tests: API endpoints
- ✅ E2E tests: Complete user workflows

### Voice Mode Testing
- ✅ Backend unit tests: Audio pipeline components
- ❌ Frontend unit tests: Skipped with note "moved to separate voice mode"
- ❌ Integration tests: No audio endpoint tests
- ❌ E2E tests: No voice workflow tests

## Actionable Solutions

### Solution 1: Implement Audio Processing in Request-Response Mode (Quick Fix)

Modify the backend to process audio through the existing pipeline:

```python
# In main.py, replace the 501 error with:
elif mime_type == "audio/pcm":
    # Decode base64 audio
    audio_data = base64.b64decode(data)
    
    # Process through audio pipeline
    audio_session = AudioPipelineSession(
        session_id=session_id,
        language=request.headers.get("X-Language", "en-US")
    )
    
    # Convert audio to text
    transcript = await audio_session.process_audio(audio_data)
    
    # Process transcript through conversation flow
    return await process_text_message(session_id, transcript)
```

### Solution 2: Implement WebSocket Audio Streaming (Recommended)

Create a dedicated WebSocket endpoint for real-time audio streaming:

```python
@app.websocket("/ws/audio/{session_id}")
async def websocket_audio_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    audio_session = AudioPipelineSession(session_id)
    
    try:
        while True:
            # Receive audio chunks
            audio_chunk = await websocket.receive_bytes()
            
            # Process audio in real-time
            result = await audio_session.process_chunk(audio_chunk)
            
            if result.transcript:
                # Send transcript and response
                await websocket.send_json({
                    "type": "transcript",
                    "data": result.transcript
                })
                
                # Process through conversation flow
                response = await process_conversation(session_id, result.transcript)
                await websocket.send_json({
                    "type": "response",
                    "data": response
                })
    except WebSocketDisconnect:
        await audio_session.cleanup()
```

## Voice Mode Testing Strategy

### 1. Test Audio Fixtures

Create reusable audio test fixtures:

```python
# tests/fixtures/audio_samples.py
import base64
from pathlib import Path

class AudioSamples:
    """Pre-recorded audio samples for testing"""
    
    @staticmethod
    def get_sample(phrase: str) -> str:
        """Get base64-encoded audio for common test phrases"""
        samples = {
            "hello": "fixtures/audio/hello_16khz_pcm.raw",
            "i_feel_anxious": "fixtures/audio/i_feel_anxious_16khz_pcm.raw",
            "help_me_reframe": "fixtures/audio/help_me_reframe_16khz_pcm.raw",
        }
        
        audio_path = Path(__file__).parent / samples[phrase]
        with open(audio_path, 'rb') as f:
            return base64.b64encode(f.read()).decode()
```

### 2. Mock Audio Services for Testing

```python
# tests/mocks/audio_mocks.py
class MockSpeechToText:
    """Mock STT service with predictable responses"""
    
    def __init__(self):
        self.responses = {
            "hello_audio": "Hello",
            "anxiety_audio": "I feel anxious about social situations",
            "reframe_audio": "Can you help me reframe this thought?",
        }
    
    async def transcribe(self, audio_data: bytes) -> str:
        # Map audio data to known transcripts
        audio_hash = hashlib.md5(audio_data).hexdigest()[:10]
        return self.responses.get(audio_hash, "Unknown audio")
```

### 3. Frontend Voice Mode Tests

```typescript
// frontend/lib/hooks/__tests__/use-natural-conversation.voice.test.tsx
import { renderHook, act } from '@testing-library/react-hooks';
import { useNaturalConversation } from '../use-natural-conversation';

describe('useNaturalConversation - Voice Mode', () => {
  let mockAudioContext: any;
  let mockMediaStream: any;
  
  beforeEach(() => {
    // Mock Web Audio API
    mockAudioContext = {
      sampleRate: 16000,
      createMediaStreamSource: jest.fn(),
      audioWorklet: {
        addModule: jest.fn().mockResolvedValue(undefined),
      },
    };
    
    // Mock getUserMedia
    mockMediaStream = {
      getTracks: jest.fn(() => [{ stop: jest.fn() }]),
    };
    
    global.navigator.mediaDevices = {
      getUserMedia: jest.fn().mockResolvedValue(mockMediaStream),
    };
    
    global.AudioContext = jest.fn(() => mockAudioContext);
  });
  
  it('should initialize audio recording', async () => {
    const { result } = renderHook(() => useNaturalConversation());
    
    await act(async () => {
      await result.current.startVoiceMode();
    });
    
    expect(result.current.isVoiceMode).toBe(true);
    expect(navigator.mediaDevices.getUserMedia).toHaveBeenCalledWith({
      audio: {
        channelCount: 1,
        sampleRate: 16000,
        echoCancellation: true,
        noiseSuppression: true,
      },
    });
  });
  
  it('should send audio data in chunks', async () => {
    const mockApiClient = jest.spyOn(ApiClient.prototype, 'sendMessage');
    const { result } = renderHook(() => useNaturalConversation());
    
    await act(async () => {
      await result.current.startVoiceMode();
    });
    
    // Simulate audio data
    const mockAudioData = new Float32Array(1600); // 100ms of audio at 16kHz
    
    act(() => {
      result.current.processAudioChunk(mockAudioData);
    });
    
    // Wait for debounced send
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 250));
    });
    
    expect(mockApiClient).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        mime_type: 'audio/pcm',
        data: expect.any(String), // base64 encoded
      })
    );
  });
});
```

### 4. Backend Integration Tests

```python
# backend/tests/test_audio_endpoints.py
import pytest
from fastapi.testclient import TestClient
from tests.fixtures.audio_samples import AudioSamples

class TestAudioEndpoints:
    """Test audio processing through API endpoints"""
    
    @pytest.mark.asyncio
    async def test_audio_message_processing(self, client: TestClient, mock_stt):
        """Test sending audio through the standard endpoint"""
        # Arrange
        session_id = "test-session-123"
        audio_sample = AudioSamples.get_sample("i_feel_anxious")
        mock_stt.transcribe.return_value = "I feel anxious about social situations"
        
        # Act
        response = client.post(
            f"/api/send/{session_id}",
            json={
                "mime_type": "audio/pcm",
                "data": audio_sample
            }
        )
        
        # Assert
        assert response.status_code == 200  # Not 501
        assert mock_stt.transcribe.called
        
        # Verify the response contains CBT content
        messages = response.json()["messages"]
        assert any("anxiety" in msg["content"].lower() for msg in messages)
    
    @pytest.mark.asyncio
    async def test_websocket_audio_streaming(self, client: TestClient):
        """Test real-time audio streaming via WebSocket"""
        with client.websocket_connect(f"/ws/audio/test-session") as websocket:
            # Send audio chunk
            audio_chunk = b"\\x00\\x01\\x02\\x03" * 400  # Mock PCM data
            websocket.send_bytes(audio_chunk)
            
            # Receive transcript
            response = websocket.receive_json()
            assert response["type"] == "transcript"
            assert response["data"] == "Hello"
            
            # Receive AI response
            response = websocket.receive_json()
            assert response["type"] == "response"
            assert "CBTAssistant" in response["data"]
```

### 5. E2E Voice Tests

```python
# tests/e2e/tests/test_voice_mode.py
import pytest
from playwright.sync_api import Page
from tests.fixtures.audio_samples import AudioSamples

class TestVoiceMode:
    """End-to-end tests for voice mode functionality"""
    
    @pytest.fixture
    def mock_microphone(self, page: Page):
        """Mock microphone input with pre-recorded audio"""
        page.evaluate("""
            // Override getUserMedia to return mock audio stream
            navigator.mediaDevices.getUserMedia = async (constraints) => {
                const audioContext = new AudioContext();
                const oscillator = audioContext.createOscillator();
                const destination = audioContext.createMediaStreamDestination();
                oscillator.connect(destination);
                oscillator.start();
                return destination.stream;
            };
        """)
    
    def test_voice_conversation_flow(self, page: Page, mock_microphone):
        """Test complete voice conversation workflow"""
        # Navigate to app
        page.goto("http://localhost:3000")
        
        # Switch to voice mode
        voice_button = page.locator("button[aria-label='Switch to voice input']")
        voice_button.click()
        
        # Grant microphone permission (mocked)
        page.wait_for_timeout(1000)
        
        # Verify voice mode is active
        assert page.locator(".voice-indicator").is_visible()
        
        # Inject test audio data
        page.evaluate(f"""
            // Simulate audio input
            window.simulateAudioInput('{AudioSamples.get_sample("i_feel_anxious")}');
        """)
        
        # Wait for transcript to appear
        transcript = page.locator(".transcript-display")
        transcript.wait_for(state="visible", timeout=5000)
        assert "I feel anxious" in transcript.text_content()
        
        # Wait for AI response
        response = page.locator(".message-list .message").last
        response.wait_for(state="visible", timeout=10000)
        assert "thought pattern" in response.text_content().lower()
```

### 6. Performance and Quality Tests

```python
# tests/performance/test_audio_latency.py
import time
import statistics

class TestAudioPerformance:
    """Test audio processing performance metrics"""
    
    def test_audio_latency(self, audio_pipeline):
        """Ensure audio processing meets latency requirements"""
        latencies = []
        
        for _ in range(10):
            audio_chunk = generate_test_audio(duration_ms=100)
            
            start_time = time.time()
            result = audio_pipeline.process_chunk(audio_chunk)
            end_time = time.time()
            
            latency_ms = (end_time - start_time) * 1000
            latencies.append(latency_ms)
        
        avg_latency = statistics.mean(latencies)
        p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
        
        assert avg_latency < 50  # Average under 50ms
        assert p95_latency < 100  # 95% under 100ms
```

## Implementation Roadmap

### Phase 1: Fix Immediate Issue (1-2 days)
1. Implement Solution 1 (process audio in request-response mode)
2. Add basic integration tests
3. Verify frontend-backend communication

### Phase 2: Add Comprehensive Testing (3-4 days)
1. Create audio test fixtures
2. Implement frontend voice mode tests
3. Add backend integration tests
4. Create E2E voice tests

### Phase 3: Optimize Architecture (1 week)
1. Implement WebSocket-based audio streaming
2. Add real-time transcription display
3. Implement audio quality monitoring
4. Add performance tests

### Phase 4: Enhanced Features (Future)
1. Voice activity detection
2. Interruption handling
3. Multi-language support testing
4. Audio feedback and coaching

## Constructive Critique and Recommendations

### Strengths of Current Plan
The testing strategy provides excellent coverage of core functionality with clear implementation examples. The phased approach ensures rapid delivery while maintaining quality. The separation of concerns between unit, integration, and E2E tests follows best practices.

### Critical Gaps and Recommendations

#### 1. Error Handling and Edge Case Testing
**Gap**: The current strategy lacks comprehensive error scenario testing.
**Recommendation**: Add dedicated error handling test suites:

```python
# backend/tests/test_audio_error_handling.py
class TestAudioErrorHandling:
    """Test error scenarios in audio processing"""
    
    async def test_corrupted_audio_data(self, client):
        """Test handling of malformed audio data"""
        response = client.post(
            f"/api/send/test-session",
            json={"mime_type": "audio/pcm", "data": "invalid_base64_!@#"}
        )
        assert response.status_code == 400
        assert "Invalid audio data" in response.json()["detail"]
    
    async def test_audio_timeout_handling(self, client):
        """Test timeout in audio processing"""
        # Send very large audio that triggers timeout
        large_audio = base64.b64encode(b"x" * 10_000_000).decode()
        response = client.post(
            f"/api/send/test-session",
            json={"mime_type": "audio/pcm", "data": large_audio},
            timeout=5.0
        )
        assert response.status_code == 504
```

#### 2. Security and Privacy Testing
**Gap**: No testing for audio data security and privacy compliance.
**Recommendation**: Implement security-focused tests:

```python
# backend/tests/test_audio_security.py
class TestAudioSecurity:
    """Test security aspects of audio processing"""
    
    def test_audio_data_not_logged(self, caplog):
        """Ensure audio data is never logged"""
        audio_pipeline.process_audio(sensitive_audio_data)
        for record in caplog.records:
            assert "audio_data" not in record.message
            assert base64_audio not in record.message
    
    def test_audio_data_not_stored(self, session_manager):
        """Verify audio is processed but not persisted"""
        session = session_manager.get_session("test-id")
        assert "audio_data" not in session.to_dict()
        assert all(msg.get("mime_type") != "audio/pcm" 
                  for msg in session.messages)
```

#### 3. Cross-Browser and Device Compatibility
**Gap**: No testing across different browsers and devices for Web Audio API compatibility.
**Recommendation**: Add browser compatibility matrix:

```typescript
// frontend/lib/hooks/__tests__/use-natural-conversation.browser.test.tsx
describe('Browser Compatibility', () => {
  const browsers = ['chrome', 'firefox', 'safari', 'edge'];
  
  browsers.forEach(browser => {
    it(`should handle audio recording in ${browser}`, async () => {
      const mockUserAgent = getUserAgentFor(browser);
      Object.defineProperty(navigator, 'userAgent', {
        value: mockUserAgent,
        writable: true
      });
      
      const { result } = renderHook(() => useNaturalConversation());
      
      if (browser === 'safari') {
        // Safari requires user interaction for audio
        expect(result.current.requiresUserGesture).toBe(true);
      }
      
      await act(async () => {
        await result.current.startVoiceMode();
      });
      
      expect(result.current.isVoiceMode).toBe(true);
    });
  });
});
```

#### 4. Network Resilience Testing
**Gap**: No testing for poor network conditions or connection recovery.
**Recommendation**: Add network condition simulations:

```python
# tests/e2e/tests/test_voice_network_resilience.py
class TestVoiceNetworkResilience:
    """Test voice mode under various network conditions"""
    
    async def test_voice_mode_network_interruption(self, page, context):
        """Test recovery from network disconnection"""
        # Start voice conversation
        await page.goto("http://localhost:3000")
        await page.click("button[aria-label='Switch to voice input']")
        
        # Simulate network interruption
        await context.set_offline(True)
        await page.wait_for_timeout(2000)
        
        # Verify error state
        error_indicator = page.locator(".connection-error")
        await expect(error_indicator).to_be_visible()
        
        # Restore connection
        await context.set_offline(False)
        
        # Verify automatic recovery
        await expect(error_indicator).not_to_be_visible()
        voice_indicator = page.locator(".voice-indicator")
        await expect(voice_indicator).to_be_visible()
```

#### 5. Audio Quality Validation
**Gap**: Limited testing of audio quality requirements (sample rate, bit depth, noise).
**Recommendation**: Add audio quality validation tests:

```python
# backend/tests/test_audio_quality.py
import numpy as np
from scipy import signal

class TestAudioQuality:
    """Test audio quality metrics"""
    
    def test_audio_sample_rate_validation(self):
        """Ensure audio meets sample rate requirements"""
        audio_data = load_test_audio("test_16khz.pcm")
        detected_rate = detect_sample_rate(audio_data)
        assert detected_rate == 16000, f"Expected 16kHz, got {detected_rate}"
    
    def test_audio_noise_level(self):
        """Verify audio noise is within acceptable range"""
        audio_data = load_test_audio("speech_with_noise.pcm")
        snr = calculate_snr(audio_data)
        assert snr > 15, f"SNR {snr}dB is below minimum 15dB"
    
    def test_audio_clipping_detection(self):
        """Detect and handle clipped audio"""
        clipped_audio = generate_clipped_audio()
        result = audio_pipeline.process_audio(clipped_audio)
        assert result.warnings and "Audio clipping detected" in result.warnings
```

#### 6. Load and Concurrent User Testing
**Gap**: No testing for multiple concurrent voice users.
**Recommendation**: Add load testing scenarios:

```python
# tests/load/test_voice_concurrency.py
import asyncio
import pytest

class TestVoiceConcurrency:
    """Test system under concurrent voice load"""
    
    @pytest.mark.load
    async def test_concurrent_voice_sessions(self, client):
        """Test handling multiple simultaneous voice sessions"""
        async def simulate_voice_user(user_id: int):
            session_id = f"session-{user_id}"
            audio_data = AudioSamples.get_sample("hello")
            
            response = await client.post(
                f"/api/send/{session_id}",
                json={"mime_type": "audio/pcm", "data": audio_data}
            )
            return response.status_code, response.elapsed
        
        # Simulate 50 concurrent users
        tasks = [simulate_voice_user(i) for i in range(50)]
        results = await asyncio.gather(*tasks)
        
        # Verify all requests succeeded
        status_codes = [r[0] for r in results]
        assert all(code == 200 for code in status_codes)
        
        # Verify response times
        response_times = [r[1].total_seconds() for r in results]
        p95_time = sorted(response_times)[int(len(response_times) * 0.95)]
        assert p95_time < 2.0, f"P95 response time {p95_time}s exceeds 2s SLA"
```

#### 7. CI/CD Integration Strategy
**Gap**: No clear integration with CI/CD pipeline for voice tests.
**Recommendation**: Define CI/CD test stages:

```yaml
# .github/workflows/voice-tests.yml
name: Voice Mode Tests
on: [push, pull_request]

jobs:
  voice-unit-tests:
    runs-on: ubuntu-latest
    steps:
      - name: Install audio dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y ffmpeg sox
      
      - name: Run voice unit tests
        run: |
          cd backend && uv run pytest tests/test_audio* -v
          cd ../frontend && pnpm test voice
  
  voice-integration-tests:
    needs: voice-unit-tests
    runs-on: ubuntu-latest
    services:
      audio-mock:
        image: ghcr.io/project/audio-test-server:latest
        ports:
          - 8080:8080
    
    steps:
      - name: Run integration tests
        run: make test-voice-integration
  
  voice-e2e-tests:
    needs: voice-integration-tests
    runs-on: ubuntu-latest
    strategy:
      matrix:
        browser: [chromium, firefox, webkit]
    
    steps:
      - name: Run E2E tests with ${{ matrix.browser }}
        run: |
          npx playwright test --project=${{ matrix.browser }} test_voice_mode.py
```

#### 8. Monitoring and Observability
**Gap**: No production monitoring strategy for voice features.
**Recommendation**: Add monitoring instrumentation:

```python
# backend/src/monitoring/audio_metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
audio_requests = Counter('audio_requests_total', 'Total audio requests', ['status'])
audio_processing_time = Histogram('audio_processing_seconds', 'Audio processing time')
active_voice_sessions = Gauge('active_voice_sessions', 'Current active voice sessions')
audio_quality_score = Histogram('audio_quality_score', 'Audio quality scores', buckets=[0.1, 0.5, 0.7, 0.9])

# Usage in audio pipeline
@audio_processing_time.time()
async def process_audio_with_metrics(audio_data: bytes) -> str:
    active_voice_sessions.inc()
    try:
        result = await audio_pipeline.process(audio_data)
        audio_requests.labels(status='success').inc()
        audio_quality_score.observe(result.quality_score)
        return result.transcript
    except Exception as e:
        audio_requests.labels(status='error').inc()
        raise
    finally:
        active_voice_sessions.dec()
```

### Implementation Priority

1. **Immediate (Before Phase 1)**: Add error handling tests and security validation
2. **Phase 2 Addition**: Include browser compatibility and network resilience tests
3. **Phase 3 Addition**: Implement load testing and monitoring
4. **Ongoing**: Maintain audio quality validation and expand test fixtures

## Conclusion

The voice modality failure is not a bug but an unfinished feature. The backend has all necessary components but lacks the integration layer. By following this roadmap and implementing the proposed testing strategy, you can ensure both text and voice modalities work reliably and maintain quality through comprehensive testing.

The recommended approach is to start with the quick fix (Phase 1) to get voice mode working, then immediately add tests (Phase 2) before optimizing the architecture (Phase 3). This ensures you have working functionality with test coverage before making architectural improvements.

The additional recommendations in this critique address critical gaps in error handling, security, compatibility, and production readiness. Implementing these will ensure the voice feature is not only functional but also robust, secure, and maintainable in production environments.

---

## ✨ 2025-07-18 – Further Gap Analysis vs. Current Code-Base

The earlier plan is still directionally correct, however a quick survey of the current repository surfaces a few **additional mismatches** between the plan and the real implementation that are worth tackling before development starts:

1. Backend entry-point still **hard-blocks audio** (HTTP 501) in `backend/src/main.py` lines 617-628.  This means *all* proposed tests that expect a 200/OK will instantly fail until the guard is removed.  Consider creating a feature flag (`VOICE_MODE_ENABLED`) so the CI can run voice tests without exposing an unfinished endpoint in production builds.

2. The frontend `useNaturalConversation` hook records at **24 kHz** (`new PCMPlayer(24000)`) while the test fixtures and the plan assume **16 kHz** PCM.  Align the sample-rate end-to-end (and reflect it in the STT configuration) to avoid resampling artefacts and false negatives in audio-quality tests.

3. The hook currently **chunks and POSTs audio every 200 ms** through the same REST endpoint that handles text.  In contrast, the plan introduces both request/response and WebSocket flows.  Decide on one path and delete the dead code to keep the surface small; dual implementations double the test matrix and maintenance cost.

4. No code path writes **`turn_complete = true`** messages on the backend, yet the client sends them.  Either:
   • Map `turn_complete` to an internal `conversation_finished` event, or
   • Drop the field from the client until it is needed.  Tests that assert on turn completion will otherwise fail.

5. The STT service is mocked in unit tests but the **audio hash → transcript lookup** in `MockSpeechToText` will always return `"Unknown audio"` because the current implementation hashes raw bytes, while the fixtures feed **base64-encoded** strings.  Hash the *decoded* bytes (or simpler, index by fixture filename) to make the mock deterministic.

6. Front-end does not expose a **`simulateAudioInput`** helper yet; the e2e example in the plan relies on it.  Add a small utility that writes to a `MediaStreamAudioSourceNode` so Playwright can inject audio without touching private React state.

7. **Silence detection**: the client starts a timer but the backend has no logic to short-circuit an STT request on silence.  Either remove the unused timer or propagate a `silence_detected` event so the pipeline can close a turn gracefully.  Add unit tests to lock the behaviour down.

8. **Browser API mocks**: the Jest setup file currently mocks `AudioContext`, but *Safari/WebKit* requires an `OfflineAudioContext` polyfill as well.  Add the polyfill so the new browser-matrix tests do not crash.

9. **CI resources**: the GitHub runners ship without `sox` and `libasound2` which the audio fixtures rely on when resampling.  Extend the workflow’s provisioning step (see example YAML) to include those packages or vendor pre-converted raw PCM fixtures to remove the native dependency entirely.

10. **Metric namespacing**: if you adopt the Prometheus snippet, prefix the counters with `reframe_` (e.g. `reframe_audio_requests_total`) to avoid clashes with other services scraping the same registry in k8s.

### Quick-Win Test to Add Immediately

Before embarking on WebSocket streaming, add the following integration test (pseudo-code) that will start passing as soon as the 501 guard is lifted.  It provides an unmistakable “green light” that the plumbing works end-to-end:

```python
@pytest.mark.asyncio
async def test_audio_roundtrip(client, audio_samples):
    session = SessionManager.create()
    resp = client.post(
        f"/api/send/{session.id}",
        json={
            "mime_type": "audio/pcm",
            "data": audio_samples.get_sample("hello"),
        },
    )
    assert resp.status_code == 200, resp.text
    assert any(m["role"] == "assistant" for m in resp.json()["messages"])
```

Keeping this minimal makes it suitable for the ordinary `pytest -q` job and guarantees the feature never regresses once enabled.

---

These points are intentionally scoped to **gaps that would break the first CI run** or cause noisy false-failures.  Addressing them early will make the comprehensive test-suite described above both stable and trustworthy.
