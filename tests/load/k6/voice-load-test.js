import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';
import encoding from 'k6/encoding';

// Custom metrics
const errorRate = new Rate('errors');
const audioResponseTime = new Trend('audio_response_time');
const textResponseTime = new Trend('text_response_time');

// Test configuration
export const options = {
  // Configurable via environment variables
  vus: __ENV.K6_VUS || 50,
  duration: __ENV.K6_DURATION || '5m',
  
  // Ramp-up pattern
  stages: [
    { duration: '30s', target: 10 },   // Warm up
    { duration: '1m', target: 50 },    // Ramp to 50 users
    { duration: '3m', target: 50 },    // Stay at 50
    { duration: '30s', target: 0 },    // Ramp down
  ],
  
  // Thresholds for pass/fail
  thresholds: {
    http_req_duration: ['p(95)<2000', 'p(99)<5000'], // 95% < 2s, 99% < 5s
    errors: ['rate<0.01'],                             // Error rate < 1%
    audio_response_time: ['p(95)<3000'],              // Audio 95% < 3s
    text_response_time: ['p(95)<1000'],               // Text 95% < 1s
  },
};

// Base URL from environment
const BASE_URL = __ENV.API_BASE_URL || 'http://localhost:8000';

// Generate synthetic audio data (16-bit PCM at 16kHz)
function generateAudioData(durationSeconds = 1) {
  const sampleRate = 16000;
  const samples = sampleRate * durationSeconds;
  const buffer = new ArrayBuffer(samples * 2); // 16-bit = 2 bytes
  const view = new Int16Array(buffer);
  
  // Generate a simple sine wave
  const frequency = 440; // A4 note
  for (let i = 0; i < samples; i++) {
    const t = i / sampleRate;
    const value = Math.sin(2 * Math.PI * frequency * t) * 16000;
    view[i] = Math.floor(value);
  }
  
  // Convert to base64
  return encoding.b64encode(buffer);
}

// Test phrases for variety
const testPhrases = [
  "I feel anxious about the upcoming presentation",
  "I'm worried that everyone will judge me",
  "Help me reframe my negative thoughts",
  "I keep thinking about worst case scenarios",
  "I need help with my social anxiety",
];

export default function () {
  const sessionId = `k6-session-${__VU}-${Date.now()}`;
  
  // Randomly choose between audio and text mode
  const useAudio = Math.random() < 0.7; // 70% audio, 30% text
  
  let response;
  let startTime = Date.now();
  
  if (useAudio) {
    // Audio request
    const audioData = generateAudioData(1 + Math.random() * 2); // 1-3 seconds
    
    response = http.post(
      `${BASE_URL}/api/send/${sessionId}`,
      JSON.stringify({
        mime_type: "audio/pcm",
        data: audioData,
      }),
      {
        headers: {
          'Content-Type': 'application/json',
          'X-Language': 'en-US',
        },
        timeout: '30s',
      }
    );
    
    audioResponseTime.add(Date.now() - startTime);
  } else {
    // Text request
    const phrase = testPhrases[Math.floor(Math.random() * testPhrases.length)];
    
    response = http.post(
      `${BASE_URL}/api/send/${sessionId}`,
      JSON.stringify({
        mime_type: "text/plain",
        data: phrase,
      }),
      {
        headers: {
          'Content-Type': 'application/json',
          'X-Language': 'en-US',
        },
        timeout: '30s',
      }
    );
    
    textResponseTime.add(Date.now() - startTime);
  }
  
  // Check response
  const success = check(response, {
    'status is 200': (r) => r.status === 200,
    'response has messages': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.messages && body.messages.length > 0;
      } catch (e) {
        return false;
      }
    },
    'no error in response': (r) => {
      try {
        const body = JSON.parse(r.body);
        return !body.error && !body.detail;
      } catch (e) {
        return false;
      }
    },
  });
  
  errorRate.add(!success);
  
  // Log failures for debugging
  if (!success) {
    console.error(`Request failed: ${response.status} - ${response.body}`);
  }
  
  // Simulate user think time between requests
  sleep(Math.random() * 5 + 2); // 2-7 seconds
  
  // Occasional session end (10% chance)
  if (Math.random() < 0.1) {
    const endResponse = http.post(
      `${BASE_URL}/api/end-session/${sessionId}`,
      null,
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
    
    check(endResponse, {
      'session end successful': (r) => r.status === 200,
    });
  }
}

// Optional: Setup function to verify service is ready
export function setup() {
  const healthCheck = http.get(`${BASE_URL}/health`);
  if (healthCheck.status !== 200) {
    throw new Error(`Service not healthy: ${healthCheck.status}`);
  }
  
  // Check if voice mode is enabled
  const testSession = `k6-setup-test-${Date.now()}`;
  const voiceCheck = http.post(
    `${BASE_URL}/api/send/${testSession}`,
    JSON.stringify({
      mime_type: "audio/pcm",
      data: generateAudioData(0.1), // Short test audio
    }),
    {
      headers: { 'Content-Type': 'application/json' },
    }
  );
  
  if (voiceCheck.status === 501) {
    console.warn('Voice mode not enabled - tests will use text mode only');
  }
  
  return { voiceEnabled: voiceCheck.status === 200 };
}

// Optional: Teardown function to export metrics
export function teardown(data) {
  console.log('Test completed');
  console.log(`Voice mode was ${data.voiceEnabled ? 'enabled' : 'disabled'}`);
}