import { ChatClient } from './chat-client'

export default function ChatPage({ params }: { params: { locale: string } }) {
  return <ChatClient locale={params.locale} />
}