# User Stories and Journeys for CBT Assistant

This document outlines all user journeys and stories for the CBT Assistant platform, which will be used as the basis for integration testing.

## Overview

The CBT Assistant provides two primary interaction modes:
1. **Text Mode**: Traditional text-based chat interface
2. **Voice Mode**: Natural conversation using audio input/output

## User Stories

### 1. First-Time User Onboarding

**Story**: As a first-time user, I want to understand what the CBT Assistant does and how it can help me.

**Journey**:
1. User visits the homepage at `/`
2. User sees the main interface with Text/Voice mode toggle
3. User can access:
   - `/about` - Learn about the service
   - `/learn-cbt` - Understand CBT techniques
   - `/privacy` - Review privacy policy
   - `/support` - Get help

**Acceptance Criteria**:
- All navigation links work correctly
- Pages load without errors
- Content is accessible and readable

### 2. Text-Based Cognitive Reframing

**Story**: As a user with social anxiety, I want to type my anxious thoughts and receive helpful reframing suggestions.

**Journey**:
1. User navigates to homepage
2. User ensures "Text Mode" is selected
3. User types an anxious thought in the text area (e.g., "Everyone at the party will judge me")
4. User clicks "Get Reframe" button
5. System establishes SSE connection
6. User sees loading indicator
7. User receives streaming response with:
   - Reframed perspective
   - CBT techniques used
   - Transparency information (frameworks, agents, techniques)
8. User can clear and start again

**Acceptance Criteria**:
- SSE connection establishes successfully
- Response streams in real-time
- Transparency information is displayed
- Clear button resets the interface

### 3. Voice Conversation Mode

**Story**: As a user who prefers speaking, I want to have a natural voice conversation about my anxious thoughts.

**Journey**:
1. User navigates to homepage
2. User selects "Voice Mode"
3. User sees the voice interface with "Start Conversation" button
4. User grants microphone permissions (first time only)
5. User clicks "Start Conversation"
6. System establishes audio SSE connection
7. User speaks their anxious thought
8. System transcribes and displays the text
9. User hears AI assistant's voice response
10. Conversation continues naturally
11. User clicks "Stop Conversation" to end

**Acceptance Criteria**:
- Microphone permissions handled correctly
- Audio recording works (48kHz WAV)
- Real-time transcription displayed
- Audio response plays automatically
- Smooth conversation flow
- Clean session termination

### 4. Language Selection

**Story**: As a non-English speaker, I want to use the assistant in my preferred language.

**Journey**:
1. User sees language selector in header
2. User clicks dropdown and selects language (e.g., Spanish, French)
3. For Text Mode:
   - Interface updates with localized strings
   - User types in selected language
   - Receives response in same language
4. For Voice Mode:
   - User speaks in selected language
   - Receives audio response in same language

**Acceptance Criteria**:
- Language selector persists choice
- Text interface works in selected language
- Voice recognition works for selected language
- Responses match user's language

### 5. Session Management

**Story**: As a returning user, I want to see my past sessions and download summaries.

**Journey**:
1. User clicks "Past Sessions" in header
2. User sees list of previous sessions (if implemented)
3. User can download session summary as PDF
4. PDF contains:
   - Session date/time
   - Key thoughts discussed
   - Reframing suggestions
   - Techniques used

**Acceptance Criteria**:
- Session list loads correctly
- PDF download works
- PDF contains relevant information

### 6. Error Handling

**Story**: As a user, I want clear feedback when something goes wrong.

**Journey Scenarios**:

**6.1 Network Error**:
1. User loses internet connection
2. User tries to submit thought
3. System shows connection error message
4. User can retry when connection restored

**6.2 Audio Permission Denied**:
1. User selects Voice Mode
2. User denies microphone permission
3. System shows clear error message
4. System provides instructions to enable permissions

**6.3 Server Error**:
1. Backend service unavailable
2. User tries any action
3. System shows friendly error message
4. System suggests trying again later

**Acceptance Criteria**:
- All errors show user-friendly messages
- No technical stack traces exposed
- Clear recovery actions provided

### 7. Crisis Detection

**Story**: As a user in crisis, I want to receive appropriate resources instead of reframing.

**Journey**:
1. User types crisis-related content (e.g., self-harm thoughts)
2. System detects crisis keywords
3. System immediately shows:
   - Crisis helpline numbers
   - Emergency resources
   - Clear message about seeking professional help
4. System does not attempt CBT reframing

**Acceptance Criteria**:
- Crisis detection triggers immediately
- Resources displayed prominently
- No attempt at therapeutic intervention
- Clear professional help guidance

### 8. Theme Switching

**Story**: As a user, I want to use the app in my preferred visual theme.

**Journey**:
1. User clicks theme toggle button
2. Theme switches between light/dark mode
3. Theme preference persists across sessions
4. All UI elements adapt to selected theme

**Acceptance Criteria**:
- Theme toggle works instantly
- No flash of wrong theme on reload
- All components properly themed
- Preference saved in localStorage

## Technical Integration Points

### Frontend → Backend API Calls

1. **SSE Connection** (Text Mode):
   - GET `/api/events/{session_id}?language={lang}`
   - Establishes event stream
   - Receives: connected event, text responses, completion events

2. **Send Text Message**:
   - POST `/api/send/{session_id}`
   - Body: `{ mime_type: "text/plain", content: "user message" }`
   - Response: Message acknowledgment

3. **SSE Connection** (Voice Mode):
   - GET `/api/events/{session_id}?is_audio=true&language={lang}`
   - Establishes audio event stream
   - Receives: connected event, audio/pcm data, transcriptions

4. **Send Audio Message**:
   - POST `/api/send/{session_id}`
   - Body: `{ mime_type: "audio/wav", content: "base64_audio" }`
   - Response: Message acknowledgment

5. **Health Check**:
   - GET `/health`
   - Verifies backend availability

6. **Download PDF**:
   - GET `/api/pdf/{session_id}`
   - Returns: PDF file download

7. **Session Info**:
   - GET `/api/session/{session_id}`
   - Returns: Session metadata

## Testing Priority

### P0 - Critical Paths
1. Text-based reframing (core functionality)
2. Basic error handling
3. SSE connection management

### P1 - Important Features  
1. Voice conversation mode
2. Language switching
3. Crisis detection

### P2 - Nice to Have
1. PDF download
2. Theme switching
3. Session history

## Notes for Test Implementation

- All tests should run against Docker Compose environment
- Use stable test data and mock responses where appropriate
- Test both successful paths and error scenarios
- Verify frontend-backend integration, not unit functionality
- Focus on user-visible behavior and outcomes