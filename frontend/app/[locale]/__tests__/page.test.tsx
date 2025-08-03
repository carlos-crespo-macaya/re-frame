import React from 'react';
import { render, screen } from '@testing-library/react';
import { useRouter, usePathname } from 'next/navigation';
import LocalePage from '../page';

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  usePathname: jest.fn(),
}));

// Mock the InterfaceSelector component to avoid feature flag dependencies
jest.mock('@/components/ui', () => ({
  LanguageSelector: ({ value, onChange }: any) => (
    <select data-testid="language-selector" value={value} onChange={(e) => onChange(e.target.value)}>
      <option value="en-US">English</option>
      <option value="es-ES">Español</option>
    </select>
  ),
  InterfaceSelector: ({ locale }: any) => (
    <div data-testid="interface-selector">
      <div>Interface options here</div>
    </div>
  ),
}));

describe('LocalePage', () => {
  const mockPush = jest.fn();
  const mockUseRouter = useRouter as jest.MockedFunction<typeof useRouter>;
  const mockUsePathname = usePathname as jest.MockedFunction<typeof usePathname>;

  beforeEach(() => {
    mockUseRouter.mockReturnValue({
      push: mockPush,
      back: jest.fn(),
      forward: jest.fn(),
      refresh: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
    });
    mockUsePathname.mockReturnValue('/en');
    mockPush.mockClear();
  });

  it('renders the home page for English locale', () => {
    render(<LocalePage params={{ locale: 'en' }} />);
    
    expect(screen.getAllByText('re-frame')[0]).toBeInTheDocument();
    expect(screen.getByText('Cognitive reframing support')).toBeInTheDocument();
    expect(screen.getByText('Explore a new perspective')).toBeInTheDocument();
  });

  it('renders the home page for Spanish locale', () => {
    render(<LocalePage params={{ locale: 'es' }} />);
    
    expect(screen.getAllByText('re-frame')[0]).toBeInTheDocument();
    expect(screen.getByText('Apoyo de reencuadre cognitivo')).toBeInTheDocument();
    expect(screen.getByText('Explora una nueva perspectiva')).toBeInTheDocument();
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