import { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { PrivacyClient } from './privacy-client'

export const metadata: Metadata = {
  title: 'Privacy Policy - re-frame',
  description: 'Privacy policy for re-frame cognitive reframing assistant'
}

interface PrivacyPageProps {
  params: { locale: string }
}

export default async function PrivacyPage({ params }: PrivacyPageProps) {
  const t = await getTranslations({locale: params.locale, namespace: 'privacy'})

  const translations = {
    title: t('title'),
    lastUpdated: t('lastUpdated'),
    introduction: t('introduction'),
    navigation: {
      back: t('navigation.back')
    },
    sections: {
      dataCollection: {
        title: t('sections.dataCollection.title'),
        description: t('sections.dataCollection.description'),
        points: t.raw('sections.dataCollection.points') as string[]
      },
      technicalData: {
        title: t('sections.technicalData.title'),
        description: t('sections.technicalData.description'),
        points: t.raw('sections.technicalData.points') as string[],
        note: t('sections.technicalData.note')
      },
      dataRetention: {
        title: t('sections.dataRetention.title'),
        description: t('sections.dataRetention.description'),
        points: t.raw('sections.dataRetention.points') as string[]
      },
      yourRights: {
        title: t('sections.yourRights.title'),
        description: t('sections.yourRights.description'),
        points: t.raw('sections.yourRights.points') as string[]
      },
      security: {
        title: t('sections.security.title'),
        description: t('sections.security.description'),
        points: t.raw('sections.security.points') as string[]
      },
      changes: {
        title: t('sections.changes.title'),
        description: t('sections.changes.description')
      },
      contact: {
        title: t('sections.contact.title'),
        description: t('sections.contact.description'),
        email: t('sections.contact.email')
      }
    },
    footer: {
      privacy: t('footer.privacy'),
      support: t('footer.support'),
      about: t('footer.about')
    }
  }

  return <PrivacyClient locale={params.locale} translations={translations} />
}
