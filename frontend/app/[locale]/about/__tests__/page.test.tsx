import { render } from '@testing-library/react'
import AboutPage from '../page'

// Mock next-intl/server
jest.mock('next-intl/server', () => ({
  getTranslations: jest.fn(async () => {
    const translations: Record<string, any> = {
      'title': 'ℹ️ About re-frame',
      'navigation.back': '← Return to re-frame',
      'mission.label': 'Mission',
      'mission.description': 'give people who struggle with avoidant patterns a gentle way to challenge harsh thoughts.',
      'details.whatIs.label': 'What it is:',
      'details.whatIs.description': 'a therapeutic framework-informed cognitive restructuring tool that spots thinking traps (catastrophising, mind-reading, etc.) and offers kinder perspectives.',
      'details.whatIsnt.label': 'What it isn\'t:',
      'details.whatIsnt.description': 'full psychotherapy, medical advice, or a crisis service.',
      'details.creator.title': 'About me',
      'details.creator.content': 'I\'m <a href=\'https://carlos-crespo.com/\' target=\'_blank\' rel=\'noopener noreferrer\' class=\'text-brand-green-400 hover:text-brand-green-300 underline\'>Carlos</a>, this page aims to create, collect and share resources that could help people like me on their journey.',
      'details.whyOpen.label': 'Why open source:',
      'details.whyOpen.description': 'transparency builds trust; anyone can inspect or improve the code.',
      'details.thankYou.title': 'Thank You',
      'details.thankYou.content': 'Thank you for trying re-frame. We hope it helps you in some way on your journey.',
      'contact.question': 'Questions? Reach me at ',
      'contact.email': 'hello@re-frame.social',
      'footer.privacy': 'Privacy',
      'footer.support': 'Support',
      'footer.about': 'About'
    }
    
    const mockT = (key: string) => {
      return translations[key] || key
    }
    
    // Add raw method for HTML content
    mockT.raw = (key: string) => {
      return translations[key] || key
    }
    
    return mockT
  })
}))

describe('AboutPage - Content Updates (C1)', () => {
  test('about page should have thank you section and updated creator info', async () => {
    const AboutPageComponent = await AboutPage({ params: { locale: 'en' } })
    const { getByText, queryByText } = render(AboutPageComponent)
    
    // Should have "Thank You" section
    expect(getByText('Thank You')).toBeInTheDocument()
    
    // Should have "About me" section with Carlos link
    expect(getByText('About me')).toBeInTheDocument()
    
    // Should NOT have "The Why" section (roadmap)
    expect(queryByText('Roadmap:')).not.toBeInTheDocument()
    
    // Should NOT have specific text about "without shame, ads, or data mining"
    expect(queryByText(/without shame, ads, or data mining/)).not.toBeInTheDocument()
  })
})