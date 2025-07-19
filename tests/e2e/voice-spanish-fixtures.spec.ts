import { test, expect } from '@playwright/test';
import * as path from 'path';
import * as fs from 'fs';

test.describe('Spanish Voice Conversation with Pre-generated Audio', () => {
  const fixturesDir = path.join(__dirname, 'fixtures', 'audio', 'spanish');
  
  test.beforeEach(async ({ context }) => {
    // Grant microphone permissions
    await context.grantPermissions(['microphone']);
  });

  test('complete Spanish CBT conversation using audio fixtures', async ({ page }) => {
    // Define conversation flow with fixture files
    const conversationFlow = [
      {
        audioFile: 'es-greeting.wav',
        transcription: "Hola, me siento ansioso por una presentación que tengo en el trabajo",
        expectedKeywords: ['presentación', 'ansioso', 'ansiedad', 'entiendo', 'cuéntame']
      },
      {
        audioFile: 'es-thought-1.wav',
        transcription: "Sigo pensando que todos me van a juzgar y notarán todos mis errores",
        expectedKeywords: ['pensamientos', 'evidencia', 'perspectiva', 'juzgar']
      },
      {
        audioFile: 'es-insight.wav',
        transcription: "Tienes razón, creo que estoy asumiendo lo peor sin evidencia real",
        expectedKeywords: ['reformular', 'útil', 'positivo', 'preparado']
      },
      {
        audioFile: 'es-conclusion.wav',
        transcription: "Gracias, me siento más confiado ahora y listo para prepararme adecuadamente",
        expectedKeywords: ['excelente', 'progreso', 'estrategias', 'recuerda']
      }
    ];

    // Mock MediaRecorder to use our pre-generated audio files
    await page.addInitScript((audioFixtures) => {
      window.audioFixtures = audioFixtures;
      window.currentFixtureIndex = 0;
      
      // Override MediaRecorder
      window.MediaRecorder = class MockMediaRecorder {
        constructor(stream, options) {
          this.stream = stream;
          this.options = options;
          this.state = 'inactive';
          this.chunks = [];
        }
        
        async start() {
          this.state = 'recording';
          
          // Load the current audio fixture
          const fixture = window.audioFixtures[window.currentFixtureIndex];
          if (fixture && fixture.audioData) {
            setTimeout(() => {
              if (this.state === 'recording') {
                // Convert base64 to blob
                const binaryString = atob(fixture.audioData);
                const bytes = new Uint8Array(binaryString.length);
                for (let i = 0; i < binaryString.length; i++) {
                  bytes[i] = binaryString.charCodeAt(i);
                }
                
                const blob = new Blob([bytes], { type: 'audio/wav' });
                this.chunks.push(blob);
                
                if (this.ondataavailable) {
                  this.ondataavailable({ data: blob });
                }
              }
            }, 1500); // Simulate recording delay
          }
        }
        
        stop() {
          this.state = 'inactive';
          window.currentFixtureIndex++;
          
          setTimeout(() => {
            if (this.onstop) {
              this.onstop();
            }
          }, 100);
        }
      };
    }, await loadAudioFixtures(conversationFlow));

    await page.goto('/');
    
    // Wait for initial AI greeting (might be in Spanish if language detected)
    await expect(page.getByTestId('assistant-message')).toBeVisible({ timeout: 15000 });
    const greeting = await page.getByTestId('assistant-message').first().textContent();
    console.log('AI Greeting:', greeting);
    
    // Process each phrase
    for (const [index, flow] of conversationFlow.entries()) {
      console.log(`\n--- Procesando: ${flow.audioFile} ---`);
      
      // Click record button
      const recordButton = page.getByRole('button', { name: /start.*recording|microphone|micrófono|grabar/i });
      await recordButton.click();
      
      // Verify recording state
      await expect(page.getByRole('button', { name: /stop.*recording|recording|detener|grabando/i })).toBeVisible();
      const recordingIndicator = page.locator('[data-testid="recording-indicator"], .recording-active');
      await expect(recordingIndicator).toBeVisible();
      
      // Wait for "recording"
      await page.waitForTimeout(2000);
      
      // Stop recording
      await page.getByRole('button', { name: /stop.*recording|recording|detener|grabando/i }).click();
      
      // Wait for the transcription to appear
      await expect(page.getByText(flow.transcription)).toBeVisible({ timeout: 10000 });
      console.log('Mensaje del usuario:', flow.transcription);
      
      // Wait for AI response
      const expectedMessageCount = index + 2; // Initial greeting + responses
      await expect(page.getByTestId('assistant-message')).toHaveCount(expectedMessageCount, { 
        timeout: 30000 
      });
      
      // Get and verify AI response
      const aiResponse = await page.getByTestId('assistant-message').last().textContent();
      console.log('Respuesta IA:', aiResponse?.substring(0, 100) + '...');
      
      // Check for expected keywords in response (AI might respond in Spanish)
      const responseText = aiResponse?.toLowerCase() || '';
      const hasExpectedContent = flow.expectedKeywords.some(keyword => 
        responseText.includes(keyword.toLowerCase())
      );
      
      // If not found in Spanish, check for English keywords as fallback
      if (!hasExpectedContent) {
        const englishKeywords = {
          'presentación': ['presentation'],
          'ansioso': ['anxious', 'anxiety'],
          'pensamientos': ['thoughts'],
          'evidencia': ['evidence'],
          'perspectiva': ['perspective'],
          'juzgar': ['judge'],
          'reformular': ['reframe'],
          'útil': ['helpful'],
          'positivo': ['positive'],
          'preparado': ['prepared']
        };
        
        const hasEnglishContent = flow.expectedKeywords.some(keyword => {
          const englishEquivalents = englishKeywords[keyword] || [];
          return englishEquivalents.some(eng => responseText.includes(eng));
        });
        
        expect(hasExpectedContent || hasEnglishContent).toBeTruthy();
      }
      
      // Check if audio playback is available
      const lastMessage = page.getByTestId('assistant-message').last();
      const playButton = lastMessage.getByRole('button', { name: /play|audio|reproducir/i });
      
      if (await playButton.count() > 0) {
        console.log('Audio disponible para la respuesta');
      }
      
      // Small delay between interactions
      await page.waitForTimeout(1000);
    }
    
    // Verify complete conversation
    const totalMessages = await page.getByTestId('message-bubble').count();
    expect(totalMessages).toBe(9); // 1 greeting + 4 user + 4 assistant
    
    console.log('\n✅ Conversación en español completada exitosamente!');
  });

  test('handles Spanish alternative scenario', async ({ page }) => {
    // Use one of the existing Spanish fixtures for an alternative test
    const fixture = {
      audioFile: 'es-thought-1.wav',
      transcription: "Sigo pensando que todos me van a juzgar y notarán todos mis errores",
      expectedKeywords: ['pensar', 'juzgar', 'errores', 'preocupación', 'ansiedad']
    };

    await page.addInitScript((audioFixture) => {
      window.audioFixtures = [audioFixture];
      window.currentFixtureIndex = 0;
    }, await loadAudioFixtures([fixture]));

    await page.goto('/');
    
    // Wait for greeting
    await expect(page.getByTestId('assistant-message')).toBeVisible({ timeout: 15000 });
    
    // Send audio
    const recordButton = page.getByRole('button', { name: /start.*recording|microphone|micrófono|grabar/i });
    await recordButton.click();
    await page.waitForTimeout(2000);
    await page.getByRole('button', { name: /stop.*recording|recording|detener|grabando/i }).click();
    
    // Verify response addresses the concern
    await expect(page.getByTestId('assistant-message')).toHaveCount(2, { timeout: 30000 });
    const response = await page.getByTestId('assistant-message').last().textContent();
    
    const hasRelevantContent = fixture.expectedKeywords.some(keyword =>
      response?.toLowerCase().includes(keyword)
    ) || response?.toLowerCase().match(/(think|judge|error|worry|anxiety)/);
    
    expect(hasRelevantContent).toBeTruthy();
  });

  test('language switching between Spanish and English', async ({ page }) => {
    // Start with Spanish
    const spanishFixture = {
      audioFile: 'es-greeting.wav',
      transcription: "Hola, me siento ansioso por una presentación que tengo en el trabajo"
    };

    await page.addInitScript((audioFixture) => {
      window.audioFixtures = [audioFixture];
      window.currentFixtureIndex = 0;
    }, await loadAudioFixtures([spanishFixture]));

    await page.goto('/');
    
    // Wait for greeting
    await expect(page.getByTestId('assistant-message')).toBeVisible({ timeout: 15000 });
    
    // Send Spanish voice message
    const recordButton = page.getByRole('button', { name: /start.*recording|microphone|micrófono|grabar/i });
    await recordButton.click();
    await page.waitForTimeout(2000);
    await page.getByRole('button', { name: /stop.*recording|recording|detener|grabando/i }).click();
    
    // Wait for response (might be in Spanish)
    await expect(page.getByTestId('assistant-message')).toHaveCount(2, { timeout: 30000 });
    
    // Now switch to English text
    const thoughtInput = page.getByPlaceholder(/share.*thought|comparte.*pensamiento/i);
    await thoughtInput.fill("Actually, let me continue in English. What techniques can help with presentations?");
    await page.getByRole('button', { name: /send|enviar/i }).click();
    
    // Verify English message appears
    await expect(page.getByText("Actually, let me continue in English")).toBeVisible();
    
    // Wait for AI response (should adapt to English)
    await expect(page.getByTestId('assistant-message')).toHaveCount(3, { timeout: 30000 });
    
    // Verify response is relevant
    const lastResponse = await page.getByTestId('assistant-message').last().textContent();
    expect(lastResponse?.toLowerCase()).toMatch(/(technique|presentation|practice|prepare)/);
  });
});

// Helper function to load audio fixtures as base64
async function loadAudioFixtures(flows: Array<{audioFile: string, transcription: string}>) {
  const fixturesDir = path.join(__dirname, 'fixtures', 'audio', 'spanish');
  const fixtures = [];
  
  for (const flow of flows) {
    const audioPath = path.join(fixturesDir, flow.audioFile);
    let audioData = '';
    
    // Check if file exists, if not create a placeholder
    if (fs.existsSync(audioPath)) {
      const audioBuffer = fs.readFileSync(audioPath);
      audioData = audioBuffer.toString('base64');
    } else {
      console.warn(`Audio fixture not found: ${audioPath}`);
      // Create a simple placeholder audio
      audioData = createPlaceholderAudio();
    }
    
    fixtures.push({
      audioFile: flow.audioFile,
      transcription: flow.transcription,
      audioData
    });
  }
  
  return fixtures;
}

// Create placeholder audio data if fixture doesn't exist
function createPlaceholderAudio(): string {
  const sampleRate = 16000;
  const duration = 2;
  const numSamples = sampleRate * duration;
  
  const header = Buffer.alloc(44);
  header.write('RIFF', 0);
  header.writeUInt32LE(36 + numSamples * 2, 4);
  header.write('WAVE', 8);
  header.write('fmt ', 12);
  header.writeUInt32LE(16, 16);
  header.writeUInt16LE(1, 20);
  header.writeUInt16LE(1, 22);
  header.writeUInt32LE(sampleRate, 24);
  header.writeUInt32LE(sampleRate * 2, 28);
  header.writeUInt16LE(2, 32);
  header.writeUInt16LE(16, 34);
  header.write('data', 36);
  header.writeUInt32LE(numSamples * 2, 40);
  
  const audioData = Buffer.alloc(numSamples * 2);
  for (let i = 0; i < numSamples; i++) {
    const sample = Math.sin(2 * Math.PI * 440 * i / sampleRate) * 0.3;
    audioData.writeInt16LE(Math.floor(sample * 32767), i * 2);
  }
  
  return Buffer.concat([header, audioData]).toString('base64');
}