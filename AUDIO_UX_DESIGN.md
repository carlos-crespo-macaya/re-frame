# Audio UX/UI Design for re-frame.social

## Design Philosophy

The audio interface should feel like a natural extension of the existing calm, supportive environment. For users with AvPD, the ability to speak instead of type can reduce the cognitive load of formulating written thoughts while maintaining privacy and control.

### Two Modes of Operation

1. **Review Mode** (Default): Speak → Review transcription → Edit if needed → Send
2. **Conversational Mode**: Speak → Auto-send → Immediate AI response → Continuous flow

Users can toggle between modes based on their comfort level and needs.

## UI States and Mockups

### 1. Default State - Text Mode (Current)
```
┌─────────────────────────────────────────────────────────────┐
│  Tell us about the situation                               │
│  A few sentences are enough — share what feels right.      │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ What happened? How did it feel?                     │  │
│  │                                                      │  │
│  │                                                      │  │
│  │                                                      │  │
│  └─────────────────────────────────────────────────────┘  │
│                                               0 / 1000      │
│                                                             │
│     [Generate perspective]     [↻ Clear]                    │
│                                                             │
│         Ctrl + Enter to submit                              │
│                                                             │
│     Private session — we don't store personal data.        │
└─────────────────────────────────────────────────────────────┘
```

### 2. Enhanced Default - With Audio Option
```
┌─────────────────────────────────────────────────────────────┐
│  Tell us about the situation                               │
│  A few sentences are enough — share what feels right.      │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ What happened? How did it feel?                     │  │
│  │                                                      │  │
│  │                                                      │  │
│  │                                          [🎤]       │  │
│  └─────────────────────────────────────────────────────┘  │
│                                               0 / 1000      │
│                                                             │
│     [Generate perspective]     [↻ Clear]                    │
│                                                             │
│         Ctrl + Enter to submit                              │
│                                                             │
│     Private session — we don't store personal data.        │
└─────────────────────────────────────────────────────────────┘
```

### 2a. Mode Selection (After Microphone Permission)
```
┌─────────────────────────────────────────────────────────────┐
│  Tell us about the situation                               │
│  A few sentences are enough — share what feels right.      │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ How would you like to use voice input?              │  │
│  │                                                      │  │
│  │ 📝 Review Mode (Default)                             │  │
│  │ See and edit your words before sending              │  │
│  │                                                      │  │
│  │ 💬 Conversation Mode                                 │  │
│  │ Natural back-and-forth dialogue                     │  │
│  │                                                      │  │
│  │ You can change this anytime: [🎤 ▼]                 │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│     Private session — we don't store personal data.        │
└─────────────────────────────────────────────────────────────┘
```

### 3. Microphone Permission Request
```
┌─────────────────────────────────────────────────────────────┐
│  Tell us about the situation                               │
│  A few sentences are enough — share what feels right.      │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ 🎤 Allow microphone access?                         │  │
│  │                                                      │  │
│  │ Speak your thoughts instead of typing.              │  │
│  │ • Your voice is converted to text                   │  │
│  │ • Audio is not stored                               │  │
│  │ • You can review before sending                     │  │
│  │                                                      │  │
│  │   [Allow microphone]    [Stay with typing]          │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│     Private session — we don't store personal data.        │
└─────────────────────────────────────────────────────────────┘
```

### 4a. Recording State - Review Mode
```
┌─────────────────────────────────────────────────────────────┐
│  Tell us about the situation                               │
│  A few sentences are enough — share what feels right.      │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ 🔴 Listening... (Review Mode)           [🎤 ▼]      │  │
│  │                                                      │  │
│  │ "I've been feeling anxious about..."                │  │
│  │                                                      │  │
│  │ ▁▃▅▇▅▃▁▁▃▅▇▅▃▁▁▃▅▁▁▁                          │  │
│  │                                                      │  │
│  │                            [⏸ Pause] [✓ Done]      │  │
│  └─────────────────────────────────────────────────────┘  │
│                                  45 / 1000 (transcribed)    │
│                                                             │
│     [Generate perspective]     [↻ Clear]                    │
│                                                             │
│     Space to pause • Enter to finish                       │
│                                                             │
│     Private session — we don't store personal data.        │
└─────────────────────────────────────────────────────────────┘
```

### 4b. Recording State - Conversation Mode
```
┌─────────────────────────────────────────────────────────────┐
│  Active Conversation                                        │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ You: I've been feeling anxious about the meeting    │  │
│  │      tomorrow...                                     │  │
│  │                                                      │  │
│  │ AI: I understand meetings can feel overwhelming...   │  │
│  │     [🔊 Speaking...]                                 │  │
│  │                                                      │  │
│  │ ─────────────────────────────────────────────────   │  │
│  │                                                      │  │
│  │ 🔴 Listening...              💬 Conversation Mode    │  │
│  │ ▁▃▅▇▅▃▁▁▃▅▇▅▃▁▁▃▅▁▁▁                          │  │
│  │                                                      │  │
│  │ [⏸ Pause conversation]  [End session]  [🎤 ▼]      │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│     Hold Space to talk • Release to send                   │
│                                                             │
│     Private session — we don't store personal data.        │
└─────────────────────────────────────────────────────────────┘
```

### 5. Review Transcription State (Review Mode Only)
```
┌─────────────────────────────────────────────────────────────┐
│  Tell us about the situation                               │
│  A few sentences are enough — share what feels right.      │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Review your message:                                 │  │
│  │                                                      │  │
│  │ I've been feeling anxious about the meeting         │  │
│  │ tomorrow. Everyone will be looking at me when       │  │
│  │ I present.                                           │  │
│  │                                                      │  │
│  │ [✏️ Edit text]  [🎤 Re-record]  [👍 Looks good]    │  │
│  └─────────────────────────────────────────────────────┘  │
│                                               89 / 1000     │
│                                                             │
│     [Generate perspective]     [↻ Clear]                    │
│                                                             │
│     Private session — we don't store personal data.        │
└─────────────────────────────────────────────────────────────┘
```

### 6. AI Response - Text Only
```
┌─────────────────────────────────────────────────────────────┐
│  Alternative perspective                                    │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ It's natural to feel nervous about presenting.      │  │
│  │ Consider that your colleagues are likely focused    │  │
│  │ on the content rather than judging you...           │  │
│  │                                                      │  │
│  │                                      [🔊 Listen]     │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  Thank you for sharing. When you're ready:                 │
│                                                             │
│     [Continue conversation]     [End session]               │
└─────────────────────────────────────────────────────────────┘
```

### 7. AI Response - Audio Playing
```
┌─────────────────────────────────────────────────────────────┐
│  Alternative perspective                                    │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ 🔊 Speaking...                                       │  │
│  │                                                      │  │
│  │ It's natural to feel nervous about presenting.      │  │
│  │ Consider that your colleagues are likely focused    │  │
│  │ on the content rather than judging you...           │  │
│  │                                                      │  │
│  │ ━━━━━━━━━━━━━━━━━●━━━━━━━  1:23 / 2:45            │  │
│  │                                                      │  │
│  │ [⏸ Pause]  [⏮ -10s]  [⏭ +10s]  [■ Stop]          │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  Thank you for sharing. When you're ready:                 │
│                                                             │
│     [Continue conversation]     [End session]               │
└─────────────────────────────────────────────────────────────┘
```

### 8. Session End State
```
┌─────────────────────────────────────────────────────────────┐
│  Session Complete                                           │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                                                      │  │
│  │           Thank you for sharing today.               │  │
│  │                                                      │  │
│  │     Remember, these perspectives are here to         │  │
│  │     support you, not replace your own judgment.     │  │
│  │                                                      │  │
│  │              [Start new session]                     │  │
│  │                                                      │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│     Private session completed — nothing was stored.         │
└─────────────────────────────────────────────────────────────┘
```

## Component Design Specifications

### Audio Button States
```
Default:        [🎤]     - Gray, subtle
Hover:          [🎤]     - Slightly darker with tooltip "Speak instead"
Active:         [🔴]     - Red dot, pulsing glow
Processing:     [⟳]      - Spinning, transcribing
Disabled:       [🎤]     - Grayed out (no permission)
```

### Mode Indicator Dropdown
```
Review Mode:     [🎤 ▼] → [📝 Review Mode    ✓]
                          [💬 Conversation Mode ]

Conversation:    [🎤 ▼] → [📝 Review Mode     ]
                          [💬 Conversation Mode ✓]
```

### Visual Indicators

#### 1. Audio Level Indicator
```
Quiet:    ▁▁▁▁▁▁▁▁▁▁
Speaking: ▁▃▅▇▅▃▁▁▃▅
Loud:     ▃▅▇█▇▅▃▅▇█
```

#### 2. Recording Timer
```
0:00 ────────────────── 5:00
     ●
```

#### 3. AI Speaking Indicator
```
Idle:     ○ ○ ○
Speaking: ● ○ ○ → ○ ● ○ → ○ ○ ● (animated)
```

## Interaction Patterns

### Voice Input Flow - Review Mode
1. **Tap microphone** → Permission check (first time)
2. **Start speaking** → Real-time transcription appears
3. **Pause/silence** → Auto-detect end or manual stop
4. **Review screen** → Edit, re-record, or accept
5. **Submit** → Same as text submission

### Voice Input Flow - Conversation Mode
1. **Tap microphone** → Permission check (first time)
2. **Hold to speak** or **Toggle recording**
3. **Release/pause** → Auto-sends to AI
4. **AI responds** → Audio + text response
5. **Continue speaking** → Natural back-and-forth
6. **End session** → Thank you message

### Keyboard Shortcuts
**Review Mode:**
- `Space`: Start/stop recording (when focused)
- `Escape`: Cancel recording
- `Enter`: Finish recording and review
- `Ctrl+Enter`: Submit (after review)
- `R`: Re-record (on review screen)

**Conversation Mode:**
- `Space` (hold): Push-to-talk
- `Space` (tap): Toggle recording on/off
- `Escape`: Pause conversation
- `Ctrl+E`: End session
- `M`: Toggle mode (Review/Conversation)

### Mobile Adaptations

**Review Mode:**
```
┌─────────────────────┐
│ Tell us about the   │
│ situation           │
│                     │
│ ┌─────────────────┐ │
│ │                 │ │
│ │  Tap 🎤 to      │ │
│ │  record         │ │
│ │                 │ │
│ └─────────────────┘ │
│ 📝 Review Mode      │
│ [Generate] [Clear]  │
└─────────────────────┘
```

**Conversation Mode:**
```
┌─────────────────────┐
│ Active Conversation │
│                     │
│ You: How can I...   │
│ AI: Let me help...  │
│                     │
│ ┌─────────────────┐ │
│ │  Hold to talk   │ │
│ │      🎤         │ │
│ │  ▁▃▅▇▅▃▁▁▃     │ │
│ └─────────────────┘ │
│ 💬 Conversation     │
│ [⏸] [End session]  │
└─────────────────────┘
```

## Accessibility Features

### Visual Feedback
- **Recording pulse**: Gentle animation shows active recording
- **Waveform display**: Shows audio is being captured
- **Color coding**: Red for recording, green for success
- **Text alternatives**: All audio states have text labels

### Screen Reader Announcements
- "Microphone button available. Press to speak your thought"
- "Recording started. Speak your thought"
- "Recording stopped. Review your message"
- "AI response available. Press to listen"

### Motion Preferences
```css
/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .recording-indicator {
    animation: none;
    opacity: 1;
  }
}
```

## Error States

### No Microphone Access
```
┌─────────────────────────────────────────────────────┐
│ ⚠️ Microphone access blocked                        │
│                                                      │
│ To use voice input:                                 │
│ 1. Click the lock icon in your address bar         │
│ 2. Allow microphone access                          │
│ 3. Refresh the page                                 │
│                                                      │
│ [Continue with typing]                               │
└─────────────────────────────────────────────────────┘
```

### Network Issues During Recording
```
┌─────────────────────────────────────────────────────┐
│ ⚠️ Connection interrupted                            │
│                                                      │
│ Your recording was saved. You can:                  │
│ • [Try again] when connection returns               │
│ • [Type instead] to continue now                    │
└─────────────────────────────────────────────────────┘
```

## Design Principles

1. **Non-intrusive**: Audio features don't dominate the interface
2. **Fallback-first**: Text input remains the primary method
3. **User control**: Choice between review and conversation modes
4. **Privacy-focused**: Visual indicators for all recording states
5. **Calm aesthetics**: Gentle animations, muted colors
6. **Clear feedback**: Users always know what's happening
7. **Flexibility**: Support both controlled (review) and natural (conversation) interactions
8. **No gamification**: Therapeutic focus, not achievement-driven

## Color Palette for Audio Features

```css
--audio-idle: #6B7280;        /* Gray 500 */
--audio-active: #DC2626;      /* Red 600 */
--audio-success: #10B981;     /* Green 500 */
--audio-processing: #3B82F6;  /* Blue 500 */
--audio-error: #F59E0B;       /* Amber 500 */
--audio-waveform: #9CA3AF;    /* Gray 400 */
```

## Implementation Notes

1. **Progressive Enhancement**: Features appear only after permission granted
2. **State Persistence**: Remember user's preference (audio/text mode AND review/conversation mode)
3. **Graceful Degradation**: Falls back to text on any audio failure
4. **Performance**: Lazy load audio components only when needed
5. **Privacy**: Clear indicators when microphone is active
6. **Mode Switching**: Easy toggle between review and conversation modes
7. **Session Management**: Clean session end without gamification

## Mode Comparison

| Feature | Review Mode | Conversation Mode |
|---------|------------|-------------------|
| Default | ✓ Yes | No |
| Transcription shown | Real-time | Real-time |
| Edit before sending | ✓ Yes | No |
| Auto-send on pause | No | ✓ Yes |
| AI response | Text (audio optional) | Audio + text |
| Interaction style | Form-based | Chat-based |
| Best for | Careful expression | Natural dialogue |

## User Journey Improvements

The audio capabilities enhance the existing journey:

1. **Lower barrier to entry**: Speaking can be easier than typing when anxious
2. **More natural expression**: Voice captures emotion and nuance
3. **Flexibility**: Users choose their comfort level (review vs conversation)
4. **Continuous support**: Natural dialogue in conversation mode
5. **Clean closure**: Sessions end with gratitude, not pressure to continue

This design maintains the supportive, non-judgmental environment while offering flexibility in how users interact - whether they prefer the control of reviewing their words or the natural flow of conversation.