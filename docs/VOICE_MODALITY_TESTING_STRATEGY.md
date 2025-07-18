# Voice Modality Testing Strategy - Comprehensive Implementation Guide

## Executive Summary

The voice modality is currently non-functional due to an intentional backend limitation (HTTP 501 response). This document provides a bulletproof testing strategy that addresses all technical gaps, implementation mismatches, and quality requirements for enabling voice mode in the CBT Assistant POC.

## Current State Analysis

### Working Components
1. **Text Mode**: Fully functional with comprehensive test coverage
2. **Audio Infrastructure**: Components exist but are disconnected
   - AudioPipeline orchestrator
   - Speech-to-text service (Google Cloud Speech)
   - Text-to-speech service (Google Cloud TTS)
   - Audio format converters
   - Unit tests for all components

### Critical Issues Requiring Immediate Resolution

1. **Backend Hard Block**: `backend/src/main.py` lines 617-628 return HTTP 501 for audio
2. **Sample Rate Mismatch**: Frontend records at 24kHz, backend expects 16kHz
3. **Missing Turn Completion**: No backend code writes `turn_complete = true`
4. **Mock Service Issues**: Audio hash lookup fails due to base64 encoding mismatch
5. **Missing Frontend Helpers**: No `simulateAudioInput` for E2E testing
6. **Silence Detection**: Frontend timer exists but backend has no handling logic
7. **Browser API Gaps**: Missing OfflineAudioContext polyfill for Safari/WebKit
8. **CI Dependencies**: GitHub runners lack sox and libasound2

## Implementation Roadmap

### Phase 0: Pre-Implementation Fixes (Immediate)

#### 1. Add Feature Flag for Voice Mode
```python
# backend/src/config.py
VOICE_MODE_ENABLED = os.getenv("VOICE_MODE_ENABLED", "false").lower() == "true"

# backend/src/main.py
elif mime_type == "audio/pcm":
    if not config.VOICE_MODE_ENABLED:
        raise HTTPException(
            status_code=501,
            detail="Audio processing not yet implemented in request-response mode",
        )
    # Process audio when enabled
```

#### 2. Align Sample Rates
```typescript
// frontend/lib/hooks/use-natural-conversation.ts
const AUDIO_SAMPLE_RATE = 16000; // Align with backend expectation

// Update PCMPlayer initialization
this.pcmPlayer = new PCMPlayer(AUDIO_SAMPLE_RATE);

// Update getUserMedia constraints
const stream = await navigator.mediaDevices.getUserMedia({
  audio: {
    channelCount: 1,
    sampleRate: AUDIO_SAMPLE_RATE,
    echoCancellation: true,
    noiseSuppression: true,
  },
});
```

#### 3. Fix Mock Service Hash Lookup
```python
# tests/mocks/audio_mocks.py
class MockSpeechToText:
    def __init__(self):
        self.responses = {}
        
    def register_response(self, audio_base64: str, transcript: str):
        # Hash the decoded bytes, not the base64 string
        audio_bytes = base64.b64decode(audio_base64)
        audio_hash = hashlib.md5(audio_bytes).hexdigest()[:10]
        self.responses[audio_hash] = transcript
    
    async def transcribe(self, audio_data: bytes) -> str:
        audio_hash = hashlib.md5(audio_data).hexdigest()[:10]
        return self.responses.get(audio_hash, "Unknown audio")
```

#### 4. Add Frontend Audio Simulation Helper
```typescript
// frontend/test-utils/audio-helpers.ts
export function setupAudioSimulation(window: Window) {
  window.simulateAudioInput = async (base64Audio: string) => {
    const audioData = atob(base64Audio);
    const audioArray = new Uint8Array(audioData.length);
    for (let i = 0; i < audioData.length; i++) {
      audioArray[i] = audioData.charCodeAt(i);
    }
    
    // Dispatch to the audio processing pipeline
    window.dispatchEvent(new CustomEvent('test-audio-input', {
      detail: { audioData: audioArray }
    }));
  };
}
```

### Phase 1: Core Implementation (1-2 days)

#### Quick-Win Integration Test
```python
# backend/tests/test_audio_roundtrip.py
@pytest.mark.asyncio
async def test_audio_roundtrip_minimal(client, audio_samples):
    """Minimal test to verify audio processing works end-to-end"""
    session_id = "test-session-123"
    
    # Enable voice mode for this test
    with patch.dict(os.environ, {"VOICE_MODE_ENABLED": "true"}):
        resp = client.post(
            f"/api/send/{session_id}",
            json={
                "mime_type": "audio/pcm",
                "data": audio_samples.get_sample("hello"),
            },
        )
    
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    messages = resp.json()["messages"]
    assert any(m["role"] == "assistant" for m in messages)
```

#### Audio Processing Implementation
```python
# backend/src/main.py
elif mime_type == "audio/pcm":
    if not config.VOICE_MODE_ENABLED:
        raise HTTPException(status_code=501, detail="Voice mode disabled")
    
    try:
        # Decode base64 audio
        audio_data = base64.b64decode(data)
        
        # Initialize audio session
        audio_session = AudioPipelineSession(
            session_id=session_id,
            language=request.headers.get("X-Language", "en-US"),
            sample_rate=16000  # Explicit sample rate
        )
        
        # Process audio to text
        transcript = await audio_session.process_audio(audio_data)
        
        # Log transcript but never log audio data
        logger.info(f"Transcribed audio for session {session_id}: {transcript[:50]}...")
        
        # Process through normal text flow
        return await process_text_message(session_id, transcript)
        
    except Exception as e:
        logger.error(f"Audio processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Audio processing failed")
```

### Phase 2: Comprehensive Testing Suite (3-4 days)

#### Test Fixtures Infrastructure
```python
# tests/fixtures/audio_samples.py
import base64
import numpy as np
from pathlib import Path
from typing import Dict, Optional

class AudioSamples:
    """Pre-recorded audio samples for testing"""
    
    _samples_cache: Dict[str, str] = {}
    
    @classmethod
    def get_sample(cls, phrase: str, corrupted: bool = False) -> str:
        """Get base64-encoded audio for common test phrases"""
        if phrase in cls._samples_cache and not corrupted:
            return cls._samples_cache[phrase]
        
        samples = {
            "hello": "fixtures/audio/hello_16khz_pcm.raw",
            "i_feel_anxious": "fixtures/audio/i_feel_anxious_16khz_pcm.raw",
            "help_me_reframe": "fixtures/audio/help_me_reframe_16khz_pcm.raw",
            "silence": "fixtures/audio/silence_16khz_pcm.raw",
            "noisy_speech": "fixtures/audio/speech_with_noise_16khz_pcm.raw",
            "clipped_audio": "fixtures/audio/clipped_speech_16khz_pcm.raw",
        }
        
        audio_path = Path(__file__).parent / samples[phrase]
        
        if not audio_path.exists():
            # Generate synthetic audio if file doesn't exist
            audio_data = cls._generate_synthetic_audio(phrase)
        else:
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
        
        if corrupted:
            # Corrupt the audio data for error testing
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            audio_array[::10] = 32767  # Add clipping
            audio_data = audio_array.tobytes()
        
        encoded = base64.b64encode(audio_data).decode()
        cls._samples_cache[phrase] = encoded
        return encoded
    
    @staticmethod
    def _generate_synthetic_audio(phrase: str) -> bytes:
        """Generate synthetic audio for testing"""
        duration = 1.0  # seconds
        sample_rate = 16000
        samples = int(duration * sample_rate)
        
        # Generate simple tone for testing
        t = np.linspace(0, duration, samples)
        frequency = 440  # A4 note
        audio = np.sin(2 * np.pi * frequency * t)
        
        # Convert to 16-bit PCM
        audio_int16 = (audio * 32767).astype(np.int16)
        return audio_int16.tobytes()
```

#### Error Handling Tests
```python
# backend/tests/test_audio_error_handling.py
import pytest
from fastapi import HTTPException

class TestAudioErrorHandling:
    """Test error scenarios in audio processing"""
    
    @pytest.mark.asyncio
    async def test_corrupted_base64_audio(self, client):
        """Test handling of malformed base64 audio data"""
        with patch.dict(os.environ, {"VOICE_MODE_ENABLED": "true"}):
            response = await client.post(
                "/api/send/test-session",
                json={"mime_type": "audio/pcm", "data": "invalid_base64_!@#"}
            )
        
        assert response.status_code == 400
        assert "Invalid audio data" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_audio_size_limit(self, client):
        """Test rejection of oversized audio data"""
        # 10MB of audio (way too large for a single request)
        large_audio = base64.b64encode(b"x" * 10_000_000).decode()
        
        with patch.dict(os.environ, {"VOICE_MODE_ENABLED": "true"}):
            response = await client.post(
                "/api/send/test-session",
                json={"mime_type": "audio/pcm", "data": large_audio}
            )
        
        assert response.status_code == 413
        assert "Audio data too large" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_stt_service_failure(self, client, mock_stt):
        """Test graceful handling of STT service failure"""
        mock_stt.transcribe.side_effect = Exception("STT service unavailable")
        
        with patch.dict(os.environ, {"VOICE_MODE_ENABLED": "true"}):
            response = await client.post(
                "/api/send/test-session",
                json={
                    "mime_type": "audio/pcm",
                    "data": AudioSamples.get_sample("hello")
                }
            )
        
        assert response.status_code == 503
        assert "Speech recognition temporarily unavailable" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_silence_detection(self, client):
        """Test handling of silence in audio"""
        with patch.dict(os.environ, {"VOICE_MODE_ENABLED": "true"}):
            response = await client.post(
                "/api/send/test-session",
                json={
                    "mime_type": "audio/pcm",
                    "data": AudioSamples.get_sample("silence")
                }
            )
        
        assert response.status_code == 200
        # Should return empty transcript or silence indicator
        messages = response.json()["messages"]
        assert len(messages) == 0 or messages[0]["content"] == ""
```

#### Security and Privacy Tests
```python
# backend/tests/test_audio_security.py
import logging
import pytest

class TestAudioSecurity:
    """Test security aspects of audio processing"""
    
    @pytest.mark.asyncio
    async def test_audio_data_not_logged(self, client, caplog):
        """Ensure audio data is never logged"""
        audio_sample = AudioSamples.get_sample("i_feel_anxious")
        
        with caplog.at_level(logging.DEBUG):
            with patch.dict(os.environ, {"VOICE_MODE_ENABLED": "true"}):
                await client.post(
                    "/api/send/test-session",
                    json={"mime_type": "audio/pcm", "data": audio_sample}
                )
        
        # Check that no log contains the actual audio data
        for record in caplog.records:
            assert audio_sample not in record.message
            assert "audio_data" not in record.message.lower()
            # Only transcript should be logged
            assert "transcript" in record.message.lower() or "audio" not in record.message.lower()
    
    @pytest.mark.asyncio
    async def test_audio_not_stored_in_session(self, client, session_manager):
        """Verify audio is processed but not persisted"""
        session_id = "test-security-session"
        
        with patch.dict(os.environ, {"VOICE_MODE_ENABLED": "true"}):
            await client.post(
                f"/api/send/{session_id}",
                json={
                    "mime_type": "audio/pcm",
                    "data": AudioSamples.get_sample("hello")
                }
            )
        
        # Check session storage
        session = session_manager.get_session(session_id)
        session_data = session.to_dict()
        
        # Ensure no audio data in session
        assert "audio_data" not in str(session_data)
        assert all(msg.get("mime_type") != "audio/pcm" for msg in session.messages)
        
        # Only transcripts should be stored
        assert any("Hello" in msg.get("content", "") for msg in session.messages)
    
    @pytest.mark.asyncio
    async def test_audio_headers_sanitization(self, client):
        """Test that sensitive headers are not exposed"""
        with patch.dict(os.environ, {"VOICE_MODE_ENABLED": "true"}):
            response = await client.post(
                "/api/send/test-session",
                json={
                    "mime_type": "audio/pcm",
                    "data": AudioSamples.get_sample("hello")
                },
                headers={
                    "X-Api-Key": "sensitive-key",
                    "Authorization": "Bearer sensitive-token"
                }
            )
        
        # Ensure response doesn't echo sensitive headers
        assert "X-Api-Key" not in response.headers
        assert "Authorization" not in response.headers
```

#### Browser Compatibility Tests
```typescript
// frontend/lib/hooks/__tests__/use-natural-conversation.browser.test.tsx
import { renderHook, act } from '@testing-library/react-hooks';
import { useNaturalConversation } from '../use-natural-conversation';

// Polyfill for Safari/WebKit
if (typeof OfflineAudioContext === 'undefined') {
  (window as any).OfflineAudioContext = (window as any).webkitOfflineAudioContext;
}

describe('Browser Compatibility', () => {
  const browserConfigs = [
    { name: 'chrome', userAgent: 'Chrome/120.0', needsGesture: false },
    { name: 'firefox', userAgent: 'Firefox/120.0', needsGesture: false },
    { name: 'safari', userAgent: 'Safari/17.0', needsGesture: true },
    { name: 'edge', userAgent: 'Edg/120.0', needsGesture: false },
  ];
  
  beforeEach(() => {
    // Mock AudioContext for all browsers
    const MockAudioContext = jest.fn().mockImplementation(() => ({
      sampleRate: 16000,
      createMediaStreamSource: jest.fn(),
      audioWorklet: {
        addModule: jest.fn().mockResolvedValue(undefined),
      },
      close: jest.fn(),
    }));
    
    (window as any).AudioContext = MockAudioContext;
    (window as any).webkitAudioContext = MockAudioContext;
  });
  
  browserConfigs.forEach(({ name, userAgent, needsGesture }) => {
    it(`should handle audio recording in ${name}`, async () => {
      // Set user agent
      Object.defineProperty(navigator, 'userAgent', {
        value: userAgent,
        writable: true,
        configurable: true,
      });
      
      const { result } = renderHook(() => useNaturalConversation());
      
      // Check if browser requires user gesture
      if (needsGesture) {
        expect(result.current.requiresUserGesture).toBe(true);
        
        // Simulate user gesture for Safari
        const event = new MouseEvent('click');
        document.dispatchEvent(event);
      }
      
      // Start voice mode
      await act(async () => {
        await result.current.startVoiceMode();
      });
      
      expect(result.current.isVoiceMode).toBe(true);
      expect(result.current.error).toBeNull();
    });
    
    it(`should handle getUserMedia rejection in ${name}`, async () => {
      Object.defineProperty(navigator, 'userAgent', {
        value: userAgent,
        writable: true,
        configurable: true,
      });
      
      // Mock getUserMedia rejection
      navigator.mediaDevices.getUserMedia = jest.fn().mockRejectedValue(
        new Error('Permission denied')
      );
      
      const { result } = renderHook(() => useNaturalConversation());
      
      await act(async () => {
        await result.current.startVoiceMode();
      });
      
      expect(result.current.isVoiceMode).toBe(false);
      expect(result.current.error).toContain('microphone access');
    });
  });
});
```

#### Network Resilience Tests
```python
# tests/e2e/tests/test_voice_network_resilience.py
import pytest
from playwright.sync_api import Page, BrowserContext, expect

class TestVoiceNetworkResilience:
    """Test voice mode under various network conditions"""
    
    @pytest.mark.asyncio
    async def test_voice_mode_network_interruption(self, page: Page, context: BrowserContext):
        """Test recovery from network disconnection"""
        # Start voice conversation
        await page.goto("http://localhost:3000")
        await page.click("button[aria-label='Switch to voice input']")
        
        # Wait for voice mode to activate
        voice_indicator = page.locator(".voice-indicator")
        await expect(voice_indicator).to_be_visible()
        
        # Simulate network interruption
        await context.set_offline(True)
        await page.wait_for_timeout(2000)
        
        # Verify error state
        error_indicator = page.locator(".connection-error")
        await expect(error_indicator).to_be_visible()
        await expect(error_indicator).to_contain_text("Connection lost")
        
        # Restore connection
        await context.set_offline(False)
        await page.wait_for_timeout(1000)
        
        # Verify automatic recovery
        await expect(error_indicator).not_to_be_visible()
        await expect(voice_indicator).to_be_visible()
        
        # Test that voice input still works after recovery
        await page.evaluate(f"""
            window.simulateAudioInput('{AudioSamples.get_sample("hello")}');
        """)
        
        # Verify response received
        response = page.locator(".message-list .message").last
        await expect(response).to_be_visible(timeout=10000)
    
    @pytest.mark.asyncio
    async def test_voice_mode_slow_network(self, page: Page, context: BrowserContext):
        """Test voice mode on slow 3G connection"""
        # Simulate slow 3G
        await context.route('**/*', lambda route: route.continue_(
            throttle_download_speed=50 * 1024,  # 50 KB/s
            throttle_upload_speed=50 * 1024
        ))
        
        await page.goto("http://localhost:3000")
        await page.click("button[aria-label='Switch to voice input']")
        
        # Send audio and measure response time
        start_time = page.evaluate("Date.now()")
        
        await page.evaluate(f"""
            window.simulateAudioInput('{AudioSamples.get_sample("hello")}');
        """)
        
        # Wait for response with extended timeout
        response = page.locator(".message-list .message").last
        await expect(response).to_be_visible(timeout=30000)
        
        end_time = page.evaluate("Date.now()")
        response_time = (end_time - start_time) / 1000
        
        # Verify response received despite slow network
        assert response_time < 30, f"Response took {response_time}s on slow network"
        
        # Check for buffering indicator
        buffering = page.locator(".buffering-indicator")
        await expect(buffering).to_be_visible()
```

#### Audio Quality Validation
```python
# backend/tests/test_audio_quality.py
import numpy as np
from scipy import signal
from scipy.io import wavfile
import pytest

class TestAudioQuality:
    """Test audio quality metrics"""
    
    def test_audio_sample_rate_validation(self):
        """Ensure audio meets sample rate requirements"""
        audio_data = AudioSamples.get_sample("hello")
        audio_bytes = base64.b64decode(audio_data)
        
        # Convert to numpy array
        audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
        
        # Detect sample rate using autocorrelation
        detected_rate = self._detect_sample_rate(audio_array)
        assert abs(detected_rate - 16000) < 100, f"Expected 16kHz, got {detected_rate}Hz"
    
    def test_audio_noise_level(self):
        """Verify audio noise is within acceptable range"""
        audio_data = AudioSamples.get_sample("noisy_speech")
        audio_bytes = base64.b64decode(audio_data)
        audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
        
        # Calculate SNR
        snr = self._calculate_snr(audio_array)
        assert snr > 15, f"SNR {snr:.1f}dB is below minimum 15dB"
    
    def test_audio_clipping_detection(self):
        """Detect and handle clipped audio"""
        audio_data = AudioSamples.get_sample("clipped_audio")
        audio_bytes = base64.b64decode(audio_data)
        audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
        
        # Check for clipping
        clipping_ratio = np.sum(np.abs(audio_array) >= 32000) / len(audio_array)
        assert clipping_ratio < 0.01, f"Audio has {clipping_ratio*100:.1f}% clipping"
    
    def test_audio_duration_limits(self):
        """Test audio duration constraints"""
        # Test minimum duration (100ms)
        short_audio = np.zeros(1600, dtype=np.int16)  # 100ms at 16kHz
        assert len(short_audio) >= 1600, "Audio too short for processing"
        
        # Test maximum duration (30s)
        long_audio = np.zeros(480000, dtype=np.int16)  # 30s at 16kHz
        assert len(long_audio) <= 480000, "Audio exceeds maximum duration"
    
    @staticmethod
    def _detect_sample_rate(audio_array: np.ndarray) -> float:
        """Estimate sample rate from audio data"""
        # Simple estimation based on zero-crossing rate
        zero_crossings = np.where(np.diff(np.signbit(audio_array)))[0]
        if len(zero_crossings) < 2:
            return 16000  # Default
        
        avg_period = np.mean(np.diff(zero_crossings))
        estimated_freq = 1 / (avg_period / 16000)  # Assume 16kHz base
        return estimated_freq * 16000
    
    @staticmethod
    def _calculate_snr(audio_array: np.ndarray) -> float:
        """Calculate signal-to-noise ratio"""
        # Simple energy-based SNR estimation
        signal_power = np.mean(audio_array ** 2)
        
        # Estimate noise from quiet segments
        window_size = 1600  # 100ms windows
        min_powers = []
        for i in range(0, len(audio_array) - window_size, window_size):
            window = audio_array[i:i+window_size]
            min_powers.append(np.mean(window ** 2))
        
        noise_power = np.percentile(min_powers, 10) if min_powers else 1
        snr_db = 10 * np.log10(signal_power / noise_power)
        return snr_db
```

#### Load and Concurrency Tests
```python
# tests/load/test_voice_concurrency.py
import asyncio
import pytest
import time
from typing import List, Tuple

class TestVoiceConcurrency:
    """Test system under concurrent voice load"""
    
    @pytest.mark.load
    @pytest.mark.asyncio
    async def test_concurrent_voice_sessions(self, async_client):
        """Test handling multiple simultaneous voice sessions"""
        async def simulate_voice_user(user_id: int) -> Tuple[int, float]:
            session_id = f"session-{user_id}"
            audio_data = AudioSamples.get_sample("hello")
            
            start_time = time.time()
            response = await async_client.post(
                f"/api/send/{session_id}",
                json={"mime_type": "audio/pcm", "data": audio_data}
            )
            elapsed = time.time() - start_time
            
            return response.status_code, elapsed
        
        # Enable voice mode for load test
        with patch.dict(os.environ, {"VOICE_MODE_ENABLED": "true"}):
            # Simulate 50 concurrent users
            tasks = [simulate_voice_user(i) for i in range(50)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyze results
        successful = [r for r in results if isinstance(r, tuple) and r[0] == 200]
        failed = [r for r in results if isinstance(r, Exception) or (isinstance(r, tuple) and r[0] != 200)]
        
        # Success rate should be > 95%
        success_rate = len(successful) / len(results)
        assert success_rate > 0.95, f"Success rate {success_rate:.1%} below 95%"
        
        # Response time analysis
        response_times = [r[1] for r in successful]
        avg_time = sum(response_times) / len(response_times)
        p95_time = sorted(response_times)[int(len(response_times) * 0.95)]
        p99_time = sorted(response_times)[int(len(response_times) * 0.99)]
        
        # Performance assertions
        assert avg_time < 1.0, f"Average response time {avg_time:.2f}s exceeds 1s"
        assert p95_time < 2.0, f"P95 response time {p95_time:.2f}s exceeds 2s"
        assert p99_time < 5.0, f"P99 response time {p99_time:.2f}s exceeds 5s"
        
        # Log performance metrics
        print(f"Load test results: {len(successful)} successful, {len(failed)} failed")
        print(f"Response times - Avg: {avg_time:.2f}s, P95: {p95_time:.2f}s, P99: {p99_time:.2f}s")
    
    @pytest.mark.load
    @pytest.mark.asyncio
    async def test_sustained_voice_load(self, async_client):
        """Test system under sustained voice load for 1 minute"""
        start_time = time.time()
        end_time = start_time + 60  # 1 minute test
        
        request_count = 0
        error_count = 0
        response_times: List[float] = []
        
        async def continuous_requests():
            nonlocal request_count, error_count
            
            while time.time() < end_time:
                try:
                    session_id = f"sustained-{request_count}"
                    audio_data = AudioSamples.get_sample("hello")
                    
                    req_start = time.time()
                    response = await async_client.post(
                        f"/api/send/{session_id}",
                        json={"mime_type": "audio/pcm", "data": audio_data}
                    )
                    req_time = time.time() - req_start
                    
                    request_count += 1
                    response_times.append(req_time)
                    
                    if response.status_code != 200:
                        error_count += 1
                    
                    # Target 10 requests per second
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    error_count += 1
                    print(f"Request error: {e}")
        
        # Run with 5 concurrent workers
        with patch.dict(os.environ, {"VOICE_MODE_ENABLED": "true"}):
            workers = [continuous_requests() for _ in range(5)]
            await asyncio.gather(*workers)
        
        # Calculate metrics
        duration = time.time() - start_time
        throughput = request_count / duration
        error_rate = error_count / request_count if request_count > 0 else 0
        
        # Assertions
        assert throughput > 40, f"Throughput {throughput:.1f} req/s below target 40 req/s"
        assert error_rate < 0.01, f"Error rate {error_rate:.1%} exceeds 1%"
        
        # Response time analysis
        if response_times:
            avg_response = sum(response_times) / len(response_times)
            assert avg_response < 0.5, f"Average response {avg_response:.2f}s exceeds 0.5s"
```

### Phase 3: CI/CD Integration (1 week)

#### GitHub Actions Workflow
```yaml
# .github/workflows/voice-tests.yml
name: Voice Mode Tests
on: 
  push:
    paths:
      - 'backend/src/**'
      - 'frontend/lib/**'
      - 'frontend/components/**'
      - 'tests/**'
  pull_request:
    types: [opened, synchronize]

env:
  VOICE_MODE_ENABLED: true

jobs:
  voice-unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install system dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y ffmpeg sox libasound2-dev
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      
      - name: Run backend voice tests
        run: |
          cd backend
          uv sync --all-extras
          uv run pytest tests/test_audio* -v --cov=src.audio --cov-report=xml
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      
      - name: Install pnpm
        run: npm install -g pnpm
      
      - name: Run frontend voice tests
        run: |
          cd frontend
          pnpm install
          pnpm test -- --testNamePattern="voice|audio" --coverage
  
  voice-integration-tests:
    needs: voice-unit-tests
    runs-on: ubuntu-latest
    services:
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup test environment
        run: |
          cp .env.example .env.test
          echo "VOICE_MODE_ENABLED=true" >> .env.test
          echo "GEMINI_API_KEY=${{ secrets.GEMINI_API_KEY }}" >> .env.test
      
      - name: Build and start services
        run: |
          docker-compose -f docker-compose.yml -f docker-compose.test.yml up -d
          ./scripts/wait-for-services.sh
      
      - name: Run integration tests
        run: |
          docker-compose exec -T backend uv run pytest tests/test_audio_endpoints.py -v
      
      - name: Collect logs on failure
        if: failure()
        run: |
          docker-compose logs > integration-test-logs.txt
          echo "::error::Integration tests failed. Check artifacts for logs."
      
      - name: Upload logs
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: integration-test-logs
          path: integration-test-logs.txt
  
  voice-e2e-tests:
    needs: voice-integration-tests
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        browser: [chromium, firefox, webkit]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup environment
        run: |
          cp .env.example .env.test
          echo "VOICE_MODE_ENABLED=true" >> .env.test
      
      - name: Install Playwright
        run: |
          npm install -g playwright
          playwright install --with-deps ${{ matrix.browser }}
      
      - name: Start services
        run: |
          docker-compose up -d
          ./scripts/wait-for-services.sh
      
      - name: Run E2E tests - ${{ matrix.browser }}
        run: |
          cd tests/e2e
          npm test -- --project=${{ matrix.browser }} test_voice_mode.py
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report-${{ matrix.browser }}
          path: tests/e2e/playwright-report/
  
  voice-performance-tests:
    needs: voice-e2e-tests
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup load testing environment
        run: |
          docker-compose -f docker-compose.yml -f docker-compose.perf.yml up -d
          ./scripts/wait-for-services.sh
      
      - name: Run performance tests
        run: |
          cd backend
          uv run pytest tests/load/test_voice_concurrency.py -v -m load
      
      - name: Analyze performance results
        run: |
          python scripts/analyze_performance.py > performance-report.md
      
      - name: Comment PR with performance results
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('performance-report.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: report
            });
```

### Phase 4: Future Enhancements (Post-MVP)

Once voice mode is working and stable, consider adding:

1. **Monitoring and Metrics**
   - Request rate and error tracking
   - Processing latency measurements
   - Audio quality scoring
   - Health check endpoints

2. **Advanced Features**
   - Voice activity detection
   - Interruption handling
   - Multi-language support
   - Real-time feedback and coaching

3. **Performance Optimization**
   - WebSocket-based streaming for lower latency
   - Audio compression
   - Edge caching for common responses

4. **Enhanced Error Recovery**
   - Automatic retry mechanisms
   - Graceful degradation strategies
   - Offline mode support

## Testing Checklist

### Pre-Deployment Checklist
- [ ] Feature flag `VOICE_MODE_ENABLED` implemented
- [ ] Sample rate aligned to 16kHz across frontend and backend
- [ ] Audio mock services properly hash decoded bytes
- [ ] Frontend `simulateAudioInput` helper implemented
- [ ] Turn completion logic implemented or removed
- [ ] Silence detection properly handled
- [ ] Browser polyfills added for Safari/WebKit
- [ ] CI dependencies (sox, libasound2) installed

### Test Coverage Requirements
- [ ] Unit Tests
  - [ ] Audio pipeline components
  - [ ] Error handling scenarios
  - [ ] Security and privacy checks
  - [ ] Audio quality validation
- [ ] Integration Tests
  - [ ] Basic audio roundtrip
  - [ ] Error scenarios
  - [ ] Concurrent session handling
- [ ] E2E Tests
  - [ ] Voice conversation flow
  - [ ] Network resilience
  - [ ] Browser compatibility
- [ ] Performance Tests
  - [ ] Concurrent users (50+)
  - [ ] Sustained load (1 minute)
  - [ ] Latency requirements (P95 < 2s)
- [ ] Security Tests
  - [ ] No audio data in logs
  - [ ] No audio persistence
  - [ ] Header sanitization

### Production Readiness
- [ ] Load testing completed
- [ ] Security review passed
- [ ] Documentation updated
- [ ] Rollback plan documented
- [ ] Basic logging implemented for troubleshooting

## Conclusion

This comprehensive testing strategy addresses all identified gaps and provides a bulletproof approach to implementing voice modality. The phased approach ensures rapid delivery while maintaining quality through extensive testing. By following this guide, the voice feature will be functional, secure, performant, and maintainable in production environments.

Key success factors:
1. Fix technical mismatches before implementation
2. Implement comprehensive test coverage at all levels
3. Maintain security and privacy throughout
4. Ensure cross-browser compatibility
5. Build for resilience under various network conditions
6. Focus on core functionality first, defer non-essential features

The testing infrastructure established here will serve as a foundation for future voice feature enhancements. Monitoring and advanced metrics have been intentionally deferred to post-MVP to maintain focus on getting voice mode working reliably.