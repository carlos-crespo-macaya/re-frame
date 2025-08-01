import { FormClient } from './form-client'

export default function FormPage({ params }: { params: { locale: string } }) {
  return <FormClient locale={params.locale} />
}