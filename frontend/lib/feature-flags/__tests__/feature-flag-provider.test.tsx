import React from 'react';
import { render, waitFor, act } from '@testing-library/react';
import { FeatureFlagProvider, useFeatureFlags } from '../feature-flag-provider';

// Mock fetch
global.fetch = jest.fn();

describe('FeatureFlagProvider', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    sessionStorage.clear();
  });

  it('fetches flags from backend on mount', async () => {
    const mockFlags = {
      textModeEnabled: true,
      voiceModeEnabled: false,
      enabledLanguages: ['en'],
    };

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockFlags,
    });

    const TestComponent = () => {
      const { textModeEnabled, loading } = useFeatureFlags();
      return (
        <div>
          <div data-testid="loading">{loading.toString()}</div>
          <div data-testid="text-mode">{textModeEnabled.toString()}</div>
        </div>
      );
    };

    const { getByTestId } = render(
      <FeatureFlagProvider>
        <TestComponent />
      </FeatureFlagProvider>
    );

    // Initially loading
    expect(getByTestId('loading')).toHaveTextContent('true');

    // Wait for flags to be fetched
    await waitFor(() => {
      expect(getByTestId('loading')).toHaveTextContent('false');
    });

    expect(getByTestId('text-mode')).toHaveTextContent('true');
    expect(global.fetch).toHaveBeenCalledWith('http://localhost:8000/api/feature-flags/', {
      headers: {
        'Content-Type': 'application/json',
      },
    });
  });

  it('provides flag values to child components', async () => {
    const mockFlags = {
      textModeEnabled: true,
      voiceModeEnabled: true,
      enabledLanguages: ['en', 'es'],
    };

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockFlags,
    });

    const TestComponent = () => {
      const { voiceModeEnabled, textModeEnabled, enabledLanguages } = useFeatureFlags();
      return (
        <div>
          <div data-testid="voice-mode">{voiceModeEnabled.toString()}</div>
          <div data-testid="text-enabled">{textModeEnabled.toString()}</div>
          <div data-testid="languages">{enabledLanguages.join(',')}</div>
        </div>
      );
    };

    const { getByTestId } = render(
      <FeatureFlagProvider>
        <TestComponent />
      </FeatureFlagProvider>
    );

    await waitFor(() => {
      expect(getByTestId('voice-mode')).toHaveTextContent('true');
      expect(getByTestId('text-enabled')).toHaveTextContent('true');
      expect(getByTestId('languages')).toHaveTextContent('en,es');
    });
  });

  it('handles loading states gracefully', async () => {
    let resolvePromise: (value: any) => void;
    const fetchPromise = new Promise((resolve) => {
      resolvePromise = resolve;
    });

    (global.fetch as jest.Mock).mockReturnValueOnce(fetchPromise);

    const TestComponent = () => {
      const { loading } = useFeatureFlags();
      return <div data-testid="loading">{loading.toString()}</div>;
    };

    const { getByTestId } = render(
      <FeatureFlagProvider>
        <TestComponent />
      </FeatureFlagProvider>
    );

    // Should be loading initially
    expect(getByTestId('loading')).toHaveTextContent('true');

    // Resolve the fetch
    act(() => {
      resolvePromise!({
        ok: true,
        json: async () => ({
          textModeEnabled: true,
          voiceModeEnabled: true,
          enabledLanguages: ['en'],
        }),
      });
    });

    // Should no longer be loading
    await waitFor(() => {
      expect(getByTestId('loading')).toHaveTextContent('false');
    });
  });

  it('retries on network failure', async () => {
    // First call fails
    (global.fetch as jest.Mock)
      .mockRejectedValueOnce(new Error('Network error'))
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          textModeEnabled: true,
          voiceModeEnabled: true,
          enabledLanguages: ['en'],
        }),
      });

    const TestComponent = () => {
      const { textModeEnabled } = useFeatureFlags();
      return <div data-testid="text-mode">{textModeEnabled?.toString() || 'default'}</div>;
    };

    const { getByTestId } = render(
      <FeatureFlagProvider>
        <TestComponent />
      </FeatureFlagProvider>
    );

    // Wait for retry - just check that multiple calls happened
    await waitFor(() => {
      expect((global.fetch as jest.Mock).mock.calls.length).toBeGreaterThanOrEqual(2);
    }, { timeout: 3000 });

    await waitFor(() => {
      expect(getByTestId('text-mode')).toHaveTextContent('true');
    });
  });

  it('caches flags in sessionStorage', async () => {
    const mockFlags = {
      textModeEnabled: true,
      voiceModeEnabled: false,
      enabledLanguages: ['en'],
    };

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockFlags,
    });

    render(
      <FeatureFlagProvider>
        <div>Test</div>
      </FeatureFlagProvider>
    );

    await waitFor(() => {
      const cached = sessionStorage.getItem('feature-flags');
      expect(cached).toBeTruthy();
      const parsedCache = JSON.parse(cached!);
      expect(parsedCache.textModeEnabled).toBe(true);
      expect(parsedCache.voiceModeEnabled).toBe(false);
    });
  });

  it('uses cached flags when fetch fails', async () => {
    // Set up cached flags
    const cachedFlags = {
      textModeEnabled: false,
      voiceModeEnabled: true,
      enabledLanguages: ['en', 'es'],
    };
    sessionStorage.setItem('feature-flags', JSON.stringify(cachedFlags));

    // Fetch fails
    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

    const TestComponent = () => {
      const { textModeEnabled, voiceModeEnabled, loading } = useFeatureFlags();
      return (
        <div>
          <div data-testid="loading">{loading.toString()}</div>
          <div data-testid="text-mode">{textModeEnabled.toString()}</div>
          <div data-testid="voice-mode">{voiceModeEnabled.toString()}</div>
        </div>
      );
    };

    const { getByTestId } = render(
      <FeatureFlagProvider>
        <TestComponent />
      </FeatureFlagProvider>
    );

    await waitFor(() => {
      expect(getByTestId('loading')).toHaveTextContent('false');
      expect(getByTestId('text-mode')).toHaveTextContent('false');
      expect(getByTestId('voice-mode')).toHaveTextContent('true');
    });
  });

  it('provides refetch function', async () => {
    const initialFlags = {
      textModeEnabled: true,
      voiceModeEnabled: true,
      enabledLanguages: ['en'],
    };

    const updatedFlags = {
      textModeEnabled: false,
      voiceModeEnabled: true,
      enabledLanguages: ['en', 'es'],
    };

    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => initialFlags,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => updatedFlags,
      });

    const TestComponent = () => {
      const { textModeEnabled, refetch } = useFeatureFlags();
      return (
        <div>
          <div data-testid="text-mode">{textModeEnabled?.toString() || 'default'}</div>
          <button onClick={refetch}>Refetch</button>
        </div>
      );
    };

    const { getByTestId, getByText } = render(
      <FeatureFlagProvider>
        <TestComponent />
      </FeatureFlagProvider>
    );

    await waitFor(() => {
      expect(getByTestId('text-mode')).toHaveTextContent('true');
    });

    // Click refetch
    act(() => {
      getByText('Refetch').click();
    });

    await waitFor(() => {
      expect(getByTestId('text-mode')).toHaveTextContent('false');
    });

    expect(global.fetch).toHaveBeenCalledTimes(2);
  });

  it('includes session headers if available', async () => {
    // Mock session ID from session storage
    sessionStorage.setItem('sessionId', 'test-session-123');

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        textModeEnabled: true,
        voiceModeEnabled: true,
        enabledLanguages: ['en'],
      }),
    });

    render(
      <FeatureFlagProvider>
        <div>Test</div>
      </FeatureFlagProvider>
    );

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('http://localhost:8000/api/feature-flags/', {
        headers: {
          'Content-Type': 'application/json',
          'X-Session-ID': 'test-session-123',
        },
      });
    });
  });
});