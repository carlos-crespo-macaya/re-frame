import React from 'react';
import { formatDuration } from '@/lib/audio';

interface PlaybackControlsProps {
  isPlaying: boolean;
  currentTime: number; // in milliseconds
  duration: number; // in milliseconds
  onPlayPause: () => void;
  onSeek?: (time: number) => void;
  onSkip?: (seconds: number) => void;
  onStop?: () => void;
  showSkipButtons?: boolean;
  className?: string;
}

export const PlaybackControls: React.FC<PlaybackControlsProps> = ({
  isPlaying,
  currentTime,
  duration,
  onPlayPause,
  onSeek,
  onSkip,
  onStop,
  showSkipButtons = true,
  className = ''
}) => {
  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (onSeek) {
      const newTime = (parseFloat(e.target.value) / 100) * duration;
      onSeek(newTime);
    }
  };

  return (
    <div className={`playback-controls ${className}`}>
      <div className="playback-controls__buttons">
        {showSkipButtons && (
          <button
            type="button"
            className="playback-controls__button playback-controls__button--skip"
            onClick={() => onSkip?.(-10)}
            aria-label="Skip back 10 seconds"
            title="Skip back 10 seconds"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z" fill="currentColor"/>
              <text x="12" y="16" textAnchor="middle" fontSize="10" fill="currentColor">10</text>
            </svg>
          </button>
        )}

        <button
          type="button"
          className="playback-controls__button playback-controls__button--play"
          onClick={onPlayPause}
          aria-label={isPlaying ? 'Pause' : 'Play'}
        >
          {isPlaying ? (
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" fill="currentColor"/>
            </svg>
          ) : (
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M8 5v14l11-7L8 5z" fill="currentColor"/>
            </svg>
          )}
        </button>

        {showSkipButtons && (
          <button
            type="button"
            className="playback-controls__button playback-controls__button--skip"
            onClick={() => onSkip?.(10)}
            aria-label="Skip forward 10 seconds"
            title="Skip forward 10 seconds"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M12 5V1l5 5-5 5V7c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6h2c0 4.42-3.58 8-8 8s-8-3.58-8-8 3.58-8 8-8z" fill="currentColor"/>
              <text x="12" y="16" textAnchor="middle" fontSize="10" fill="currentColor">10</text>
            </svg>
          </button>
        )}

        {onStop && (
          <button
            type="button"
            className="playback-controls__button playback-controls__button--stop"
            onClick={onStop}
            aria-label="Stop"
            title="Stop playback"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M6 6h12v12H6V6z" fill="currentColor"/>
            </svg>
          </button>
        )}
      </div>

      {onSeek && (
        <div className="playback-controls__progress">
          <span className="playback-controls__time">
            {formatDuration(currentTime)}
          </span>
          
          <div className="playback-controls__slider-container">
            <input
              type="range"
              className="playback-controls__slider"
              min="0"
              max="100"
              value={progress}
              onChange={handleSeek}
              aria-label="Seek"
              aria-valuemin={0}
              aria-valuemax={duration}
              aria-valuenow={currentTime}
              aria-valuetext={`${formatDuration(currentTime)} of ${formatDuration(duration)}`}
            />
            <div 
              className="playback-controls__progress-bar"
              style={{ width: `${progress}%` }}
            />
          </div>
          
          <span className="playback-controls__time">
            {formatDuration(duration)}
          </span>
        </div>
      )}
    </div>
  );
};

export default PlaybackControls;