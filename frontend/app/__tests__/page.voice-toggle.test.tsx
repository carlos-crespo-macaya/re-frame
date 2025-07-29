import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import Home from '../[locale]/page';
import { useTextModeEnabled, useVoiceModeEnabled } from '@/lib/feature-flags';

// Mock ReactMarkdown
jest.mock('react-markdown', () => ({
  __esModule: true,
  default: ({ children }: any) => <div>{children}</div>,
}));

// Mock next-intl
jest.mock('next-intl', () => ({
  useTranslations: () => (key: string) => key,
}));

// Mock dependencies
jest.mock('@/lib/feature-flags', () => ({
  useTextModeEnabled: jest.fn(),
  useVoiceModeEnabled: jest.fn(),
  useEnabledLanguages: () => ({
    value: ['en', 'es'],
    loading: false,
    error: null,
    refetch: jest.fn(),
  }),
  FeatureFlagProvider: ({ children }: { children: React.ReactNode }) => children,
}));

jest.mock('@/lib/streaming/use-sse-client', () => ({
  useSSEClient: () => ({
    isConnected: false,
    messages: [],
    connect: jest.fn(),
    disconnect: jest.fn(),
    sendText: jest.fn(),
    error: null,
  }),
}));

jest.mock('@/components/audio/NaturalConversation', () => ({
  NaturalConversation: () => <div data-testid="natural-conversation">Natural Conversation Component</div>,
}));

jest.mock('@/components/forms/ThoughtInputForm', () => ({
  __esModule: true,
  default: ({ onSubmit }: any) => (
    <div data-testid="thought-input-form">
      <button onClick={() => onSubmit('test thought')}>Submit</button>
    </div>
  ),
}));

jest.mock('@/components/ui', () => ({
  FrameworkBadge: () => <div>Framework Badge</div>,
  LanguageSelector: ({ onChange }: any) => (
    <select onChange={(e) => onChange(e.target.value)}>
      <option value="en-US">English</option>
      <option value="es-ES">Spanish</option>
    </select>
  ),
}));

describe('Home Page - Voice Mode Toggle', () => {
  const mockUseTextModeEnabled = useTextModeEnabled as jest.MockedFunction<typeof useTextModeEnabled>;
  const mockUseVoiceModeEnabled = useVoiceModeEnabled as jest.MockedFunction<typeof useVoiceModeEnabled>;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('shows mode toggle when both text and voice modes are enabled', () => {
    mockUseTextModeEnabled.mockReturnValue({
      value: true,
      loading: false,
      error: null,
      refetch: jest.fn(),
    });
    mockUseVoiceModeEnabled.mockReturnValue({
      value: true,
      loading: false,
      error: null,
      refetch: jest.fn(),
    });

    const { getByText } = render(<Home />);
    
    expect(getByText('Switch to Voice')).toBeInTheDocument();
  });

  it('hides mode toggle when only text mode is enabled', () => {
    mockUseTextModeEnabled.mockReturnValue({
      value: true,
      loading: false,
      error: null,
      refetch: jest.fn(),
    });
    mockUseVoiceModeEnabled.mockReturnValue({
      value: false,
      loading: false,
      error: null,
      refetch: jest.fn(),
    });

    const { queryByText } = render(<Home />);
    
    expect(queryByText('Switch to Voice')).not.toBeInTheDocument();
    expect(queryByText('Switch to Text')).not.toBeInTheDocument();
  });

  it('hides mode toggle when only voice mode is enabled', () => {
    mockUseTextModeEnabled.mockReturnValue({
      value: false,
      loading: false,
      error: null,
      refetch: jest.fn(),
    });
    mockUseVoiceModeEnabled.mockReturnValue({
      value: true,
      loading: false,
      error: null,
      refetch: jest.fn(),
    });

    const { queryByText } = render(<Home />);
    
    expect(queryByText('Switch to Voice')).not.toBeInTheDocument();
    expect(queryByText('Switch to Text')).not.toBeInTheDocument();
  });

  it('switches between text and voice modes', () => {
    mockUseTextModeEnabled.mockReturnValue({
      value: true,
      loading: false,
      error: null,
      refetch: jest.fn(),
    });
    mockUseVoiceModeEnabled.mockReturnValue({
      value: true,
      loading: false,
      error: null,
      refetch: jest.fn(),
    });

    const { getByText, getByTestId, queryByTestId } = render(<Home />);
    
    // Initially in text mode
    expect(getByTestId('thought-input-form')).toBeInTheDocument();
    expect(queryByTestId('natural-conversation')).not.toBeInTheDocument();
    
    // Switch to voice mode
    fireEvent.click(getByText('Switch to Voice'));
    
    expect(queryByTestId('thought-input-form')).not.toBeInTheDocument();
    expect(getByTestId('natural-conversation')).toBeInTheDocument();
    expect(getByText('Switch to Text')).toBeInTheDocument();
    
    // Switch back to text mode
    fireEvent.click(getByText('Switch to Text'));
    
    expect(getByTestId('thought-input-form')).toBeInTheDocument();
    expect(queryByTestId('natural-conversation')).not.toBeInTheDocument();
    expect(getByText('Switch to Voice')).toBeInTheDocument();
  });

  it('shows fallback message when no modes are enabled', () => {
    mockUseTextModeEnabled.mockReturnValue({
      value: false,
      loading: false,
      error: null,
      refetch: jest.fn(),
    });
    mockUseVoiceModeEnabled.mockReturnValue({
      value: false,
      loading: false,
      error: null,
      refetch: jest.fn(),
    });

    const { getByText } = render(<Home />);
    
    expect(getByText('No communication modes are currently available.')).toBeInTheDocument();
    expect(getByText('Please check back later.')).toBeInTheDocument();
  });

  it('hides mode toggle during loading', () => {
    mockUseTextModeEnabled.mockReturnValue({
      value: true,
      loading: true,
      error: null,
      refetch: jest.fn(),
    });
    mockUseVoiceModeEnabled.mockReturnValue({
      value: true,
      loading: true,
      error: null,
      refetch: jest.fn(),
    });

    const { queryByText } = render(<Home />);
    
    expect(queryByText('Switch to Voice')).not.toBeInTheDocument();
    expect(queryByText('Switch to Text')).not.toBeInTheDocument();
  });

  it('defaults to voice mode when only voice is enabled', async () => {
    mockUseTextModeEnabled.mockReturnValue({
      value: false,
      loading: false,
      error: null,
      refetch: jest.fn(),
    });
    mockUseVoiceModeEnabled.mockReturnValue({
      value: true,
      loading: false,
      error: null,
      refetch: jest.fn(),
    });

    const { getByTestId, queryByTestId } = render(<Home />);
    
    // Should automatically show voice mode
    await waitFor(() => {
      expect(getByTestId('natural-conversation')).toBeInTheDocument();
      expect(queryByTestId('thought-input-form')).not.toBeInTheDocument();
    });
  });

  it('defaults to text mode when only text is enabled', async () => {
    mockUseTextModeEnabled.mockReturnValue({
      value: true,
      loading: false,
      error: null,
      refetch: jest.fn(),
    });
    mockUseVoiceModeEnabled.mockReturnValue({
      value: false,
      loading: false,
      error: null,
      refetch: jest.fn(),
    });

    const { getByTestId, queryByTestId } = render(<Home />);
    
    // Should show text mode
    await waitFor(() => {
      expect(getByTestId('thought-input-form')).toBeInTheDocument();
      expect(queryByTestId('natural-conversation')).not.toBeInTheDocument();
    });
  });
});