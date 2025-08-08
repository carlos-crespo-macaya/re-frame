Title: Secret Leak – Findings and Remediation Status (2025-08-08)

Overview
- Scans executed: Gitleaks (history + filesystem), TruffleHog (history + filesystem, plus verified-only filesystem).
- Reports: `infra/gcp/security/reports/`

Key Findings (redacted)
- Gitleaks – history (SARIF): 2 results
  - `test.py` (commit 5785720… by Carlos Crespo): rule `generic-api-key`.
  - `backend/tests/test_audio_security.py` (commit c488bbb…): rule `generic-api-key`.

- Gitleaks – working tree (JSON): multiple entries, notably
  - `.env`: `OPENROUTER_API_KEY`, `OPENAI_API_KEY`, `XAI_API_KEY`, and GCP API keys (local only; `.env` is ignored by git).
  - `.claude/settings.local.json`: private-key-like material (local tool config; not tracked).
  - `frontend/.next/**`: Next.js preview/encryption keys inside build artifacts (ignored by git).
  - `reframe_diag_20250808_225656/run_re-frame-backend.yaml`: GCP API key-like value inside diagnostic export (this directory is ignored from git by `.gitignore: infra/`).

- TruffleHog – filesystem (verified-only)
  - Verified xAI key format detected in `.env` at line 26.

- TruffleHog – git history
  - Unverified hits only; no verified secrets in history for current HEAD per tool summary.

Risk Assessment
- Highest risk: Any secrets committed in history (2 gitleaks SARIF hits). These require rotation at source and history rewrite to ensure removal from all commits.
- Local-only artifacts: `.env`, `.next/**`, `.claude/**`, `backend/.venv/**`, and `reframe_diag_*/` contain secrets but are ignored from git; ensure they never get committed. Keep them out of archives and PR attachments.

Remediation Plan & Status
1) Rotate credentials (Action: required by owners)
   - Rotate any keys that were committed historically (generic API key in `test.py` and `backend/tests/test_audio_security.py`).
   - Rotate `.env`-resident keys if they match committed values or were ever shared.
   - Rotate any Google API key exposed in diag output before sharing externally.

2) Purge from history (Prepared)
   - Use BFG with `--delete-files` for sensitive patterns and `--replace-text` using regexes for API key formats.
   - Force-push rewritten history. Requires repo admin access and coordination.

3) Working tree cleanup (To apply after rewrite)
   - Ensure `.env`, `.env.*`, key files, and similar are removed from the index and added to `.gitignore`.
   - Keep `.env.example` with placeholders only.

4) Guardrails (In progress)
   - Add gitleaks pre-commit hook to `backend/.pre-commit-config.yaml`.
   - Optional CI job for gitleaks with `fetch-depth: 0`.

Conclusion
- Findings indicate 2 historical secrets and several local-only secrets in ignored files and build artifacts.
- With rotation plus history purge, the repository can be considered remediated. Remaining risk depends on timely rotation and the force-push of the rewritten history.

Appendix – References
- `gitleaks.sarif` – 2 results (history)
- `gitleaks-fs.json` – working tree findings
- `trufflehog-git.json` – unverified secrets in history
- `trufflehog-fs.json` – many candidates, including binaries (noise)
- `trufflehog-fs-verified.json` – verified xAI key in `.env`
