'use client'

import { useState } from 'react'
import { ConversationIntegrated } from '@/components/audio/conversation'
import { LanguageSelector } from '@/components/ui'
import Link from 'next/link'

export default function DemoPage() {
  const [selectedLanguage, setSelectedLanguage] = useState('en-US')
  
  return (
    <div className="min-h-screen bg-[#0A0A0A]">
      {/* Header */}
      <header className="border-b border-[#3a3a3a]">
        <div className="container-safe py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/" className="text-brand-green-400 hover:text-brand-green-300">
                ← Back
              </Link>
              <h1 className="text-xl font-heading font-semibold text-[#EDEDED]">
                Conversation Demo
              </h1>
            </div>
            <div className="w-48">
              <LanguageSelector 
                value={selectedLanguage}
                onChange={setSelectedLanguage}
              />
            </div>
          </div>
        </div>
      </header>
      
      {/* Main content */}
      <main className="container-safe py-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8 text-center">
            <h2 className="text-2xl font-heading font-medium text-[#EDEDED] mb-4">
              Real-time Conversation with CBT Assistant
            </h2>
            <p className="text-[#999999]">
              Click the microphone to start speaking. The AI will respond with therapeutic insights.
            </p>
          </div>
          
          <ConversationIntegrated language={selectedLanguage} />
        </div>
      </main>
    </div>
  )
}