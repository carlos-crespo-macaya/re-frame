import React from 'react';
import { render, screen } from '@testing-library/react';
import LocalePage from '../page';

// Mock the InterfaceSelector component to avoid feature flag dependencies
type LangProps = { value: string; onChange: (v: string) => void };
type InterfaceProps = { locale: string };

jest.mock('@/components/ui', () => ({
  LanguageSelector: ({ value, onChange }: LangProps) => (
    <select aria-label="Language" data-testid="language-selector" value={value} onChange={(e) => onChange(e.target.value)}>
      <option value="en-US">English</option>
      <option value="es-ES">Español</option>
    </select>
  ),
  InterfaceSelector: ({ locale }: InterfaceProps) => (
    <div data-testid="interface-selector" data-locale={locale}>
      <div>Interface options here</div>
    </div>
  ),
}));

describe('LocalePage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the home page for English locale', () => {
    render(<LocalePage params={{ locale: 'en' }} />);

    expect(screen.getAllByText('re-frame')[0]).toBeInTheDocument();
    expect(screen.getByText('Explore a new perspective')).toBeInTheDocument();
    expect(screen.getAllByText(/evidence-based therapeutic techniques/i)[0]).toBeInTheDocument();
  });

  it('renders the home page for Spanish locale', () => {
    render(<LocalePage params={{ locale: 'es' }} />);

    expect(screen.getAllByText('re-frame')[0]).toBeInTheDocument();
    expect(screen.getByText('Explora una nueva perspectiva')).toBeInTheDocument();
    expect(screen.getAllByText(/técnicas terapéuticas basadas en evidencia/i)[0]).toBeInTheDocument();
  });

  it('interface cards should not display selector header text', () => {
    const { queryByText } = render(<LocalePage params={{ locale: 'en' }} />);

    expect(queryByText('Choose Your Interface')).not.toBeInTheDocument();
    expect(queryByText('Select how you\'d like to interact')).not.toBeInTheDocument();
  });

  it('interface cards should not display selector header text in Spanish', () => {
    const { queryByText } = render(<LocalePage params={{ locale: 'es' }} />);

    expect(queryByText('Elige Tu Interfaz')).not.toBeInTheDocument();
    expect(queryByText('Selecciona cómo te gustaría interactuar')).not.toBeInTheDocument();
  });

  it('renders navigation links correctly', () => {
    render(<LocalePage params={{ locale: 'en' }} />);

    expect(screen.getByRole('link', { name: 'Privacy' })).toHaveAttribute('href', '/en/privacy');
    expect(screen.getByRole('link', { name: 'Support' })).toHaveAttribute('href', '/en/support');
    expect(screen.getByRole('link', { name: 'About' })).toHaveAttribute('href', '/en/about');
  });
});
