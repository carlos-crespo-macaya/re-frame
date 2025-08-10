import { GlassCard } from '@/components/layout/GlassCard'

interface ImportantReminderProps {
  locale: string
  variant?: 'default' | 'crisis'
  className?: string
}

export function ImportantReminder({ locale, variant = 'default', className = '' }: ImportantReminderProps) {
  const translations = {
    en: {
      title: 'Important Reminder',
      default: "re-frame is a self-help companion that uses ideas from Cognitive Behavioral Therapy (CBT). It isn't psychotherapy, medical advice, or a crisis service.",
      crisis: "re-frame is a self-help tool and not a replacement for professional mental health care. If you're experiencing thoughts of self-harm or suicide, please contact emergency services or a crisis line immediately."
    },
    es: {
      title: 'Recordatorio Importante',
      default: "re-frame es un acompañante de autoayuda que utiliza ideas de la Terapia Cognitivo-Conductual (TCC). No es psicoterapia, consejo médico ni un servicio de crisis.",
      crisis: "re-frame es una herramienta de autoayuda y no un reemplazo de la atención profesional de salud mental. Si estás experimentando pensamientos de autolesión o suicidio, por favor contacta servicios de emergencia o una línea de crisis inmediatamente."
    }
  }

  const t = translations[locale as keyof typeof translations] || translations.en

  return (
    <GlassCard 
      className={`
        relative overflow-hidden
        ${variant === 'crisis' 
          ? 'bg-red-500/10 border-red-500/30' 
          : 'bg-[#aefcf5]/5 border-[#aefcf5]/20'
        }
        ${className}
      `}
    >
      {/* Accent bar on the left */}
      <div 
        className={`
          absolute left-0 top-0 bottom-0 w-1
          ${variant === 'crisis' ? 'bg-red-500' : 'bg-[#aefcf5]'}
        `} 
      />
      
      <div className="pl-6">
        <p className={`
          text-base font-heading font-semibold mb-2
          ${variant === 'crisis' ? 'text-red-400' : 'text-[#aefcf5]'}
        `}>
          {t.title}
        </p>
        <p className="text-white/70 leading-relaxed">
          {variant === 'crisis' ? t.crisis : t.default}
        </p>
      </div>
    </GlassCard>
  )
}