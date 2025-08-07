import { render } from '@testing-library/react'
import SupportPage from '../page'

// Mock next-intl/server
jest.mock('next-intl/server', () => ({
  getTranslations: jest.fn(async () => {
    const mockT = (key: string) => {
      const translations: Record<string, any> = {
        'title': 'Support & Help',
        'subtitle': 'Get help with re-frame or find mental health resources',
        'navigation.back': '← Return to re-frame',
        'sections.technicalSupport.title': 'Tech Support & Feedback',
        'sections.technicalSupport.description': 'Having trouble with the app? We\'re here to help.',
        'sections.technicalSupport.contact': 'Contact us at:',
        'sections.technicalSupport.email': 'hello@re-frame.social',
        'sections.technicalSupport.responseTime': 'We typically respond as soon as possible.',
        'sections.mentalHealthResources.title': 'Need to talk right now?',
        'sections.mentalHealthResources.description': 'If you\'re in crisis or need immediate support:',
        'sections.aboutAvpd.title': 'About Avoidant Personality Disorder',
        'sections.aboutAvpd.description': 'Helpful objective literature',
        'sections.privacyAndSafety.title': 'Privacy & Safety',
        'sections.privacyAndSafety.description': 'Your privacy and safety are our top priorities:',
        'reminder.title': 'Important Reminder',
        'reminder.text': 're-frame is a self-help tool and not a replacement for professional mental health care. If you\'re experiencing thoughts of self-harm or suicide, please contact emergency services or a crisis helpline immediately.',
        'footer.privacy': 'Privacy',
        'footer.support': 'Support',
        'footer.about': 'About'
      }
      return translations[key] || key
    }
    
    mockT.raw = (key: string) => {
      const rawTranslations: Record<string, any> = {
        'sections.mentalHealthResources.resources': [
          {
            name: 'Find a Helpline',
            description: 'Crisis numbers and text lines in your country',
            url: 'https://findahelpline.com'
          },
          {
            name: 'Befrienders Worldwide',
            description: 'Email or call volunteers in 90+ countries',
            url: 'https://befrienders.org'
          },
          {
            name: '7 Cups',
            description: 'Free, anonymous 24/7 chat with trained listeners',
            url: 'https://7cups.com'
          }
        ],
        'sections.aboutAvpd.resources': [
          {
            name: 'Cleveland Clinic',
            description: 'Plain-language overview, diagnostic criteria, and treatment options',
            url: 'https://my.clevelandclinic.org/health/diseases/9761-avoidant-personality-disorder'
          },
          {
            name: 'StatPearls / NCBI Bookshelf',
            description: 'Clinical depth with DSM criteria and therapeutic evidence',
            url: 'https://www.ncbi.nlm.nih.gov/books/NBK559325/'
          },
          {
            name: 'Psych Central',
            description: 'Accessible guide to symptoms, impact, and therapy expectations',
            url: 'https://psychcentral.com/disorders/avoidant-personality-disorder'
          }
        ],
        'sections.privacyAndSafety.points': [
          'We don\'t store your conversation data',
          'Sessions are not recorded or saved',
          'All communication is encrypted',
          'No personal information is required'
        ]
      }
      return rawTranslations[key] || []
    }
    
    return mockT
  })
}))

describe('SupportPage - Crisis Resources', () => {
  test('crisis section should display three international resources', async () => {
    const SupportPageComponent = await SupportPage({ params: { locale: 'en' } })
    const { getByText, getAllByRole } = render(SupportPageComponent)
    
    expect(getByText('Need to talk right now?')).toBeInTheDocument()
    expect(getByText('Find a Helpline')).toBeInTheDocument()
    expect(getByText('Befrienders Worldwide')).toBeInTheDocument()
    expect(getByText('7 Cups')).toBeInTheDocument()
    
    const links = getAllByRole('link')
    expect(links.find(l => l.getAttribute('href') === 'https://findahelpline.com')).toBeDefined()
  })
})

describe('SupportPage - AvPD Resources', () => {
  test('AvPD section should display helpful objective literature', async () => {
    const SupportPageComponent = await SupportPage({ params: { locale: 'en' } })
    const { getByText } = render(SupportPageComponent)
    
    expect(getByText('About Avoidant Personality Disorder')).toBeInTheDocument()
    expect(getByText('Helpful objective literature')).toBeInTheDocument()
    expect(getByText('Cleveland Clinic')).toBeInTheDocument()
  })
})

describe('SupportPage - Tech Support Section', () => {
  test('tech support section should show updated title and response time', async () => {
    const SupportPageComponent = await SupportPage({ params: { locale: 'en' } })
    const { getByText, queryByText } = render(SupportPageComponent)
    
    expect(getByText('Tech Support & Feedback')).toBeInTheDocument()
    expect(getByText(/as soon as possible/)).toBeInTheDocument()
    expect(queryByText(/24-48 hours/)).not.toBeInTheDocument()
  })
})