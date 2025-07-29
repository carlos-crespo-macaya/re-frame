import React from 'react';
import { waitFor, act } from '@testing-library/react';
import { renderHook } from '@testing-library/react';
import { FeatureFlagProvider } from '../feature-flag-provider';
import { useFeatureFlag, useTextModeEnabled, useVoiceModeEnabled, useEnabledLanguages } from '../use-feature-flag';

// Mock fetch
global.fetch = jest.fn();

describe('useFeatureFlag', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    sessionStorage.clear();
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <FeatureFlagProvider>{children}</FeatureFlagProvider>
  );

  it('returns flag value and loading state', async () => {
    const mockFlags = {
      textModeEnabled: true,
      voiceModeEnabled: false,
      enabledLanguages: ['en'],
    };

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockFlags,
    });

    const { result } = renderHook(() => useFeatureFlag('textModeEnabled'), { wrapper });

    // Initially loading
    expect(result.current.loading).toBe(true);
    expect(result.current.value).toBe(true); // Default value

    // Wait for flags to load
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.value).toBe(true);
  });

  it('returns voice mode flag correctly', async () => {
    const mockFlags = {
      textModeEnabled: true,
      voiceModeEnabled: false,
      enabledLanguages: ['en'],
    };

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockFlags,
    });

    const { result } = renderHook(() => useFeatureFlag('voiceModeEnabled'), { wrapper });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.value).toBe(false);
  });

  it('updates when flags are refetched', async () => {
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

    const { result } = renderHook(() => useFeatureFlag('textModeEnabled'), { wrapper });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.value).toBe(true);

    // Refetch flags
    await act(async () => {
      await result.current.refetch();
    });

    await waitFor(() => {
      expect(result.current.value).toBe(false);
    });
  });

  it('provides consistent values across multiple hooks', async () => {
    const mockFlags = {
      textModeEnabled: true,
      voiceModeEnabled: false,
      enabledLanguages: ['en', 'es'],
    };

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockFlags,
    });

    const { result } = renderHook(() => ({
      text: useFeatureFlag('textModeEnabled'),
      voice: useFeatureFlag('voiceModeEnabled'),
      languages: useFeatureFlag('enabledLanguages'),
    }), { wrapper });

    await waitFor(() => {
      expect(result.current.text.loading).toBe(false);
      expect(result.current.voice.loading).toBe(false);
      expect(result.current.languages.loading).toBe(false);
    });

    expect(result.current.text.value).toBe(true);
    expect(result.current.voice.value).toBe(false);
    expect(result.current.languages.value).toEqual(['en', 'es']);
  });

  it('provides access to languages array', async () => {
    const mockFlags = {
      textModeEnabled: true,
      voiceModeEnabled: true,
      enabledLanguages: ['en', 'es', 'fr'],
    };

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockFlags,
    });

    const { result } = renderHook(() => useFeatureFlag('enabledLanguages'), { wrapper });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.value).toEqual(['en', 'es', 'fr']);
  });

  it('throws error when used outside provider', () => {
    // Suppress console.error for this test
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

    expect(() => {
      renderHook(() => useFeatureFlag('textModeEnabled'));
    }).toThrow('useFeatureFlags must be used within a FeatureFlagProvider');

    consoleSpy.mockRestore();
  });

  describe('convenience hooks', () => {
    it('useTextModeEnabled returns text mode flag', async () => {
      const mockFlags = {
        textModeEnabled: true,
        voiceModeEnabled: false,
        enabledLanguages: ['en'],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockFlags,
      });

      const { result } = renderHook(() => useTextModeEnabled(), { wrapper });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.value).toBe(true);
    });

    it('useVoiceModeEnabled returns voice mode flag', async () => {
      const mockFlags = {
        textModeEnabled: true,
        voiceModeEnabled: false,
        enabledLanguages: ['en'],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockFlags,
      });

      const { result } = renderHook(() => useVoiceModeEnabled(), { wrapper });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.value).toBe(false);
    });

    it('useEnabledLanguages returns languages array', async () => {
      const mockFlags = {
        textModeEnabled: true,
        voiceModeEnabled: true,
        enabledLanguages: ['en', 'es', 'pt', 'fr'],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockFlags,
      });

      const { result } = renderHook(() => useEnabledLanguages(), { wrapper });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.value).toEqual(['en', 'es', 'pt', 'fr']);
    });
  });
});