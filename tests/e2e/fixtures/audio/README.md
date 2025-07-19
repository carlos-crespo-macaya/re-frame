# Audio Test Fixtures

This directory should contain audio files for testing voice features.

## Required Files

1. **test-audio.wav** - A short WAV file (1-3 seconds) with speech
   - Format: 16kHz, 16-bit, mono (to match backend expectations)
   - Content: Simple phrase like "Hello, I need help with something"

2. **silence.wav** - A WAV file with silence
   - Format: 16kHz, 16-bit, mono
   - Duration: 2 seconds

## Generating Test Audio Files

You can create test audio files using:

### Using sox (command line):
```bash
# Generate 2 seconds of silence
sox -n -r 16000 -c 1 -b 16 silence.wav trim 0 2

# Generate a tone (simulating speech)
sox -n -r 16000 -c 1 -b 16 test-tone.wav synth 2 sine 300-3000
```

### Using ffmpeg:
```bash
# Convert any audio to the required format
ffmpeg -i input.mp3 -ar 16000 -ac 1 -sample_fmt s16 test-audio.wav
```

### Using Python:
```python
import numpy as np
import wave

# Generate test audio
sample_rate = 16000
duration = 2  # seconds
frequency = 440  # Hz

t = np.linspace(0, duration, int(sample_rate * duration))
audio_data = np.sin(2 * np.pi * frequency * t) * 0.3
audio_data = (audio_data * 32767).astype(np.int16)

# Save as WAV
with wave.open('test-audio.wav', 'w') as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(sample_rate)
    wav_file.writeframes(audio_data.tobytes())
```

## Using in Tests

```typescript
import * as path from 'path';

const audioFile = path.join(__dirname, 'fixtures', 'audio', 'test-audio.wav');
```