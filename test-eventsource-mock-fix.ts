// Fixed EventSource mock that properly simulates real EventSource behavior
window.__sendSSEMessage = (index: number, eventType: string, data: string) => {
  const source = window.__mockEventSources?.[index];
  if (source && source.readyState === MockEventSource.OPEN) {
    // The real EventSource API extracts just the data portion from SSE format
    // So we should send only the JSON data, not the full SSE format
    const event = new MessageEvent('message', {
      data: data  // Just the JSON string, not SSE format
    });
    source.dispatchEvent(event);
  }
};

// Example usage for connection event - must include 'type' field
window.__sendSSEMessage(0, 'connected', JSON.stringify({ 
  type: 'connected',  // The app checks for this field
  session_id: 'test-session' 
}));

// Example for transcription - must match expected format
window.__sendSSEMessage(0, 'transcription', JSON.stringify({
  mime_type: 'text/plain',
  message_type: 'transcription',
  data: 'User transcription text here'
}));

// Example for audio data
window.__sendSSEMessage(0, 'audio', JSON.stringify({
  mime_type: 'audio/pcm',
  data: 'base64_encoded_audio_here'
}));