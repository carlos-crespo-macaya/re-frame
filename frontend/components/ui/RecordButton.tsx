/* eslint-disable jsx-a11y/aria-proptypes */
import React from 'react';
import { MicPermissionState } from '@/lib/audio';

interface RecordButtonProps {
  isRecording: boolean;
  micPermission: MicPermissionState;
  onStartRecording: () => void;
  onStopRecording: () => void;
  disabled?: boolean;
  className?: string;
}

export const RecordButton: React.FC<RecordButtonProps> = ({
  isRecording,
  micPermission,
  onStartRecording,
  onStopRecording,
  disabled = false,
  className = ''
}) => {
  const handleClick = () => {
    console.log('RecordButton clicked - isRecording:', isRecording, 'micPermission:', micPermission)
    if (isRecording) {
      onStopRecording();
    } else {
      onStartRecording();
    }
  };

  const getButtonContent = () => {
    if (isRecording) {
      return (
        <>
          <span className="record-button__dot" />
          <span className="sr-only">Stop recording</span>
        </>
      );
    }

    if (micPermission === 'denied') {
      return (
        <>
          <svg 
            className="record-button__icon record-button__icon--disabled" 
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
            <line 
              x1="3" 
              y1="3" 
              x2="21" 
              y2="21" 
              stroke="currentColor" 
              strokeWidth="2"
            />
          </svg>
          <span className="sr-only">Microphone access denied</span>
        </>
      );
    }

    return (
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
        <span className="sr-only">Start recording</span>
      </>
    );
  };

  const getTooltip = () => {
    if (micPermission === 'denied') {
      return 'Microphone access denied';
    }
    if (isRecording) {
      return 'Click to stop recording';
    }
    return 'Speak instead of typing';
  };

  const commonProps = {
    type: 'button' as const,
    onClick: handleClick,
    disabled: disabled || micPermission === 'denied',
    className: `record-button ${isRecording ? 'record-button--recording' : ''} ${className}`,
    title: getTooltip()
  };

  if (isRecording) {
    return (
      <button
        {...commonProps}
        aria-label="Stop recording"
        aria-pressed="true"
      >
        {getButtonContent()}
      </button>
    );
  }

  return (
    <button
      {...commonProps}
      aria-label="Start recording"
      aria-pressed="false"
    >
      {getButtonContent()}
    </button>
  );
};

export default RecordButton;