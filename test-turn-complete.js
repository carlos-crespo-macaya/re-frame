// Test script to debug turn_complete events
const axios = require('axios');
const { EventSource } = require('eventsource');

const baseUrl = 'http://localhost:8000';
const sessionId = 'test-' + Date.now();

console.log('Starting test with session:', sessionId);

// Step 1: Connect to SSE
const eventSource = new EventSource(`${baseUrl}/api/events/${sessionId}?language=en-US`);

let messageCount = 0;
let turnCompleteReceived = false;

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`[SSE] Received:`, data);
  
  if (data.type === 'content') {
    messageCount++;
  } else if (data.type === 'turn_complete') {
    turnCompleteReceived = true;
    console.log('✅ TURN COMPLETE RECEIVED!');
  }
};

eventSource.onerror = (error) => {
  console.error('SSE Error:', error);
};

// Wait for connection
setTimeout(async () => {
  console.log('\nSending test message...');
  
  try {
    // Step 2: Send a message
    const response = await axios.post(`${baseUrl}/api/send/${sessionId}`, {
      mime_type: 'text/plain',
      data: 'Hello, I am feeling anxious'
    });
    
    console.log('Message sent successfully:', response.data);
    
    // Wait for turn_complete
    setTimeout(() => {
      console.log('\n--- Results ---');
      console.log('Messages received:', messageCount);
      console.log('Turn complete received:', turnCompleteReceived);
      
      if (!turnCompleteReceived) {
        console.log('❌ TURN COMPLETE NOT RECEIVED!');
      }
      
      eventSource.close();
      process.exit(turnCompleteReceived ? 0 : 1);
    }, 5000);
    
  } catch (error) {
    console.error('Error sending message:', error.response?.data || error.message);
    eventSource.close();
    process.exit(1);
  }
}, 2000);