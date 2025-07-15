import React, { useState, useCallback } from 'react';
import { RecordButton } from '@/components/ui/RecordButton';
import { AudioVisualizer } from '@/components/ui/AudioVisualizer';
import { PlaybackControls } from '@/components/ui/PlaybackControls';
import { AudioMode, MicPermissionState, AudioState } from '@/lib/audio';

interface AudioControlsProps {
  audioState: AudioState;
  onStartRecording: () => void;
  onStopRecording: () => void;
  disabled?: boolean;
  className?: string;
}

export const AudioControls: React.FC<AudioControlsProps> = ({
  audioState,
  onStartRecording,
  onStopRecording,
  disabled = false,
  className = ''
}) => {

  // Simple mic button - no modals, no complex UI
  return (
    <div className={`audio-controls ${className}`}>
      <button
        type="button"
        className={`record-button ${audioState.isRecording ? 'record-button--recording' : ''} audio-controls__record-button`}
        onClick={() => {
          if (audioState.isRecording) {
            onStopRecording();
          } else {
            onStartRecording();
          }
        }}
        disabled={disabled || audioState.micPermission === 'denied'}
        title={audioState.isRecording ? 'Click to stop' : 'Click to start'}
        aria-label={audioState.isRecording ? 'Recording - click to stop' : 'Click to start recording'}
        aria-pressed={audioState.isRecording}
      >
        {audioState.isRecording ? (
          <>
            <span className="record-button__dot" />
            <span className="sr-only">Recording</span>
          </>
        ) : (
          <>
            <svg 
              className="record-button__icon" 
              width="20" 
              height="20" 
              viewBox="0 0 24 24" 
              fill="none"
              aria-hidden="true"
            >
              <path 
                d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" 
                fill="currentColor"
              />
              <path 
                d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" 
                fill="currentColor"
              />
            </svg>
            <span className="sr-only">Click to record</span>
          </>
        )}
      </button>
    </div>
  );
};

export default AudioControls;