import { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { LearnCBTClient } from './learn-cbt-client'

export const metadata: Metadata = {
  title: 'Learn about CBT - re-frame',
  description: 'Learn about Cognitive Behavioral Therapy and how it helps with avoidant patterns'
}

interface LearnCBTPageProps {
  params: { locale: string }
}

export default async function LearnCBTPage({ params }: LearnCBTPageProps) {
  const t = await getTranslations({locale: params.locale, namespace: 'learn-cbt'})

  const translations = {
    title: t('title'),
    quickLink: t('quickLink'),
    introduction: t('introduction'),
    navigation: {
      return: t('navigation.return')
    },
    whyHelpsAvpd: {
      title: t('whyHelpsAvpd.title'),
      description: t('whyHelpsAvpd.description'),
      tools: t.raw('whyHelpsAvpd.tools') as string[],
      conclusion: t('whyHelpsAvpd.conclusion')
    },
    howWeUse: {
      title: t('howWeUse.title'),
      description: t('howWeUse.description')
    },
    reminder: {
      prefix: t('reminder.prefix'),
      text: t('reminder.text')
    },
    references: {
      title: t('references.title'),
      tableHeaders: {
        number: t('references.tableHeaders.number'),
        source: t('references.tableHeaders.source'),
        keyPoint: t('references.tableHeaders.keyPoint')
      },
      entries: t.raw('references.entries') as Array<{
        number: string
        source: string
        keyPoint: string
      }>
    },
    note: {
      title: t('note.title'),
      text: t('note.text')
    }
  }

  return <LearnCBTClient locale={params.locale} translations={translations} />
}
