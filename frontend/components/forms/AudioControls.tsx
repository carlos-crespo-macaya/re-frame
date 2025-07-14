import React, { useState, useCallback } from 'react';
import { RecordButton } from '@/components/ui/RecordButton';
import { AudioVisualizer } from '@/components/ui/AudioVisualizer';
import { PlaybackControls } from '@/components/ui/PlaybackControls';
import { AudioMode, MicPermissionState, AudioState } from '@/lib/audio';

interface AudioControlsProps {
  audioState: AudioState;
  onStartRecording: () => void;
  onStopRecording: () => void;
  onModeChange: (mode: AudioMode) => void;
  onTranscriptionEdit?: (text: string) => void;
  onTranscriptionAccept?: () => void;
  onReRecord?: () => void;
  onPermissionDenied?: () => void;
  disabled?: boolean;
  className?: string;
}

export const AudioControls: React.FC<AudioControlsProps> = ({
  audioState,
  onStartRecording,
  onStopRecording,
  onModeChange,
  onTranscriptionEdit,
  onTranscriptionAccept,
  onReRecord,
  onPermissionDenied,
  disabled = false,
  className = ''
}) => {
  const [showModeMenu, setShowModeMenu] = useState(false);
  const [isEditingTranscription, setIsEditingTranscription] = useState(false);
  const [editedTranscription, setEditedTranscription] = useState('');

  const handleModeChange = useCallback((mode: AudioMode) => {
    onModeChange(mode);
    setShowModeMenu(false);
  }, [onModeChange]);

  const handleEditClick = useCallback(() => {
    setEditedTranscription(audioState.transcription);
    setIsEditingTranscription(true);
  }, [audioState.transcription]);

  const handleSaveEdit = useCallback(() => {
    onTranscriptionEdit?.(editedTranscription);
    setIsEditingTranscription(false);
  }, [editedTranscription, onTranscriptionEdit]);

  const handleCancelEdit = useCallback(() => {
    setIsEditingTranscription(false);
    setEditedTranscription('');
  }, []);

  // Show permission request UI
  if (audioState.micPermission === 'prompt' && audioState.audioEnabled) {
    return (
      <div className={`audio-controls audio-controls--permission ${className}`}>
        <div className="audio-controls__permission">
          <svg 
            className="audio-controls__permission-icon" 
            width="24" 
            height="24" 
            viewBox="0 0 24 24" 
            fill="none"
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
          <h3 className="audio-controls__permission-title">Allow microphone access?</h3>
          <p className="audio-controls__permission-text">
            Speak your thoughts instead of typing.
          </p>
          <ul className="audio-controls__permission-list">
            <li>Your voice is converted to text</li>
            <li>Audio is not stored</li>
            <li>You can review before sending</li>
          </ul>
          <div className="audio-controls__permission-buttons">
            <button 
              type="button" 
              className="audio-controls__button audio-controls__button--primary"
              onClick={onStartRecording}
            >
              Allow microphone
            </button>
            <button 
              type="button" 
              className="audio-controls__button audio-controls__button--secondary"
              onClick={() => onPermissionDenied?.()}
            >
              Stay with typing
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Recording state
  if (audioState.isRecording) {
    return (
      <div className={`audio-controls audio-controls--recording ${className}`} data-recording="true">
        <div className="audio-controls__header">
          <span className="audio-controls__status">
            <span className="audio-controls__status-dot" />
            Listening... ({audioState.mode === 'instant' ? 'Instant Mode' : 'Manual Mode'})
          </span>
          
          <button
            type="button"
            className="audio-controls__mode-button"
            onClick={() => setShowModeMenu(!showModeMenu)}
            aria-label="Change audio mode"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" fill="currentColor"/>
              <path d="M7 10l5 5 5-5H7z" fill="currentColor"/>
            </svg>
          </button>

          {showModeMenu && (
            <div className="audio-controls__mode-menu">
              <button
                type="button"
                className={`audio-controls__mode-option ${audioState.mode === 'manual' ? 'audio-controls__mode-option--active' : ''}`}
                onClick={() => handleModeChange('manual')}
              >
                <span>📝</span> Manual Mode
                {audioState.mode === 'manual' && <span className="audio-controls__check">✓</span>}
              </button>
              <button
                type="button"
                className={`audio-controls__mode-option ${audioState.mode === 'instant' ? 'audio-controls__mode-option--active' : ''}`}
                onClick={() => handleModeChange('instant')}
              >
                <span>💬</span> Instant Mode
                {audioState.mode === 'instant' && <span className="audio-controls__check">✓</span>}
              </button>
            </div>
          )}
        </div>

        {audioState.transcription && (
          <div className="audio-controls__transcription">
            <p className="audio-controls__transcription-text">
              "{audioState.transcription}"
            </p>
          </div>
        )}

        <AudioVisualizer
          audioLevel={audioState.audioLevel}
          isActive={true}
          variant="waveform"
          className="audio-controls__visualizer"
        />

        <div className="audio-controls__recording-buttons">
          {audioState.mode === 'manual' ? (
            <>
              <button
                type="button"
                className="audio-controls__button audio-controls__button--secondary"
                onClick={() => {/* Handle pause */}}
              >
                ⏸ Pause
              </button>
              <button
                type="button"
                className="audio-controls__button audio-controls__button--primary"
                onClick={onStopRecording}
              >
                ✓ Done
              </button>
            </>
          ) : (
            <div className="audio-controls__instant-hint">
              <span className="audio-controls__instant-icon">🎙️</span>
              <span>Release to send...</span>
            </div>
          )}
        </div>

        {audioState.mode === 'manual' && (
          <p className="audio-controls__hint">
            Click Done when finished
          </p>
        )}
        {audioState.mode === 'instant' && (
          <p className="audio-controls__hint">
            Click and hold to record • Release to send
          </p>
        )}
      </div>
    );
  }

  // Review transcription state (Manual Mode only)
  if (audioState.mode === 'manual' && audioState.transcription && !audioState.isRecording) {
    return (
      <div className={`audio-controls audio-controls--review ${className}`}>
        <h3 className="audio-controls__review-title">Review your message:</h3>
        
        {isEditingTranscription ? (
          <div className="audio-controls__edit">
            <textarea
              className="audio-controls__edit-textarea"
              value={editedTranscription}
              onChange={(e) => setEditedTranscription(e.target.value)}
              autoFocus
            />
            <div className="audio-controls__edit-buttons">
              <button
                type="button"
                className="audio-controls__button audio-controls__button--secondary"
                onClick={handleCancelEdit}
              >
                Cancel
              </button>
              <button
                type="button"
                className="audio-controls__button audio-controls__button--primary"
                onClick={handleSaveEdit}
              >
                Save
              </button>
            </div>
          </div>
        ) : (
          <>
            <p className="audio-controls__transcription-text">
              {audioState.transcription}
            </p>
            <div className="audio-controls__review-buttons">
              <button
                type="button"
                className="audio-controls__button audio-controls__button--secondary"
                onClick={handleEditClick}
              >
                ✏️ Edit text
              </button>
              <button
                type="button"
                className="audio-controls__button audio-controls__button--secondary"
                onClick={onReRecord}
              >
                🎤 Re-record
              </button>
              <button
                type="button"
                className="audio-controls__button audio-controls__button--primary"
                onClick={onTranscriptionAccept}
              >
                👍 Looks good
              </button>
            </div>
          </>
        )}
      </div>
    );
  }

  // Default state - record button with mode-specific behavior
  return (
    <div className={`audio-controls ${className}`}>
      {audioState.mode === 'instant' ? (
        <button
          type="button"
          className={`record-button ${audioState.isRecording ? 'record-button--recording' : ''} audio-controls__record-button`}
          onMouseDown={(e) => {
            e.preventDefault();
            onStartRecording();
          }}
          onMouseUp={(e) => {
            e.preventDefault();
            if (audioState.isRecording) {
              onStopRecording();
            }
          }}
          onMouseLeave={() => {
            if (audioState.isRecording) {
              onStopRecording();
            }
          }}
          onTouchStart={(e) => {
            e.preventDefault();
            onStartRecording();
          }}
          onTouchEnd={(e) => {
            e.preventDefault();
            if (audioState.isRecording) {
              onStopRecording();
            }
          }}
          disabled={disabled || audioState.micPermission === 'denied'}
          title={audioState.isRecording ? 'Release to send' : 'Hold to record'}
          aria-label={audioState.isRecording ? 'Recording - release to send' : 'Hold to record'}
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
              <span className="sr-only">Hold to record</span>
            </>
          )}
        </button>
      ) : (
        <RecordButton
          isRecording={audioState.isRecording}
          micPermission={audioState.micPermission}
          onStartRecording={onStartRecording}
          onStopRecording={onStopRecording}
          disabled={disabled}
          className="audio-controls__record-button"
        />
      )}
    </div>
  );
};

export default AudioControls;