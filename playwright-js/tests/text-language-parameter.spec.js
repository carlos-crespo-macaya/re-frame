const { test, expect } = require('@playwright/test');

test.describe('Language Parameter E2E Tests', () => {
  test.setTimeout(60000); // 60 second timeout

  test('should respect language parameter for Spanish conversation', async ({ page }) => {
    // Navigate to the application
    await page.goto('http://localhost:3000');
    
    // Start a Spanish conversation
    await page.fill('[data-testid="chat-input"]', 'Hola, necesito ayuda con mis pensamientos');
    
    // Intercept the SSE request to verify language parameter
    const ssePromise = page.waitForRequest(request => {
      const url = request.url();
      return url.includes('/api/events') && url.includes('language=es-ES');
    });
    
    // Send the message
    await page.click('[data-testid="send-button"]');
    
    // Wait for SSE request with language parameter
    const sseRequest = await ssePromise;
    expect(sseRequest.url()).toContain('language=es-ES');
    
    // Wait for Spanish response
    await page.waitForSelector('text=/Hola.*Estoy aquí para ayudarte/', {
      timeout: 30000
    });
    
    // Verify the greeting is in Spanish
    const greetingText = await page.textContent('[data-testid="message-0"]');
    expect(greetingText).toContain('Hola');
    expect(greetingText).toContain('ayudarte');
    expect(greetingText).toMatch(/reencuadre|cognitivo|CBT/);
  });

  test('should respect language parameter for Portuguese conversation', async ({ page }) => {
    await page.goto('http://localhost:3000');
    
    // Start a Portuguese conversation
    await page.fill('[data-testid="chat-input"]', 'Olá, preciso de ajuda com meus pensamentos');
    
    // Intercept the SSE request
    const ssePromise = page.waitForRequest(request => {
      const url = request.url();
      return url.includes('/api/events') && url.includes('language=pt-BR');
    });
    
    await page.click('[data-testid="send-button"]');
    
    // Verify language parameter
    const sseRequest = await ssePromise;
    expect(sseRequest.url()).toContain('language=pt-BR');
    
    // Wait for Portuguese response
    await page.waitForSelector('text=/Olá.*Estou aqui para ajudar/', {
      timeout: 30000
    });
    
    const greetingText = await page.textContent('[data-testid="message-0"]');
    expect(greetingText).toContain('Olá');
    expect(greetingText).toContain('ajudar');
  });

  test('should respect language parameter for German conversation', async ({ page }) => {
    await page.goto('http://localhost:3000');
    
    // Start a German conversation
    await page.fill('[data-testid="chat-input"]', 'Hallo, ich brauche Hilfe mit meinen Gedanken');
    
    const ssePromise = page.waitForRequest(request => {
      const url = request.url();
      return url.includes('/api/events') && url.includes('language=de-DE');
    });
    
    await page.click('[data-testid="send-button"]');
    
    const sseRequest = await ssePromise;
    expect(sseRequest.url()).toContain('language=de-DE');
    
    // Wait for German response
    await page.waitForSelector('text=/Hallo.*Ich bin hier/', {
      timeout: 30000
    });
    
    const greetingText = await page.textContent('[data-testid="message-0"]');
    expect(greetingText).toContain('Hallo');
    expect(greetingText).toMatch(/helfen|unterstützen/);
  });

  test('should maintain language throughout conversation phases', async ({ page }) => {
    await page.goto('http://localhost:3000');
    
    // Start Spanish conversation
    await page.fill('[data-testid="chat-input"]', 'Hola, quiero trabajar en mis pensamientos');
    await page.click('[data-testid="send-button"]');
    
    // Wait for greeting in Spanish
    await page.waitForSelector('text=/Hola.*ayudarte/', { timeout: 30000 });
    
    // Move to discovery phase
    await page.fill('[data-testid="chat-input"]', 'Sí, estoy listo para comenzar');
    await page.click('[data-testid="send-button"]');
    
    // Wait for discovery response in Spanish
    await page.waitForSelector('text=/situación|pensamiento|sentimiento/', {
      timeout: 30000
    });
    
    // Provide a thought to explore
    await page.fill('[data-testid="chat-input"]', 'Creo que todos me juzgan cuando hablo en público');
    await page.click('[data-testid="send-button"]');
    
    // Verify response continues in Spanish
    await page.waitForSelector('text=/entiendo|comprendo/', {
      timeout: 30000
    });
    
    // Check that all responses are in Spanish
    const messages = await page.$$('[data-testid^="message-"]');
    for (const message of messages) {
      const text = await message.textContent();
      // Should not contain common English CBT terms
      expect(text).not.toMatch(/\b(thought|feeling|emotion|reframe)\b/i);
    }
  });

  test('should handle language normalization', async ({ page }) => {
    await page.goto('http://localhost:3000');
    
    // Test lowercase language code
    await page.evaluate(() => {
      // Override the language detection to return lowercase
      window.detectLanguage = () => 'es';
    });
    
    await page.fill('[data-testid="chat-input"]', 'hola');
    
    // Intercept normalized request
    const ssePromise = page.waitForRequest(request => {
      const url = request.url();
      return url.includes('/api/events') && url.includes('language=es-ES');
    });
    
    await page.click('[data-testid="send-button"]');
    
    // Should normalize to es-ES
    const sseRequest = await ssePromise;
    expect(sseRequest.url()).toContain('language=es-ES');
  });

  test('should fallback to English for unsupported languages', async ({ page }) => {
    await page.goto('http://localhost:3000');
    
    // Override language detection to return unsupported language
    await page.evaluate(() => {
      window.detectLanguage = () => 'klingon';
    });
    
    await page.fill('[data-testid="chat-input"]', 'Hello');
    
    const ssePromise = page.waitForRequest(request => {
      const url = request.url();
      return url.includes('/api/events') && url.includes('language=en-US');
    });
    
    await page.click('[data-testid="send-button"]');
    
    // Should fallback to en-US
    const sseRequest = await ssePromise;
    expect(sseRequest.url()).toContain('language=en-US');
    
    // Wait for English response
    await page.waitForSelector('text=/Hello.*here to help/', {
      timeout: 30000
    });
  });
});