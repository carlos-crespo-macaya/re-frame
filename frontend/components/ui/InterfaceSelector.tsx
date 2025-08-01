'use client'

import { useRouter } from 'next/navigation'
import { Button } from './Button'

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
    interfaces: {
      chat: {
        title: 'Text Chat',
        description: 'Type and chat with re-frame in real-time'
      },
      voice: {
        title: 'Voice Conversation',
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
    interfaces: {
      chat: {
        title: 'Chat de Texto',
        description: 'Escribe y chatea con re-frame en tiempo real'
      },
      voice: {
        title: 'Conversación por Voz',
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
      icon: '🎤',
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

  const handleInterfaceSelect = (interfaceKey: string) => {
    router.push(`/${locale}/${interfaceKey}`)
  }

  return (
    <div className={`w-full max-w-4xl mx-auto ${className}`}>
      <div className="text-center mb-8">
        <h2 className="text-2xl font-heading font-medium text-[#EDEDED] mb-3">
          {t.title}
        </h2>
        <p className="text-[#999999]">
          {t.subtitle}
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {interfaces.map((interface_) => (
          <div
            key={interface_.key}
            className={`relative group cursor-pointer transition-all duration-300 ${
              currentInterface === interface_.key 
                ? 'ring-2 ring-brand-green-500' 
                : 'hover:scale-105'
            }`}
            onClick={() => handleInterfaceSelect(interface_.key)}
          >
            <div className={`absolute inset-0 bg-gradient-to-br ${interface_.gradient} rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300`} />
            <div className="relative bg-[#2a2a2a] rounded-2xl shadow-lg border border-[#3a3a3a] p-6 h-full">
              <div className="text-center">
                <div className="text-4xl mb-4">
                  {interface_.icon}
                </div>
                <h3 className="text-lg font-heading font-medium text-[#EDEDED] mb-3">
                  {interface_.title}
                </h3>
                <p className="text-sm text-[#999999] mb-6 leading-relaxed">
                  {interface_.description}
                </p>
                <Button
                  variant={currentInterface === interface_.key ? 'primary' : 'secondary'}
                  size="medium"
                  className="w-full group-hover:bg-brand-green-600 group-hover:text-white transition-colors"
                >
                  {currentInterface === interface_.key ? 'Current' : 'Select'}
                </Button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}