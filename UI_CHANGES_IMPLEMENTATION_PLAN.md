# UI Changes Implementation Plan

## Overview
This document outlines UI/UX improvements to be implemented across the re-frame application. Changes are organized for parallel execution where possible.

## Parallel Execution Groups

### Group A: Interface & UI Components (Can be done in parallel)
- **Change 1**: Interface selector text removal/modification
- **Change 2**: Button size optimization for mobile
- **Change 9**: Language selector dropdown improvements

### Group B: Support Section Updates (Can be done in parallel)
- **Change 3**: Crisis helpline resources update
- **Change 4**: AvPD resources replacement
- **Change 5**: Tech support section modifications

### Group C: Content Updates (Can be done in parallel)
- **Change 6**: About section modifications
- **Change 7**: Privacy policy updates
- **Change 8**: Date updates across the site

---

## Detailed Implementation Instructions

### Change 1: Interface Selector Text Removal
**Files to modify:**
- `frontend/locales/en/home.json`
- `frontend/locales/es/home.json`
- `frontend/app/[locale]/page.tsx` (if hardcoded)

**Actions:**
1. Locate the text "Choose Your Interface" and "Select how you'd like to interact with re-frame"
2. Remove these strings from both language files
3. Adjust spacing/padding in the component to maintain visual balance
4. Consider adding a subtle divider or visual element if needed for separation

**Alternative suggestion:** Replace with a simple, context-aware heading like "Get Started" or "Begin Your Session"

---

### Change 2: Button Size Optimization
**Files to modify:**
- `frontend/components/ui/Button.tsx`
- `frontend/app/[locale]/page.tsx` (interface cards)
- Related CSS/Tailwind classes

**Actions:**
1. Reduce button padding from current size (likely `px-8 py-4`) to `px-4 py-2` or `px-6 py-3`
2. Adjust font size if needed (from `text-lg` to `text-base`)
3. Optimize card layout for mobile:
   - Reduce overall card padding
   - Stack elements vertically on small screens
   - Use responsive classes: `sm:px-4 px-2`
4. Test on mobile viewport (375px width minimum)

---

### Change 3: Crisis Helpline Resources Update
**Files to modify:**
- `frontend/locales/en/support.json`
- `frontend/locales/es/support.json`
- `frontend/app/[locale]/support/page.tsx`

**English content to add:**
```json
{
  "crisis": {
    "title": "Need to talk right now?",
    "resources": [
      {
        "name": "Find a Helpline",
        "description": "Instant list of crisis numbers/text lines in your country",
        "url": "https://findahelpline.com"
      },
      {
        "name": "Befrienders Worldwide",
        "description": "Email or call volunteers in 90+ countries",
        "url": "https://befrienders.org"
      },
      {
        "name": "7 Cups",
        "description": "Free, anonymous 24/7 chat with trained listeners",
        "url": "https://7cups.com"
      }
    ]
  }
}
```

**Spanish content (maintaining app tone):**
```json
{
  "crisis": {
    "title": "¿Necesitas hablar ahora mismo?",
    "resources": [
      {
        "name": "Find a Helpline",
        "description": "Lista instantánea de números de crisis y líneas de texto en tu país",
        "url": "https://findahelpline.com"
      },
      {
        "name": "Befrienders Worldwide",
        "description": "Correo o llamada con voluntarios en más de 90 países",
        "url": "https://befrienders.org"
      },
      {
        "name": "7 Cups",
        "description": "Chat gratuito y anónimo 24/7 con oyentes capacitados",
        "url": "https://7cups.com"
      }
    ]
  }
}
```

**Actions:**
1. Remove all local phone numbers and references
2. Implement clickable green text using `<a>` tags with existing green color classes
3. Ensure links open in new tab: `target="_blank" rel="noopener noreferrer"`

---

### Change 4: AvPD Resources Replacement
**Files to modify:**
- `frontend/locales/en/support.json`
- `frontend/locales/es/support.json`

**English content:**
```json
{
  "avpd_resources": {
    "title": "About Avoidant Personality Disorder",
    "subtitle": "What you'll find",
    "resources": [
      {
        "name": "Cleveland Clinic",
        "description": "Plain-language overview, diagnostic criteria, and the psychotherapy/medication options most often used.",
        "url": "https://my.clevelandclinic.org/health/diseases/9761-avoidant-personality-disorder"
      },
      {
        "name": "StatPearls / NCBI Bookshelf",
        "description": "More clinical depth (for people who like DSM criteria, prevalence data, and therapeutic evidence).",
        "url": "https://www.ncbi.nlm.nih.gov/books/NBK559325/"
      },
      {
        "name": "Psych Central",
        "description": "Accessible article that walks through symptoms, real-world impact, and what to expect in therapy.",
        "url": "https://psychcentral.com/disorders/avoidant-personality-disorder"
      }
    ]
  }
}
```

**Spanish content (adapted):**
```json
{
  "avpd_resources": {
    "title": "Sobre el Trastorno de Personalidad Evitativa",
    "subtitle": "Lo que encontrarás",
    "resources": [
      {
        "name": "Cleveland Clinic",
        "description": "Resumen en lenguaje sencillo, criterios diagnósticos y las opciones de psicoterapia/medicación más utilizadas.",
        "url": "https://my.clevelandclinic.org/health/diseases/9761-avoidant-personality-disorder"
      },
      {
        "name": "StatPearls / NCBI Bookshelf",
        "description": "Mayor profundidad clínica (para quienes buscan criterios DSM, datos de prevalencia y evidencia terapéutica).",
        "url": "https://www.ncbi.nlm.nih.gov/books/NBK559325/"
      },
      {
        "name": "Psych Central",
        "description": "Artículo accesible sobre síntomas, impacto en la vida real y qué esperar en terapia.",
        "url": "https://psychcentral.com/disorders/avoidant-personality-disorder"
      }
    ]
  }
}
```

---

### Change 5: Tech Support Section Modifications
**Files to modify:**
- `frontend/locales/en/support.json`
- `frontend/locales/es/support.json`

**English updates:**
- Title: "Technical Support" → "Tech Support & Feedback"
- Subtitle: Adjust to cover both technical issues and feedback
- Response time: "24-48 hours" → "as soon as possible"
- Remove the last line about response times

**Spanish updates:**
- Title: "Soporte Técnico" → "Soporte Técnico y Comentarios"
- Subtitle: Adjust similarly
- Response time: "24-48 horas" → "lo antes posible"

---

### Change 6: About Section Modifications
**Files to modify:**
- `frontend/locales/en/about.json`
- `frontend/locales/es/about.json`
- `frontend/app/[locale]/about/page.tsx`

**Actions:**
1. **Remove sections:**
   - "The Why" opensource section
   - "Roadmap" section

2. **Add Thank You section:**
   ```json
   {
     "thankYou": {
       "title": "Thank You",
       "content": "Thank you for trying re-frame. We hope it helps you in some way on your journey."
     }
   }
   ```
   Spanish:
   ```json
   {
     "thankYou": {
       "title": "Gracias",
       "content": "Gracias por probar re-frame. Esperamos que te ayude de alguna manera en tu camino."
     }
   }
   ```

3. **Modify "Who builds it" section:**
   - Change title to something like "About the Creator" or "Behind re-frame"
   - Content: "Built with care by [Carlos Crespo](https://carlos-crespo.com/), hoping to contribute a small grain of sand to a topic that's personally important."
   - Spanish: "Creado con cariño por [Carlos Crespo](https://carlos-crespo.com/), esperando aportar un pequeño grano de arena en un tema que me es personalmente importante."

4. **Mission section:**
   - Remove: "without shame, ads, or data mining"
   - Replace with: "in a safe and supportive environment" or simply end the sentence before that phrase

---

### Change 7: Privacy Policy Updates
**Files to modify:**
- `frontend/locales/en/privacy.json`
- `frontend/locales/es/privacy.json`

**Changes:**
1. **Changes to this Policy section:**
   - Add: "The principle of privacy protection will not be affected by any changes."

2. **Data Retention section:**
   - Replace: "Conversation data is processed in real-time and not stored"
   - With: "Anonymized conversation data may be saved to help us learn how to improve and make this app more helpful. No personally identifiable information (PII) is ever stored."
   - Add: "Technical logs are maintained to help improve the platform's technical aspects."

3. **Data Collection section:**
   - Remove: "Conversations are not saved or recorded"
   - Replace with: "Anonymized conversations may be stored to learn how to best improve and make the app as helpful as possible. No PII is saved or recorded."
   - Remove: "Sessions are temporary and deleted after completion"

---

### Change 8: Date Updates
**Files to modify:**
- All files containing "January 2024" or "2024"
- Common locations:
  - `frontend/locales/*/privacy.json`
  - `frontend/locales/*/about.json`
  - Footer components

**Actions:**
- Replace "January 2024" → "August 2025"
- Replace "2024" → "2025"

---

### Change 9: Language Selector Optimization
**Files to modify:**
- `frontend/components/common/LanguageSelector.tsx` (or similar)
- Related CSS/Tailwind classes

**Actions:**
1. Reduce dropdown size (adjust padding/font-size)
2. Change label: "Select Language" → "Language"
3. Consider using a more compact design (icon + abbreviated lang code)
4. Ensure mobile responsiveness

---

## Testing Checklist

### Mobile Testing (Priority)
- [ ] Test all changes on 375px width (iPhone SE)
- [ ] Test on 390px width (iPhone 12/13)
- [ ] Test on tablet (768px)
- [ ] Verify touch targets are at least 44x44px

### Functionality Testing
- [ ] All links open correctly in new tabs
- [ ] Language switching works properly
- [ ] Feature flags still control interface display
- [ ] No broken translations

### Accessibility Testing
- [ ] Screen reader compatibility
- [ ] Keyboard navigation
- [ ] Color contrast (especially green links)

---

## Additional Suggestions

### 1. Interface Cards Enhancement
Instead of completely removing the interface selector text, consider:
- A subtle, contextual message based on enabled interfaces
- If only one interface: "Start your session"
- If multiple: "Choose your preferred way to connect"

### 2. Mobile-First Card Design
Consider implementing:
- Collapsible cards on mobile
- Swipeable carousel for interface selection
- Progressive disclosure (show details on tap/click)

### 3. Support Section Organization
Group resources by urgency:
- "Immediate Help" (crisis lines)
- "Learn More" (AvPD resources)
- "Get Support" (tech support/feedback)

### 4. Privacy Transparency
Add a simple visual indicator or badge showing:
- "No data tracking"
- "Privacy first"
- Link to full privacy policy

### 5. Loading States
Ensure smooth transitions when:
- Language changes
- Feature flags update
- External links are clicked

### 6. Feedback Mechanism
Consider adding:
- Quick feedback widget
- "Was this helpful?" prompts
- Anonymous usage analytics (with consent)

---

## Implementation Order

### Phase 1 (High Priority - User Experience)
1. Change 2: Button optimization (mobile usability)
2. Change 3: Crisis resources (safety critical)
3. Change 9: Language selector (immediate UX improvement)

### Phase 2 (Content Updates)
4. Change 4: AvPD resources
5. Change 5: Tech support section
6. Change 6: About section
7. Change 8: Date updates

### Phase 3 (Policy & Refinements)
8. Change 7: Privacy policy
9. Change 1: Interface selector text

---

## Notes for Implementation

- **Consistency**: Ensure tone and voice remain consistent across both languages
- **Testing**: Each change should be tested in both languages
- **Feature Flags**: Verify interface display logic still works after text changes
- **Git Commits**: Use atomic commits for each change group for easy rollback
- **PR Strategy**: Consider separate PRs for each group (A, B, C) for easier review

---

## Files Impact Summary

### Frontend Components
- `frontend/components/ui/Button.tsx`
- `frontend/components/common/LanguageSelector.tsx`

### Pages
- `frontend/app/[locale]/page.tsx`
- `frontend/app/[locale]/about/page.tsx`
- `frontend/app/[locale]/support/page.tsx`
- `frontend/app/[locale]/privacy/page.tsx`

### Translations
- `frontend/locales/en/*.json`
- `frontend/locales/es/*.json`

### Estimated Time
- Group A: 2-3 hours
- Group B: 2-3 hours
- Group C: 1-2 hours
- Testing: 2 hours
- **Total**: 7-10 hours