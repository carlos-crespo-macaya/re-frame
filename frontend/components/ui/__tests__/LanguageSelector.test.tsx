import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import { LanguageSelector } from '../LanguageSelector';

// Mock the feature flags hook
jest.mock('@/lib/feature-flags', () => ({
  ...jest.requireActual('@/lib/feature-flags'),
  useEnabledLanguages: jest.fn(),
  FeatureFlagProvider: ({ children }: { children: React.ReactNode }) => children,
}));

import { useEnabledLanguages } from '@/lib/feature-flags';

describe('LanguageSelector', () => {
  const mockOnChange = jest.fn();
  const mockUseEnabledLanguages = useEnabledLanguages as jest.MockedFunction<typeof useEnabledLanguages>;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders with enabled languages from feature flags', () => {
    mockUseEnabledLanguages.mockReturnValue({
      value: ['en', 'es', 'fr'],
      loading: false,
      error: null,
      refetch: jest.fn(),
    });

    const { getByLabelText, getAllByRole } = render(
      <LanguageSelector
        value="en-US"
        onChange={mockOnChange}
      />
    );

    const select = getByLabelText('Select Language');
    expect(select).toBeInTheDocument();

    const options = getAllByRole('option');
    expect(options).toHaveLength(3);
    expect(options[0]).toHaveTextContent('English');
    expect(options[1]).toHaveTextContent('Español');
    expect(options[2]).toHaveTextContent('Français');
  });

  it('defaults to English when no languages are configured', () => {
    mockUseEnabledLanguages.mockReturnValue({
      value: [],
      loading: false,
      error: null,
      refetch: jest.fn(),
    });

    const { getAllByRole } = render(
      <LanguageSelector
        value="en-US"
        onChange={mockOnChange}
      />
    );

    const options = getAllByRole('option');
    expect(options).toHaveLength(1);
    expect(options[0]).toHaveTextContent('English');
  });

  it('handles language change', () => {
    mockUseEnabledLanguages.mockReturnValue({
      value: ['en', 'es'],
      loading: false,
      error: null,
      refetch: jest.fn(),
    });

    const { getByLabelText } = render(
      <LanguageSelector
        value="en-US"
        onChange={mockOnChange}
      />
    );

    const select = getByLabelText('Select Language');
    fireEvent.change(select, { target: { value: 'es-ES' } });

    expect(mockOnChange).toHaveBeenCalledWith('es-ES');
  });

  it('correctly maps language codes to full language objects', () => {
    mockUseEnabledLanguages.mockReturnValue({
      value: ['de', 'it', 'nl'],
      loading: false,
      error: null,
      refetch: jest.fn(),
    });

    const { getAllByRole } = render(
      <LanguageSelector
        value="de-DE"
        onChange={mockOnChange}
      />
    );

    const options = getAllByRole('option');
    expect(options).toHaveLength(3);
    expect(options[0]).toHaveTextContent('Deutsch');
    expect(options[1]).toHaveTextContent('Italiano');
    expect(options[2]).toHaveTextContent('Nederlands');
  });

  it('handles loading state gracefully', () => {
    mockUseEnabledLanguages.mockReturnValue({
      value: null as any,
      loading: true,
      error: null,
      refetch: jest.fn(),
    });

    const { getAllByRole } = render(
      <LanguageSelector
        value="en-US"
        onChange={mockOnChange}
      />
    );

    // Should default to English during loading
    const options = getAllByRole('option');
    expect(options).toHaveLength(1);
    expect(options[0]).toHaveTextContent('English');
  });

  it('applies custom className', () => {
    mockUseEnabledLanguages.mockReturnValue({
      value: ['en'],
      loading: false,
      error: null,
      refetch: jest.fn(),
    });

    const { container } = render(
      <LanguageSelector
        value="en-US"
        onChange={mockOnChange}
        className="custom-class"
      />
    );

    const wrapper = container.firstChild;
    expect(wrapper).toHaveClass('relative', 'custom-class');
  });

  it('supports all expected languages when enabled', () => {
    mockUseEnabledLanguages.mockReturnValue({
      value: ['en', 'es', 'pt', 'fr', 'de', 'it', 'nl', 'pl', 'uk', 'cs'],
      loading: false,
      error: null,
      refetch: jest.fn(),
    });

    const { getAllByRole } = render(
      <LanguageSelector
        value="en-US"
        onChange={mockOnChange}
      />
    );

    const options = getAllByRole('option');
    expect(options).toHaveLength(10);
    
    const expectedLanguages = [
      'English',
      'Español',
      'Português',
      'Français',
      'Deutsch',
      'Italiano',
      'Nederlands',
      'Polski',
      'Українська',
      'Čeština'
    ];

    options.forEach((option, index) => {
      expect(option).toHaveTextContent(expectedLanguages[index]);
    });
  });
});