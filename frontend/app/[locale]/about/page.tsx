import { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { AboutClient } from './about-client'

export const metadata: Metadata = {
  title: 'About re-frame',
  description: 'Learn about re-frame cognitive reframing assistant'
}

interface AboutPageProps {
  params: { locale: string }
}

export default async function AboutPage({ params }: AboutPageProps) {
  const t = await getTranslations({locale: params.locale, namespace: 'about'})

  const translations = {
    title: t('title'),
    navigation: {
      back: t('navigation.back')
    },
    mission: {
      label: t('mission.label'),
      description: t('mission.description')
    },
    details: {
      whatIs: {
        label: t('details.whatIs.label'),
        description: t('details.whatIs.description')
      },
      whatIsnt: {
        label: t('details.whatIsnt.label'),
        description: t('details.whatIsnt.description')
      },
      creator: {
        title: t('details.creator.title'),
        content: t.raw('details.creator.content') as string
      },
      thankYou: {
        title: t('details.thankYou.title'),
        content: t('details.thankYou.content')
      }
    },
    contact: {
      question: t('contact.question'),
      email: t('contact.email')
    },
    footer: {
      privacy: t('footer.privacy'),
      support: t('footer.support'),
      about: t('footer.about')
    }
  }

  return <AboutClient locale={params.locale} translations={translations} />
}
