// API response types for re-frame

export interface ReframeResponse {
  success: boolean;
  response: string;
  frameworks_used: string[];
  transparency: {
    agents_used: string[];
    techniques_applied: string[];
    framework_details: {
      [framework: string]: {
        techniques: string[];
        confidence: number;
        patterns_addressed: string[];
      }
    };
    selection_rationale: string;
  };
  alternative_perspectives?: Array<{
    framework: string;
    perspective: string;
  }>;
  error?: string;
}

export type Framework = 'CBT' | 'DBT' | 'ACT' | 'Stoicism';