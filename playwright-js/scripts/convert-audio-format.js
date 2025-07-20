#!/usr/bin/env node

/**
 * Convert audio files from 16kHz to 48kHz for Chromium compatibility
 * This is the JavaScript port of the Python audio conversion script
 */

const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const { promisify } = require('util');

const execAsync = promisify(exec);

const AUDIO_DIR = path.join(__dirname, '..', '..', 'tests', 'e2e', 'fixtures', 'audio');

async function checkFfmpeg() {
  try {
    await execAsync('ffmpeg -version');
    return true;
  } catch (error) {
    console.error('❌ ffmpeg is not installed. Install with: brew install ffmpeg');
    return false;
  }
}

async function convertAudioFile(inputPath, outputPath) {
  const command = `ffmpeg -i "${inputPath}" -ar 48000 -ac 1 -y "${outputPath}"`;
  
  try {
    const { stdout, stderr } = await execAsync(command);
    console.log(`✓ Converted: ${path.basename(outputPath)}`);
    return true;
  } catch (error) {
    console.error(`✗ Error converting ${inputPath}: ${error.message}`);
    return false;
  }
}

async function findAudioFiles(dir) {
  const files = [];
  
  function walkDir(currentPath) {
    const entries = fs.readdirSync(currentPath, { withFileTypes: true });
    
    for (const entry of entries) {
      const fullPath = path.join(currentPath, entry.name);
      
      if (entry.isDirectory()) {
        walkDir(fullPath);
      } else if (entry.isFile() && entry.name.endsWith('.wav') && !entry.name.includes('-48k')) {
        files.push(fullPath);
      }
    }
  }
  
  walkDir(dir);
  return files;
}

async function getAudioInfo(filePath) {
  try {
    const command = `ffprobe -v quiet -print_format json -show_format -show_streams "${filePath}"`;
    const { stdout } = await execAsync(command);
    const info = JSON.parse(stdout);
    const audioStream = info.streams.find(s => s.codec_type === 'audio');
    
    return {
      sampleRate: parseInt(audioStream.sample_rate),
      channels: audioStream.channels,
      duration: parseFloat(info.format.duration)
    };
  } catch (error) {
    console.error(`Error getting info for ${filePath}: ${error.message}`);
    return null;
  }
}

async function main() {
  console.log('Audio Format Conversion Script');
  console.log('==============================\n');
  
  // Check if ffmpeg is installed
  if (!await checkFfmpeg()) {
    process.exit(1);
  }
  
  // Check if audio directory exists
  if (!fs.existsSync(AUDIO_DIR)) {
    console.error(`❌ Audio directory not found: ${AUDIO_DIR}`);
    console.log('Please run from the playwright-js directory');
    process.exit(1);
  }
  
  // Find all WAV files
  const audioFiles = await findAudioFiles(AUDIO_DIR);
  console.log(`Found ${audioFiles.length} audio files\n`);
  
  let convertedCount = 0;
  
  for (const audioFile of audioFiles) {
    console.log(`\nProcessing: ${path.relative(AUDIO_DIR, audioFile)}`);
    
    // Get audio info
    const info = await getAudioInfo(audioFile);
    if (!info) continue;
    
    console.log(`  Current: ${info.sampleRate}Hz, ${info.channels} channel(s), ${info.duration.toFixed(1)}s`);
    
    // Only convert if not already 48kHz
    if (info.sampleRate !== 48000) {
      const outputPath = audioFile.replace('.wav', '-48k.wav');
      
      if (await convertAudioFile(audioFile, outputPath)) {
        convertedCount++;
        
        // Verify conversion
        const newInfo = await getAudioInfo(outputPath);
        if (newInfo) {
          console.log(`  New: ${newInfo.sampleRate}Hz, ${newInfo.channels} channel(s)`);
        }
      }
    } else {
      console.log('  Already 48kHz, skipping');
    }
  }
  
  console.log(`\n✅ Converted ${convertedCount} files to 48kHz`);
  
  // Test with simple audio generation if no files found
  if (audioFiles.length === 0) {
    console.log('\n⚠️  No audio files found. Creating test audio...');
    
    const testOutput = path.join(AUDIO_DIR, 'test-tone-48k.wav');
    const testCommand = `ffmpeg -f lavfi -i "sine=frequency=440:duration=2" -ar 48000 -ac 1 -y "${testOutput}"`;
    
    try {
      await execAsync(testCommand);
      console.log('✓ Created test tone at 48kHz');
    } catch (error) {
      console.error('✗ Failed to create test tone:', error.message);
    }
  }
}

// Run the script
main().catch(error => {
  console.error('Script failed:', error);
  process.exit(1);
});