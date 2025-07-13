export interface ConversationMessage {
  id: string
  role: 'user' | 'ai'
  content: string
  timestamp: number
  audioUrl?: string
}

export interface ConversationState {
  messages: ConversationMessage[]
  isRecording: boolean
  isAISpeaking: boolean
  currentTranscription: string
}

export interface ConversationViewProps {
  messages?: ConversationMessage[]
  isRecording?: boolean
  isAISpeaking?: boolean
  currentTranscription?: string
  onStartRecording?: () => void
  onStopRecording?: () => void
  onEndSession?: () => void
}

export interface SessionSummary {
  duration: number // in seconds
  messageCount: number
  insights?: string[]
}

export interface SessionEndViewProps {
  onNewSession?: () => void
  sessionSummary?: SessionSummary
}

export interface MessageListProps {
  messages: ConversationMessage[]
}

export interface MessageBubbleProps {
  message: ConversationMessage
  isLast?: boolean
}