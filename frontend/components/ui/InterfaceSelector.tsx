'use client'

import { useRouter } from 'next/navigation'
import { Button } from './Button'
import { useEffect, useState } from 'react'
import { fetchUiFeatureFlags, UIFeatureFlags } from '@/lib/api/featureFlags'

interface InterfaceSelectorProps {
  locale: string
  currentInterface?: 'chat' | 'voice' | 'form'
  className?: string
}

interface InterfaceOption {
  key: 'chat' | 'voice' | 'form'
  title: string
  description: string
  icon: string
  gradient: string
}

const translations = {
  en: {
    title: 'Choose Your Interface',
    subtitle: 'Select how you\'d like to interact with re-frame',
    buttonStart: 'Start',
    buttonCurrent: 'Current',
    interfaces: {
      chat: {
        title: 'Text Chat',
        description: 'Type and chat with re-frame in real-time'
      },
      voice: {
        title: 'Voice Chat',
        description: 'Speak naturally and get audio responses'
      },
      form: {
        title: 'Structured Form',
        description: 'Use detailed forms with audio support'
      }
    }
  },
  es: {
    title: 'Elige Tu Interfaz',
    subtitle: 'Selecciona cómo te gustaría interactuar con re-frame',
    buttonStart: 'Iniciar',
    buttonCurrent: 'Actual',
    interfaces: {
      chat: {
        title: 'Chat de Texto',
        description: 'Escribe y chatea con re-frame en tiempo real'
      },
      voice: {
        title: 'Chat de Voz',
        description: 'Habla naturalmente y recibe respuestas de audio'
      },
      form: {
        title: 'Formulario Estructurado',
        description: 'Usa formularios detallados con soporte de audio'
      }
    }
  }
}

export function InterfaceSelector({ locale, currentInterface, className = '' }: InterfaceSelectorProps) {
  const router = useRouter()
  const t = translations[locale as keyof typeof translations] || translations.en
  const [flags, setFlags] = useState<UIFeatureFlags | null>(null)

  useEffect(() => {
    let mounted = true
    fetchUiFeatureFlags()
      .then((f) => { if (mounted) setFlags(f) })
      .catch(() => {
        // When flags fail to load, keep them null so we show the loading spinner
        if (mounted) setFlags(null)
      })
    return () => { mounted = false }
  }, [])

  const interfaces: InterfaceOption[] = [
    {
      key: 'chat',
      title: t.interfaces.chat.title,
      description: t.interfaces.chat.description,
      icon: '💬',
      gradient: 'from-blue-500/20 to-cyan-500/20'
    },
    {
      key: 'voice',
      title: t.interfaces.voice.title,
      description: t.interfaces.voice.description,
      icon: '🗣️',
      gradient: 'from-purple-500/20 to-pink-500/20'
    },
    {
      key: 'form',
      title: t.interfaces.form.title,
      description: t.interfaces.form.description,
      icon: '📝',
      gradient: 'from-green-500/20 to-teal-500/20'
    }
  ]

  // Apply feature flag filtering: non-activated interfaces should not appear at all.
  const filtered: InterfaceOption[] = (interfaces || []).filter((it: InterfaceOption) => {
    if (!flags) return false // do not render any card until flags are loaded
    if (it.key === 'chat') return flags.chat_mode_enabled
    if (it.key === 'voice') return flags.voice_mode_enabled
    if (it.REDACTED
    return false
  })

  const handleInterfaceSelect = (interfaceKey: string) => {
    router.push(`/${locale}/${interfaceKey}`)
  }

  // Loading gate to prevent flash of wrong UI
  if (flags === null) {
    return (
      <div className={`w-full max-w-4xl mx-auto ${className}`}>
        <div className="flex items-center justify-center py-10">
          <div className="h-8 w-8 rounded-full border-2 border-[#3a3a3a] border-t-white animate-spin" aria-label="Loading" />
        </div>
      </div>
    )
  }

  return (
    <div className={`w-full max-w-4xl mx-auto ${className}`}>

      {/* Use a centered responsive grid. The container uses place-items-center to ensure
          each card is centered within its grid cell, and auto-fit with minmax gives
          natural centering of 1–2 cards without leftover gutter bias. */}
      <div
        className="grid gap-6 justify-center place-items-center"
        style={{
          gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
        }}
      >
        {filtered.map((interface_) => (
          <div
            key={interface_.key}
            className={`relative group cursor-pointer transition-all duration-300 transform ${
              currentInterface === interface_.key
                ? 'ring-2 ring-[#9BF7EB]'
                : 'hover:translate-y-[-2px]'
            }`}
            onClick={() => handleInterfaceSelect(interface_.key)}
          >
            {/* Hover glow effect */}
            <div className={`absolute inset-0 bg-gradient-to-br ${interface_.gradient} rounded-3xl blur-2xl opacity-0 group-hover:opacity-60 transition-opacity duration-300`} />

            {/* Glass-blur card with refined styling */}
            <div className="relative backdrop-blur-md bg-[#08141c]/55 rounded-3xl shadow-lg ring-1 ring-white/5 p-8 h-full group-hover:backdrop-blur-lg transition-all duration-300">
              <div className="text-center">
                <div className="text-4xl mb-5">
                  {interface_.icon}
                </div>
                <h3 className="text-xl font-heading font-semibold text-white/90 mb-3">
                  {interface_.title}
                </h3>
                <p className="text-[15px] text-[#cdd5d7]/70 mb-6 leading-relaxed max-w-[48ch] mx-auto">
                  {interface_.description}
                </p>

                {/* CTA button with nested darker treatment */}
                <div className="bg-[#0b1014]/60 rounded-xl p-1 group-hover:ring-1 group-hover:ring-[#9BF7EB]/30 transition-all">
                  <Button
                    variant={currentInterface === interface_.key ? 'primary' : 'secondary'}
                    size="small"
                    className="w-full transition-all"
                  >
                    {currentInterface === interface_.key ? t.buttonCurrent : t.buttonStart}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
