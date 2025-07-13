import React, { useEffect, useRef } from 'react';

interface AudioVisualizerProps {
  audioLevel: number; // 0-1 range
  isActive: boolean;
  variant?: 'waveform' | 'dots';
  className?: string;
}

export const AudioVisualizer: React.FC<AudioVisualizerProps> = ({
  audioLevel,
  isActive,
  variant = 'waveform',
  className = ''
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();
  const barsRef = useRef<number[]>([]);

  useEffect(() => {
    if (!canvasRef.current || !isActive) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    const updateCanvasSize = () => {
      canvas.width = canvas.offsetWidth * window.devicePixelRatio;
      canvas.height = canvas.offsetHeight * window.devicePixelRatio;
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    };
    updateCanvasSize();
    window.addEventListener('resize', updateCanvasSize);

    // Initialize bars
    const barCount = variant === 'waveform' ? 20 : 3;
    if (barsRef.current.length !== barCount) {
      barsRef.current = new Array(barCount).fill(0);
    }

    const animate = () => {
      if (!isActive) return;

      ctx.clearRect(0, 0, canvas.offsetWidth, canvas.offsetHeight);

      if (variant === 'waveform') {
        drawWaveform(ctx, canvas.offsetWidth, canvas.offsetHeight);
      } else {
        drawDots(ctx, canvas.offsetWidth, canvas.offsetHeight);
      }

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', updateCanvasSize);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isActive, variant, audioLevel]);

  const drawWaveform = (ctx: CanvasRenderingContext2D, width: number, height: number) => {
    const barWidth = width / barsRef.current.length;
    const barGap = 2;

    barsRef.current.forEach((bar, index) => {
      // Update bar height based on audio level with some randomness
      const targetHeight = audioLevel * height * (0.3 + Math.random() * 0.7);
      barsRef.current[index] = bar + (targetHeight - bar) * 0.3;

      const barHeight = Math.max(4, barsRef.current[index]);
      const x = index * barWidth + barGap / 2;
      const y = (height - barHeight) / 2;

      const textSecondaryColor = getComputedStyle(document.documentElement)
        .getPropertyValue('--color-text-secondary').trim() || '#6b7280'; // Fallback gray-500
      ctx.fillStyle = textSecondaryColor;
      ctx.fillRect(x, y, barWidth - barGap, barHeight);
    });
  };

  const drawDots = (ctx: CanvasRenderingContext2D, width: number, height: number) => {
    const dotSize = 8;
    const dotGap = 16;
    const startX = (width - (barsRef.current.length * (dotSize + dotGap) - dotGap)) / 2;

    barsRef.current.forEach((_, index) => {
      const x = startX + index * (dotSize + dotGap);
      const y = height / 2;

      // Animate dot size based on audio level
      const scale = isActive ? 0.5 + audioLevel * 0.5 : 0.3;
      const opacity = isActive ? 0.4 + audioLevel * 0.6 : 0.3;

      const primaryColor = getComputedStyle(document.documentElement)
        .getPropertyValue('--color-primary').trim() || '#3b82f6'; // Fallback blue-500
      ctx.fillStyle = primaryColor;
      ctx.globalAlpha = opacity;
      
      ctx.beginPath();
      ctx.arc(x + dotSize / 2, y, dotSize / 2 * scale, 0, Math.PI * 2);
      ctx.fill();
      
      ctx.globalAlpha = 1;
    });
  };

  if (variant === 'waveform') {
    return (
      <div className={`audio-visualizer audio-visualizer--waveform ${className}`}>
        <canvas
          ref={canvasRef}
          className="audio-visualizer__canvas"
          aria-label="Audio level visualization"
          role="img"
        />
      </div>
    );
  }

  return (
    <div className={`audio-visualizer audio-visualizer--dots ${className}`}>
      <canvas
        ref={canvasRef}
        className="audio-visualizer__canvas"
        aria-label="Audio activity indicator"
        role="img"
      />
    </div>
  );
};

export default AudioVisualizer;