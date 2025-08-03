'use client'

interface LanguageSelectorProps {
  value: string
  onChange: (language: string) => void
  className?: string
}

const languages = [
  { code: 'en-US', name: 'English' },
  { code: 'es-ES', name: 'Español' },
]

export function LanguageSelector({ value, onChange, className = '' }: LanguageSelectorProps) {
  return (
    <div className={`relative ${className}`}>
      <label htmlFor="language-select" className="text-sm text-[#999999] mb-2 block">
        {value.startsWith('es') ? 'Idioma' : 'Language'}
      </label>
      <select
        id="language-select"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-2 py-1 text-sm bg-[#2a2a2a] border border-[#3a3a3a] rounded-lg text-[#EDEDED] focus:outline-none focus:ring-2 focus:ring-brand-green-500 focus:border-transparent"
      >
        {languages.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.name}
          </option>
        ))}
      </select>
    </div>
  )
}