'use client'

import { useRouter } from 'next/navigation'

export function ClientPage({ params }: { params: { locale: string } }) {
  const router = useRouter()

  const handleStartSession = () => {
    router.push(`/${params.locale}/chat`)
  }

  const handleLearnMore = () => {
    router.push(`/${params.locale}/about`)
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-[#161616] text-[#EDEDED]">
      <div className="text-center max-w-2xl">
        <h1 className="text-4xl font-bold mb-4 text-[#EDEDED]">
          CBT Reframing Assistant
        </h1>
        <p className="text-lg text-[#B0B0B0] mb-8">
          Welcome to your cognitive behavioral therapy assistant powered by Google's ADK
        </p>
        <div className="space-x-4">
          <button 
            onClick={handleStartSession}
            className="bg-primary-500 text-white hover:bg-primary-600 px-6 py-3 rounded-lg transition-colors"
          >
            Start Session
          </button>
          <button 
            onClick={handleLearnMore}
            className="border border-[#404040] hover:bg-[#333333] text-[#EDEDED] px-6 py-3 rounded-lg transition-colors"
          >
            Learn More
          </button>
        </div>
      </div>
    </main>
  )
}
