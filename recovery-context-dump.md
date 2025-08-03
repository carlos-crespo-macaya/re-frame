# Recovery Plan: Lost i18n and Chat Interface Features

## Executive Summary
During recent merges (within last 2 days), the re-frame project lost two critical features:
1. **Internationalization (i18n)** - Full multi-language support with next-intl
2. **Chat Interface** - Real-time chat UI replacing current form-based interface

These features were added in commit 57857207 ([ALL-010]) on the feature/FE-008-i18n-support branch but are missing from the current codebase.

## Current Status
- **Recovery Branch Created**: `recovery/i18n-and-chat-features`
- **Files Recovered**: ChatClient component and chat page wrapper
- **Blocking Issues**: TypeScript errors in recovered files need fixing

## Technical Context

### Repository Structure
```
re-frame/
├── frontend/          # Next.js 14 frontend application
│   ├── app/          # App Router pages
│   ├── components/   # React components
│   ├── lib/          # Core functionality
│   └── locales/      # Translation files (TO BE RECOVERED)
├── backend/          # FastAPI backend with ADK
└── docker-compose.yml
```

### Technology Stack
- **Frontend**: Next.js 14 with App Router, TypeScript, Tailwind CSS
- **Backend**: FastAPI with Google's Agent Development Kit (ADK)
- **Real-time**: Server-Sent Events (SSE) for streaming
- **Audio**: Web Audio API with AudioWorklets
- **Package Manager**: pnpm (frontend), uv (backend)

## Lost Features Analysis

### 1. Internationalization (i18n)
The lost implementation included:
- **next-intl** integration for translations
- **Dynamic [locale] routing** (`/en/`, `/es/`)
- **Middleware** for automatic locale detection
- **Translation files** in `/frontend/locales/`
- **Localized page wrappers** for all routes

### 2. Chat Interface
The lost implementation included:
- **ChatClient component** with real-time messaging
- **Message bubbles** UI with role-based styling
- **Markdown rendering** for formatted responses
- **Auto-scrolling** chat view
- **SSE integration** for streaming responses

## Files to Recover

### Priority 1: Core i18n Infrastructure
1. `/frontend/middleware.ts` - Locale detection and routing ✓ (EXISTS)
2. `/frontend/i18n.ts` - next-intl configuration
3. `/frontend/i18n/routing.ts` - Navigation wrappers
4. `/frontend/next.config.js` - Update for i18n support

### Priority 2: Localized Routes
1. `/frontend/app/[locale]/layout.tsx` - Locale-aware layout
2. `/frontend/app/[locale]/page.tsx` - Localized home page
3. `/frontend/app/[locale]/chat/page.tsx` - Chat page wrapper ✓ (RECOVERED)
4. `/frontend/app/[locale]/chat/chat-client.tsx` - Chat component ✓ (RECOVERED WITH ERRORS)

### Priority 3: Translation Files
```
/frontend/locales/
├── en/
│   ├── common.json
│   ├── home.json
│   ├── reframe.json
│   └── errors.json
└── es/
    ├── common.json
    ├── home.json
    ├── reframe.json
    └── errors.json
```

### Priority 4: Page Wrappers
1. `/frontend/app/about/page.tsx` - Redirect wrapper
2. `/frontend/app/learn-cbt/page.tsx` - Redirect wrapper
3. `/frontend/app/privacy/page.tsx` - Redirect wrapper
4. `/frontend/app/support/page.tsx` - Redirect wrapper
5. `/frontend/app/page.tsx` - Root redirect to /en

## Current Errors to Fix

### ChatClient TypeScript Errors
```typescript
// Line 27: 't' implicitly has type 'any'
const t = {
  en: { /* ... */ },
  es: { /* ... */ }
}[locale as keyof typeof t] || t.en  // ERROR: circular reference

// Line 225: 'onKeyPress' is deprecated
onKeyPress={handleKeyPress}  // Should use onKeyDown

// Lines 158, 231: Button missing type attribute
<button onClick={handleBack}>  // Should have type="button"
```

## Step-by-Step Recovery Plan

### Phase 1: Fix Current Errors
1. Fix TypeScript errors in ChatClient component
2. Update deprecated event handlers
3. Add missing button type attributes

### Phase 2: Recover i18n Infrastructure
1. Create `/frontend/i18n.ts` with next-intl configuration
2. Create `/frontend/i18n/routing.ts` with navigation wrappers
3. Update `/frontend/next.config.js` for i18n support
4. Verify middleware.ts integration

### Phase 3: Implement Localized Routing
1. Create `/frontend/app/[locale]/layout.tsx`
2. Create `/frontend/app/[locale]/page.tsx` with proper translations
3. Create redirect wrappers for all static pages
4. Update root page.tsx to redirect to /en

### Phase 4: Add Translation Files
1. Create locales directory structure
2. Add English translations (en/*.json)
3. Add Spanish translations (es/*.json)
4. Test translation loading

### Phase 5: Integration Testing
1. Test locale detection and routing
2. Verify chat interface functionality
3. Test SSE streaming in both locales
4. Ensure audio mode works with i18n
5. Verify form interface still works

### Phase 6: Merge Strategy
1. Keep both chat and form interfaces accessible
2. Add navigation between interfaces
3. Preserve all current functionality
4. Ensure no regression in audio features

## Implementation Commands

### Fix TypeScript Errors
```bash
cd frontend

# Fix the ChatClient component
# 1. Properly type translations
# 2. Replace onKeyPress with onKeyDown
# 3. Add type="button" to buttons
```

### Recover Files from Commit
```bash
# Already on recovery/i18n-and-chat-features branch
git show 57857207:frontend/i18n.ts > frontend/i18n.ts
git show 57857207:frontend/i18n/routing.ts > frontend/i18n/routing.ts
git show 57857207:frontend/app/[locale]/layout.tsx > frontend/app/[locale]/layout.tsx
# ... continue for all files
```

### Install Dependencies
```bash
cd frontend
pnpm add next-intl
```

### Update Configuration
```javascript
// frontend/next.config.js
const createNextIntlPlugin = require('next-intl/plugin')
const withNextIntl = createNextIntlPlugin()

module.exports = withNextIntl({
  // existing config
})
```

## Validation Checklist

- [ ] ChatClient component renders without errors
- [ ] Locale detection works correctly
- [ ] Routes redirect to locale-prefixed paths
- [ ] Translations load properly
- [ ] Chat interface functions with SSE
- [ ] Form interface remains accessible
- [ ] Audio mode works in both interfaces
- [ ] No regression in existing features
- [ ] All tests pass
- [ ] TypeScript compilation succeeds

## Current Working Directory
`/Users/carlos/workspace/re-frame`

## Current Branch
`recovery/i18n-and-chat-features`

## Next Immediate Action
Fix the TypeScript errors in `/frontend/app/[locale]/chat/chat-client.tsx`:
1. Fix the circular reference in translation object typing
2. Replace deprecated onKeyPress with onKeyDown
3. Add type="button" to button elements

## Notes for Sonnet Agent
- The user wants "the best of one and the best of the other" - integrate both features
- Don't lose current functionality while adding recovered features
- The chat interface should coexist with the form interface
- Maintain all audio functionality
- Follow the project's strict coding standards (see CLAUDE.md)
- Run quality checks: `cd frontend && pnpm run lint && pnpm run typecheck`