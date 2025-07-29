'use client'

import { useMemo } from 'react'
import { useTranslations, useLocale } from 'next-intl'
import { useRouter, usePathname } from 'next/navigation'
import { useEnabledLanguages } from '@/lib/feature-flags'

interface LanguageSelectorProps {
  value?: string
  onChange?: (language: string) => void
  className?: string
}

const allLanguages = [
  { code: 'en', fullCode: 'en-US', name: 'English' },
  { code: 'es', fullCode: 'es-ES', name: 'Español' },
] as const

export function LanguageSelector({ value, onChange, className = '' }: LanguageSelectorProps) {
  const t = useTranslations()
  const locale = useLocale()
  const router = useRouter()
  const pathname = usePathname()
  
  // Get enabled languages from feature flags
  const { value: enabledLanguages } = useEnabledLanguages()
  
  const languages = useMemo(() => {
    if (!enabledLanguages || !Array.isArray(enabledLanguages) || enabledLanguages.length === 0) {
      // Default to English and Spanish
      return allLanguages
    }
    
    // Map language codes to full language objects
    return allLanguages.filter(lang => {
      return enabledLanguages.includes(lang.code)
    })
  }, [enabledLanguages])

  const handleLanguageChange = (newLanguage: string) => {
    // Handle external onChange if provided (for backward compatibility)
    if (onChange) {
      // Convert locale code to full language code for backward compatibility
      const fullCode = allLanguages.find(lang => lang.code === newLanguage)?.fullCode || newLanguage
      onChange(fullCode)
    }
    
    // Navigate to the new locale
    const newPathname = pathname.replace(`/${locale}`, `/${newLanguage}`)
    router.push(newPathname)
  }

  const currentValue = value ? 
    // Convert full language code back to locale code
    allLanguages.find(lang => lang.fullCode === value)?.code || locale :
    locale

  return (
    <div className={`relative ${className}`}>
      <label htmlFor="language-select" className="text-sm text-[#999999] mb-2 block">
        {t('language_selector.label')}
      </label>
      <select
        id="language-select"
        value={currentValue}
        onChange={(e) => handleLanguageChange(e.target.value)}
        className="w-full px-4 py-2 bg-[#2a2a2a] border border-[#3a3a3a] rounded-lg text-[#EDEDED] focus:outline-none focus:ring-2 focus:ring-brand-green-500 focus:border-transparent"
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