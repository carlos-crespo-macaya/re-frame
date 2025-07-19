#!/usr/bin/env node

const textToSpeech = require('@google-cloud/text-to-speech');
const fs = require('fs');
const path = require('path');
const util = require('util');

// Creates a client
const client = new textToSpeech.TextToSpeechClient();

// Audio phrases for testing
const testPhrases = {
  english: [
    {
      id: 'en-greeting',
      text: "Hello, I'm feeling anxious about an upcoming presentation at work",
      description: 'Initial greeting expressing presentation anxiety',
      voice: { languageCode: 'en-US', name: 'en-US-Journey-F' } // Female voice
    },
    {
      id: 'en-thought-1',
      text: "I keep thinking that everyone will judge me and notice all my mistakes",
      description: 'Catastrophic thinking about judgment',
      voice: { languageCode: 'en-US', name: 'en-US-Journey-F' }
    },
    {
      id: 'en-insight',
      text: "You're right, I guess I'm assuming the worst without any real evidence",
      description: 'Recognition of cognitive distortion',
      voice: { languageCode: 'en-US', name: 'en-US-Journey-F' }
    },
    {
      id: 'en-conclusion',
      text: "Thank you, I feel more confident now and ready to prepare properly",
      description: 'Positive conclusion',
      voice: { languageCode: 'en-US', name: 'en-US-Journey-F' }
    },
    {
      id: 'en-sleep-worry',
      text: "I can't sleep at night because I keep worrying about things",
      description: 'Sleep anxiety issue',
      voice: { languageCode: 'en-US', name: 'en-US-Journey-D' } // Male voice for variety
    }
  ],
  spanish: [
    {
      id: 'es-greeting',
      text: "Hola, me siento ansioso por una presentación que tengo en el trabajo",
      description: 'Saludo inicial expresando ansiedad por presentación',
      voice: { languageCode: 'es-ES', name: 'es-ES-Polyglot-1' } // Spanish female voice
    },
    {
      id: 'es-thought-1',
      text: "Sigo pensando que todos me van a juzgar y notarán todos mis errores",
      description: 'Pensamiento catastrófico sobre el juicio',
      voice: { languageCode: 'es-ES', name: 'es-ES-Polyglot-1' }
    },
    {
      id: 'es-insight',
      text: "Tienes razón, creo que estoy asumiendo lo peor sin evidencia real",
      description: 'Reconocimiento de distorsión cognitiva',
      voice: { languageCode: 'es-ES', name: 'es-ES-Polyglot-1' }
    },
    {
      id: 'es-conclusion',
      text: "Gracias, me siento más confiado ahora y listo para prepararme adecuadamente",
      description: 'Conclusión positiva',
      voice: { languageCode: 'es-ES', name: 'es-ES-Polyglot-1' }
    },
    {
      id: 'es-social',
      text: "Me cuesta mucho hablar con personas nuevas en reuniones sociales",
      description: 'Ansiedad social',
      voice: { languageCode: 'es-ES', name: 'es-ES-Standard-A' } // Spanish Standard female voice
    }
  ]
};

// Create directories if they don't exist
const audioDir = path.join(__dirname, 'audio');
const englishDir = path.join(audioDir, 'english');
const spanishDir = path.join(audioDir, 'spanish');

[audioDir, englishDir, spanishDir].forEach(dir => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
});

// Function to generate speech using Google Cloud Text-to-Speech
async function generateSpeechGoogle(text, voice, outputPath) {
  try {
    // Construct the request
    const request = {
      input: { text: text },
      // Select the voice parameters
      voice: voice,
      // Select the audio encoding - LINEAR16 for WAV at 16kHz
      audioConfig: {
        audioEncoding: 'LINEAR16',
        sampleRateHertz: 16000,
        // Add speech marks for more natural speech
        speakingRate: 1.0,
        pitch: 0.0,
        volumeGainDb: 0.0,
        effectsProfileId: ['small-bluetooth-speaker-class-device'] // Optimize for device playback
      },
    };

    // Performs the text-to-speech request
    const [response] = await client.synthesizeSpeech(request);
    
    // Write the binary audio content to a local file
    const writeFile = util.promisify(fs.writeFile);
    await writeFile(outputPath, response.audioContent, 'binary');
    
    const fileSizeKB = (response.audioContent.length / 1024).toFixed(1);
    console.log(`✓ Created ${outputPath} (${fileSizeKB}KB) using voice ${voice.name}`);
    
    return true;
  } catch (error) {
    console.error(`✗ Error generating ${outputPath}:`, error.message);
    return false;
  }
}

// Function to list available voices (helper)
async function listAvailableVoices() {
  try {
    const [result] = await client.listVoices({});
    const voices = result.voices;
    
    console.log('\nAvailable voices for testing:');
    console.log('\nEnglish (en-US):');
    voices
      .filter(voice => voice.languageCodes[0].startsWith('en-US'))
      .forEach(voice => {
        console.log(`  - ${voice.name} (${voice.ssmlGender})`);
      });
    
    console.log('\nSpanish (es-ES):');
    voices
      .filter(voice => voice.languageCodes[0].startsWith('es-ES'))
      .forEach(voice => {
        console.log(`  - ${voice.name} (${voice.ssmlGender})`);
      });
      
    console.log('\nSpanish (es-MX):');
    voices
      .filter(voice => voice.languageCodes[0].startsWith('es-MX'))
      .forEach(voice => {
        console.log(`  - ${voice.name} (${voice.ssmlGender})`);
      });
  } catch (error) {
    console.error('Error listing voices:', error);
  }
}

// Function to generate audio fixtures
async function generateAudioFixtures() {
  console.log('🎙️  Generating Audio Test Fixtures with Google Cloud TTS\n');
  
  // Check if credentials are set
  if (!process.env.GOOGLE_APPLICATION_CREDENTIALS && !process.env.GOOGLE_CLOUD_PROJECT) {
    console.error('⚠️  Warning: Google Cloud credentials may not be properly configured.');
    console.log('   Set GOOGLE_APPLICATION_CREDENTIALS environment variable to your service account key file.');
    console.log('   Or ensure you have application default credentials configured.\n');
  }
  
  let successCount = 0;
  let failureCount = 0;
  
  // Generate English fixtures
  console.log('📂 Generating English Audio Files:');
  for (const phrase of testPhrases.english) {
    const outputPath = path.join(englishDir, `${phrase.id}.wav`);
    const success = await generateSpeechGoogle(phrase.text, phrase.voice, outputPath);
    
    if (success) {
      successCount++;
      // Also save the metadata
      const metadataPath = path.join(englishDir, `${phrase.id}.json`);
      fs.writeFileSync(metadataPath, JSON.stringify({
        id: phrase.id,
        text: phrase.text,
        description: phrase.description,
        voice: phrase.voice,
        generated: new Date().toISOString()
      }, null, 2));
    } else {
      failureCount++;
    }
  }
  
  console.log('\n📂 Generating Spanish Audio Files:');
  // Generate Spanish fixtures
  for (const phrase of testPhrases.spanish) {
    const outputPath = path.join(spanishDir, `${phrase.id}.wav`);
    const success = await generateSpeechGoogle(phrase.text, phrase.voice, outputPath);
    
    if (success) {
      successCount++;
      // Also save the metadata
      const metadataPath = path.join(spanishDir, `${phrase.id}.json`);
      fs.writeFileSync(metadataPath, JSON.stringify({
        id: phrase.id,
        text: phrase.text,
        description: phrase.description,
        voice: phrase.voice,
        generated: new Date().toISOString()
      }, null, 2));
    } else {
      failureCount++;
    }
  }
  
  // Create an index file
  const indexPath = path.join(audioDir, 'index.json');
  fs.writeFileSync(indexPath, JSON.stringify({
    generated: new Date().toISOString(),
    phrases: testPhrases,
    format: {
      sampleRate: 16000,
      channels: 1,
      bitDepth: 16,
      encoding: 'LINEAR16',
      provider: 'Google Cloud Text-to-Speech'
    },
    statistics: {
      total: successCount + failureCount,
      success: successCount,
      failure: failureCount
    }
  }, null, 2));
  
  console.log('\n📊 Generation Summary:');
  console.log(`✅ Successfully generated: ${successCount} files`);
  if (failureCount > 0) {
    console.log(`❌ Failed: ${failureCount} files`);
  }
  console.log(`📍 Location: ${audioDir}`);
  
  // Optionally list available voices
  if (process.argv.includes('--list-voices')) {
    await listAvailableVoices();
  }
}

// Function to verify audio files
async function verifyAudioFiles() {
  console.log('\n🔍 Verifying generated audio files:\n');
  
  const languages = ['english', 'spanish'];
  let allFilesExist = true;
  
  for (const lang of languages) {
    const phrases = testPhrases[lang];
    const dir = lang === 'english' ? englishDir : spanishDir;
    
    console.log(`${lang.charAt(0).toUpperCase() + lang.slice(1)}:`);
    
    for (const phrase of phrases) {
      const audioPath = path.join(dir, `${phrase.id}.wav`);
      const metadataPath = path.join(dir, `${phrase.id}.json`);
      
      const audioExists = fs.existsSync(audioPath);
      const metadataExists = fs.existsSync(metadataPath);
      
      if (audioExists && metadataExists) {
        const stats = fs.statSync(audioPath);
        const sizeKB = (stats.size / 1024).toFixed(1);
        console.log(`  ✓ ${phrase.id}.wav (${sizeKB}KB)`);
      } else {
        console.log(`  ✗ ${phrase.id}.wav - ${audioExists ? 'metadata missing' : 'audio missing'}`);
        allFilesExist = false;
      }
    }
    console.log('');
  }
  
  return allFilesExist;
}

// Main execution
if (require.main === module) {
  const command = process.argv[2];
  
  if (command === 'verify') {
    verifyAudioFiles();
  } else {
    generateAudioFixtures()
      .then(() => verifyAudioFiles())
      .catch(console.error);
  }
}

module.exports = { testPhrases, generateAudioFixtures };