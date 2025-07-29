import { useFeatureFlags } from './feature-flag-provider';

type FlagName = 
  | 'textModeEnabled'
  | 'voiceModeEnabled'
  | 'enabledLanguages';

type FlagValue<T extends FlagName> = 
  T extends 'enabledLanguages' ? string[] : boolean;

export function useFeatureFlag<T extends FlagName>(
  flagName: T
): {
  value: FlagValue<T>;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
} {
  const flags = useFeatureFlags();
  
  return {
    value: flags[flagName] as FlagValue<T>,
    loading: flags.loading,
    error: flags.error,
    refetch: flags.refetch,
  };
}

// Convenience hooks for common flags
export function useTextModeEnabled() {
  return useFeatureFlag('textModeEnabled');
}

export function useVoiceModeEnabled() {
  return useFeatureFlag('voiceModeEnabled');
}

export function useEnabledLanguages() {
  return useFeatureFlag('enabledLanguages');
}