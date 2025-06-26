# Testing Multilingual Support

## Quick Start

1. **Restart ADK Web** (to load new configuration):
```bash
cd /Users/carlos/workspace/re-frame/agentic_workflow
adk web
```

2. **Test Spanish Input**:
Type: "hola, tengo un problema, estoy auto aislandome"

Expected response from Maya in Spanish:
```
¡Hola! Soy Maya, tu compañera de reestructuración cognitiva. 🌱

Estoy aquí para ayudarte a explorar tus pensamientos y sentimientos usando técnicas de TCC basadas en evidencia. Nuestra sesión tendrá tres partes:

📝 **Fase de Descubrimiento** - Te haré algunas preguntas para entender lo que estás experimentando
🔍 **Fase de Reestructuración** - Examinaremos tus pensamientos juntos y encontraremos perspectivas más equilibradas
📄 **Fase de Resumen** - Crearé un resumen personalizado en PDF para que lo conserves

¿Listo para comenzar? ¿Qué tienes en mente hoy?
```

## Troubleshooting

If Maya responds in English instead of Spanish:

1. **Check logs for language detection**:
   - Look for "Detected language:" in the console
   - Should show "español" with confidence score

2. **Verify Google Cloud credentials**:
   ```bash
   echo $GOOGLE_APPLICATION_CREDENTIALS
   # OR
   gcloud auth application-default print-access-token
   ```

3. **Check if Translation API is enabled**:
   ```bash
   gcloud services list --enabled | grep translate
   ```

## What Changed

The logs showed `maya_context_agent` was being used, but we've now updated all configuration files to use `MayaMultilingualAgent` which includes:

1. Google Cloud Translation API for detection
2. Multilingual greetings and responses
3. Language-specific PDF generation

## Test Other Languages

Once Spanish works, try:
- English: "Hello, I'm feeling isolated"
- French: "Bonjour, je me sens isolé"
- Italian: "Ciao, mi sto isolando"
- Portuguese: "Olá, estou me isolando"
- Catalan: "Hola, m'estic aïllant"