import { render } from '@testing-library/react'
import PrivacyPage from '../page'

// Mock next-intl/server
jest.mock('next-intl/server', () => ({
  getTranslations: jest.fn(async () => {
    const mockT = (key: string) => {
      const translations: Record<string, any> = {
        'title': 'Privacy Policy',
        'lastUpdated': 'Last updated: January 2024',
        'introduction': 'Your privacy is important to us. This policy explains how we handle your information when you use re-frame.',
        'navigation.back': '← Return to re-frame',
        'sections.dataCollection.title': 'Data Collection',
        'sections.dataCollection.description': 'We are committed to protecting your privacy:',
        'sections.technicalData.title': 'Technical Data',
        'sections.technicalData.description': 'We may collect anonymous technical information to improve the service:',
        'sections.technicalData.note': 'This data cannot be used to identify you personally.',
        'sections.cookies.title': 'Cookies',
        'sections.cookies.description': 'We use minimal cookies for essential functionality:',
        'sections.cookies.control': 'You can disable cookies in your browser settings, though some features may not work properly.',
        'sections.thirdPartyServices.title': 'Third-Party Services',
        'sections.thirdPartyServices.description': 'We use secure third-party services for core functionality:',
        'sections.dataRetention.title': 'Data Retention',
        'sections.dataRetention.description': 'We minimize data retention:',
        'sections.yourRights.title': 'Your Rights',
        'sections.yourRights.description': 'You have the right to:',
        'sections.security.title': 'Security',
        'sections.security.description': 'We implement security measures to protect your data:',
        'sections.changes.title': 'Changes to This Policy',
        'sections.changes.description': 'We may update this privacy policy from time to time. We will notify users of any significant changes by posting the new policy on this page. The principle of privacy protection will not be affected by any changes.',
        'sections.contact.title': 'Contact Us',
        'sections.contact.description': 'If you have questions about this privacy policy, please contact us at:',
        'sections.contact.email': 'hello@re-frame.social',
        'footer.privacy': 'Privacy',
        'footer.support': 'Support',
        'footer.about': 'About'
      }
      return translations[key] || key
    }
    
    mockT.raw = (key: string) => {
      const rawTranslations: Record<string, any> = {
        'sections.dataCollection.points': [
          'We do not collect or store personal information',
          'Anonymized conversation data may be saved to help us learn how to improve and make this app more helpful. No personally identifiable information (PII) is ever stored.',
          'No user accounts or registration required'
        ],
        'sections.technicalData.points': [
          'Browser type and version',
          'Device type and screen resolution',
          'General location (country/region only)',
          'Usage statistics (page views, session duration)'
        ],
        'sections.cookies.points': [
          'Language preference',
          'Theme preference (light/dark mode)',
          'Session management (temporary)'
        ],
        'sections.thirdPartyServices.services': [
          {
            name: 'Google Cloud',
            purpose: 'AI processing and hosting',
            dataSharing: 'Temporary conversation data for processing only'
          },
          {
            name: 'Vercel',
            purpose: 'Website hosting and delivery',
            dataSharing: 'Standard web request logs'
          }
        ],
        'sections.dataRetention.points': [
          'Anonymized conversation data may be saved to help us learn how to improve and make this app more helpful. No personally identifiable information (PII) is ever stored.',
          'Technical logs are maintained to help improve the platform\'s technical aspects.',
          'No long-term storage of personal information'
        ],
        'sections.yourRights.points': [
          'Use the service anonymously',
          'Request information about data processing',
          'Report concerns about privacy',
          'Stop using the service at any time'
        ],
        'sections.security.points': [
          'All connections use HTTPS encryption',
          'Regular security updates and monitoring',
          'Minimal data collection reduces risk',
          'No sensitive data storage'
        ]
      }
      return rawTranslations[key] || []
    }
    
    return mockT
  })
}))

describe('PrivacyPage - Content Updates (C2)', () => {
  test('privacy policy should mention anonymized data and technical logs', async () => {
    const PrivacyPageComponent = await PrivacyPage({ params: { locale: 'en' } })
    const { getByText, queryByText, getAllByText } = render(PrivacyPageComponent)
    
    // Should mention anonymized conversation data may be saved (appears in multiple sections)
    const anonymizedDataElements = getAllByText(/Anonymized conversation data may be saved/)
    expect(anonymizedDataElements.length).toBeGreaterThan(0)
    
    // Should mention technical logs are maintained
    expect(getByText(/Technical logs are maintained/)).toBeInTheDocument()
    
    // Should mention principle of privacy protection will not be affected
    expect(getByText(/principle of privacy protection will not be affected/)).toBeInTheDocument()
    
    // Should NOT mention sessions are temporary and deleted after completion
    expect(queryByText(/Sessions are temporary and deleted after completion/)).not.toBeInTheDocument()
  })
})