import { getUiFeatureFlags as getUiFeatureFlagsOp } from "./generated";
import type { GetUiFeatureFlagsResponse } from "./generated";

export type UIFeatureFlags = {
  chat_mode_enabled: boolean;
  voice_mode_enabled: boolean;
  notepad_mode_enabled: boolean;
};

export async function fetchUiFeatureFlags(): Promise<UIFeatureFlags> {
  // Using typed named export from generated sdk
  const resp: GetUiFeatureFlagsResponse = await getUiFeatureFlagsOp();
  // Map to local shape explicitly
  return {
    chat_mode_enabled: Boolean(resp.chat_mode_enabled),
    voice_mode_enabled: Boolean(resp.voice_mode_enabled),
    notepad_mode_enabled: Boolean(resp.notepad_mode_enabled),
  };
}
