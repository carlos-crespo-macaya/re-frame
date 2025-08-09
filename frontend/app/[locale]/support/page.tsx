import { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { SupportClient } from './support-client'

export const metadata: Metadata = {
  title: 'Support & Help - re-frame',
  description: 'Get help with re-frame or find mental health resources'
}

interface SupportPageProps {
  params: { locale: string }
}

export default async function SupportPage({ params }: SupportPageProps) {
  const t = await getTranslations({locale: params.locale, namespace: 'support'})

  const translations = {
    title: t('title'),
    subtitle: t('subtitle'),
    navigation: {
      back: t('navigation.back')
    },
    sections: {
      technicalSupport: {
        title: t('sections.technicalSupport.title'),
        description: t('sections.technicalSupport.description'),
        contact: t('sections.technicalSupport.contact'),
        email: t('sections.technicalSupport.email'),
        responseTime: t('sections.technicalSupport.responseTime')
      },
      mentalHealthResources: {
        title: t('sections.mentalHealthResources.title'),
        description: t('sections.mentalHealthResources.description'),
        resources: t.raw('sections.mentalHealthResources.resources') as Array<{ name: string; description?: string; url?: string }>
      },
      aboutAvpd: {
        title: t('sections.aboutAvpd.title'),
        description: t('sections.aboutAvpd.description'),
        resources: t.raw('sections.aboutAvpd.resources') as Array<{ name: string; description?: string; url?: string }>
      },
      privacyAndSafety: {
        title: t('sections.privacyAndSafety.title'),
        description: t('sections.privacyAndSafety.description'),
        points: t.raw('sections.privacyAndSafety.points') as string[]
      }
    },
    reminder: {
      title: t('reminder.title'),
      text: t('reminder.text')
    },
    footer: {
      privacy: t('footer.privacy'),
      support: t('footer.support'),
      about: t('footer.about')
    }
  }

  return <SupportClient locale={params.locale} translations={translations} />
}
