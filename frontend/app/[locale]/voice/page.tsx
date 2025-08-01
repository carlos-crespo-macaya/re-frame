import { VoiceClient } from './voice-client'

export default function VoicePage({ params }: { params: { locale: string } }) {
  return <VoiceClient locale={params.locale} />
}