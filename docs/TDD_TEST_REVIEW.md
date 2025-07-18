# Test Suite Review Report (TDD Approach)

This document presents a high-level review of the existing test suites (unit, integration, and end-to-end) across the project, identifies gaps, and outlines recommendations for a comprehensive Test-Driven Development (TDD) strategy going forward.

---

## 1. Overview of Current Test Coverage

- **Backend Unit Tests** (`backend/tests/`): tests for prompt loader, audio utilities, session manager, CBT assistant, greeting and summary agents.  
- **Frontend Unit Tests** (`frontend/lib/.../__tests__`, `frontend/components/.../__tests__`): tests for API client, audio utilities, streaming utilities, UI components, and React hooks.
- **End-to-End (E2E) Tests** (`tests/e2e/`): Playwright and pytest-based scenarios covering session persistence, SSE heartbeat, conversation flow, text reframing, timeout behaviors, and full workflow.

## 2. Identified Gaps and Recommendations

### 2.1 Backend: Missing or Incomplete Tests

| Area                         | Status                   | Recommendation                                    |
|------------------------------|--------------------------|---------------------------------------------------|
| Orchestrator & Phase Manager | No unit tests present    | Add unit tests for `orchestrator.py` and `phase_manager.py` to verify phase transitions and agent coordination.  |
| Discovery/Parser Agents      | Limited coverage         | Cover parsing logic and edge cases for discovery and parser agents (`discovery_agent.py`, `parser_agent.py`).     |
| Speech-to-Text / TTS Services | No mocks/tests for I/O   | Introduce mocks or fakes for external STT/TTS services to validate audio pipeline behaviors (`speech_to_text.py`, `text_to_speech.py`). |
| PDF Generation & Download     | No tests                 | Add tests for PDF generation (`pdf_generator.py`) and download utilities to ensure document outputs meet expected formats. |
| Crisis Detection & Safety     | No unit tests            | Cover `crisis_detection.py` and `safety_response.py` to verify alerting logic and fallback responses.    |
| Localization & Resources      | No tests                 | Add tests for `language_detection.py`, `localization.py`, and resource loaders to validate locale fallback and file handling. |

### 2.2 Frontend: Coverage Gaps

| Area                          | Status                        | Recommendation                                    |
|-------------------------------|-------------------------------|---------------------------------------------------|
| Pages & Routing (app/**)      | No unit tests for Next.js pages | Add snapshot and behavioral tests for pages (`page.tsx`) to verify layout and data fetching during SSR/SSG. |
| Theme & Context               | Limited tests                | Expand tests for `ThemeContext` and `ThemeToggle` to cover dark/light mode persistence and UI updates. |
| Conversation Hooks            | Partial coverage             | Add tests for `useConversation` and `useNaturalConversation` hooks including error and edge scenarios. |
| Forms & User Input            | Partial tests                | Cover form validation and submission flows in `ThoughtInputForm` and other forms.                     |
| API Error Handling            | Missing negative tests       | Test error states in `client.ts`, `errors.ts`, and UI error boundaries (`ErrorFallback`).              |

### 2.3 End-to-End Tests: Extending Scenarios

- **Error & Recovery Flows**: simulate network failures, SSE disconnects, or invalid payloads to verify client reconnection and error messaging.  
- **Long-running Sessions**: test multi-turn conversations beyond basic happy paths, including session storage across reloads and timeouts.  
- **Accessibility & UI Responsiveness**: integrate basic accessibility checks (e.g. ARIA attributes) and verify UI on varying viewports.  

**Implementation Steps:**
- Use Playwright's built-in accessibility snapshot (`expect(page).toHaveNoAccessibilityViolations()` with axe-core).
- In E2E tests, call `page.setViewportSize({ width, height })` for mobile/desktop contexts and assert responsive layout via CSS selectors.

## 3. Test Quality and Best Practices

- **Avoid Flaky Patterns**: replace arbitrary sleeps/timeouts with event-driven waits or fixtures.  
- **Use Mocks and Fakes Strategically**: isolate external dependencies (APIs, cloud services, audio devices) to enable reliable unit tests and CI friendliness.  
- **Consistent Assertions**: ensure each test asserts on both success and error outcomes, and cleans up side effects.  
- **Maintain Test Data**: centralize fixtures and test data definitions to reduce duplication and simplify updates.

## 4. Roadmap for TDD-Driven Development

1. **Define Behavior First**: for each new feature or module, write a test specification (BDD-style) in parallel with user stories.  
2. **Red–Green–Refactor Cycle**: implement failing tests, make them pass with minimal code changes, then refactor with confidence.  
3. **Coverage Gates**: enforce minimum coverage thresholds on critical modules using CI (e.g. `coverage.py`, Jest coverage).  
4. **Documentation Alignment**: keep E2E and integration guides (e.g. in `docs/`) in sync with updated test scenarios.  


---

_This report is intended as a living document. As the codebase and requirements evolve, revisit and expand the test plan to maintain reliability and accelerate future development._
#### 2.1.1 Orchestrator & Phase Manager

**Implementation Steps:**
- Parametrize pytest cases for `PhaseManager.next()` in `backend/src/agents/phase_manager.py` to cover all valid phase transitions and invalid inputs.
- Use `unittest.mock` or `pytest-mock` to stub out downstream agent calls in `backend/src/agents/orchestrator.py`, asserting that each phase triggers the expected agent method.

#### 2.1.2 Discovery & Parser Agents

**Implementation Steps:**
- Create pytest fixtures for sample user inputs and conversation histories in `tests/fixtures/` and verify output shape and error handling in `discovery_agent.py` and `parser_agent.py`.

#### 2.1.3 Speech-to-Text / TTS Services

**Implementation Steps:**
- Monkeypatch external API clients in `speech_to_text.py` and `text_to_speech.py` to simulate HTTP failures and rate limiting, verifying retry logic and exception propagation.

#### 2.1.4 PDF Generation & Download

**Implementation Steps:**
- Use pytest's `tmp_path` to generate files via `pdf_generator.py`, then open with PyPDF2 to assert author metadata and page count.

#### 2.1.5 Crisis Detection & Safety

**Implementation Steps:**
- Parametrize input sentences to `crisis_detection.detect()` for edge thresholds, and assert `safety_response.respond()` returns safe fallback messages without raising.

#### 2.1.6 Localization & Resources

**Implementation Steps:**
- Test `prompt_loader.load_prompts()` with missing locale files and invalid markdown, verifying fallback to default language and error logging.

#### 2.2.1 Pages & Routing

**Implementation Steps:**
- Leverage Jest and React Testing Library to snapshot render each Next.js page under `frontend/app/*/page.tsx`, mocking fetch calls via `jest-fetch-mock`.

#### 2.2.2 Theme & Context

**Implementation Steps:**
- Use `renderHook` from `@testing-library/react-hooks` to toggle theme in `ThemeContext` and assert changes persisted to `localStorage`.

#### 2.2.3 Conversation Hooks

**Implementation Steps:**
- Stub global `EventSource` in Jest tests for `useConversation`, pushing synthetic messages and error events to simulate SSE streams.

#### 2.2.4 Forms & User Input

**Implementation Steps:**
- Simulate user typing and form submission in `ThoughtInputForm.test.tsx`, asserting validation errors and callback invocations.

#### 2.2.5 API Error Handling

**Implementation Steps:**
- Mock failed fetch responses in `client.ts` tests and render `ErrorFallback` to confirm error UI displays correct status and message.
