// API response types for re-frame

// Transparency data structure
export interface TransparencyData {
  techniques_applied: string[];
  reasoning_path: {
    intake: Record<string, any>;
    cbt: Record<string, any>;
    synthesis: Record<string, any>;
  };
  stage: string;
  key_points: string[];
  techniques_explained: string;
}

// Main API response
export interface ReframeResponse {
  success: boolean;
  response: string;
  transparency: TransparencyData;
  techniques_used: string[];
  error?: string | null;
  key_points: string[];
  techniques_explained: string;
}

// Request type
export interface ReframeRequest {
  thought: string;
  context?: string | null;
}

export type Framework = 'CBT' | 'DBT' | 'ACT' | 'Stoicism';