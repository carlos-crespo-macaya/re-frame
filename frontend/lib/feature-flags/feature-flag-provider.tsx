'use client';

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { getSessionId } from '../utils/session';

interface FeatureFlagsResponse {
  textModeEnabled: boolean;
  voiceModeEnabled: boolean;
  enabledLanguages: string[];
}

interface FeatureFlagContextValue extends FeatureFlagsResponse {
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

const getDefaultFlags = (): FeatureFlagsResponse => ({
  textModeEnabled: true,
  voiceModeEnabled: true,
  enabledLanguages: ['en', 'es', 'pt', 'fr', 'de', 'it', 'nl', 'pl', 'uk', 'cs'],
});

const FeatureFlagContext = createContext<FeatureFlagContextValue | undefined>(undefined);

export function FeatureFlagProvider({ children }: { children: React.ReactNode }) {
  const [data, setData] = useState<FeatureFlagsResponse>(() => {
    // Try to load from cache first
    if (typeof window !== 'undefined') {
      const cached = sessionStorage.getItem('feature-flags');
      if (cached) {
        try {
          return JSON.parse(cached);
        } catch (e) {
          console.error('Failed to parse cached feature flags:', e);
        }
      }
    }
    return getDefaultFlags();
  });
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [retryCount, setRetryCount] = useState(0);

  const fetchFlags = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };

      // Add session ID if available
      const sessionId = getSessionId();
      if (sessionId) {
        headers['X-Session-ID'] = sessionId;
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/feature-flags/`, { headers });

      if (!response.ok) {
        throw new Error(`Failed to fetch feature flags: ${response.status}`);
      }

      const flagsData: FeatureFlagsResponse = await response.json();
      
      setData(flagsData);
      
      // Cache the flags
      if (typeof window !== 'undefined') {
        sessionStorage.setItem('feature-flags', JSON.stringify(flagsData));
      }
      
      setRetryCount(0);
    } catch (err) {
      console.error('Error fetching feature flags:', err);
      setError(err as Error);
      
      // Try to use cached flags if available
      if (typeof window !== 'undefined') {
        const cached = sessionStorage.getItem('feature-flags');
        if (cached) {
          try {
            setData(JSON.parse(cached));
            console.log('Using cached feature flags due to fetch error');
          } catch (e) {
            console.error('Failed to parse cached feature flags:', e);
          }
        }
      }
      
      // Retry logic
      if (retryCount < 3) {
        setTimeout(() => {
          setRetryCount(prev => prev + 1);
        }, 1000 * Math.pow(2, retryCount)); // Exponential backoff
      }
    } finally {
      setLoading(false);
    }
  }, [retryCount]);

  useEffect(() => {
    fetchFlags();
  }, [fetchFlags]);

  // Retry on error
  useEffect(() => {
    if (retryCount > 0 && retryCount <= 3) {
      fetchFlags();
    }
  }, [retryCount, fetchFlags]);

  const value: FeatureFlagContextValue = {
    ...data,
    loading,
    error,
    refetch: fetchFlags,
  };

  return (
    <FeatureFlagContext.Provider value={value}>
      {children}
    </FeatureFlagContext.Provider>
  );
}

export const useFeatureFlags = () => {
  const context = useContext(FeatureFlagContext);
  if (context === undefined) {
    throw new Error('useFeatureFlags must be used within a FeatureFlagProvider');
  }
  return context;
};