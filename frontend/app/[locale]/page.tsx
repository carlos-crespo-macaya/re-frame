import { ClientPage } from './client-page'

export async function generateStaticParams() {
  return [
    { locale: 'en' },
    { locale: 'es' },
    { locale: 'fr' },
  ]
}

export default function LocalePage({ params }: { params: { locale: string } }) {
  return <ClientPage params={params} />
}
