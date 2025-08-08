Title: Secret Leak Remediation – Executed Process (2025-08-08)

Scope
- Repo: macayaven/re-frame
- Host OS: macOS (Homebrew-managed tooling)
- Outputs: reports saved under `infra/gcp/security/reports/`

Tools Installed
- gitleaks 8.28.0
- trufflehog 3.90.3
- bfg 1.15.0 (for history cleanup)

What Was Run (exact commands)
1) Create reports dir
   - `mkdir -p infra/gcp/security/reports`

2) Gitleaks – full git history (default) with redaction + SARIF
   - `gitleaks detect --source /Users/carlos/workspace/re-frame --redact --report-format sarif --report-path infra/gcp/security/reports/gitleaks.sarif`

3) Gitleaks – working tree only (uncommitted files)
   - `gitleaks detect --no-git --source /Users/carlos/workspace/re-frame --redact --report-format json --report-path infra/gcp/security/reports/gitleaks-fs.json`

4) TruffleHog – full git history
   - `trufflehog git --json file:///Users/carlos/workspace/re-frame > infra/gcp/security/reports/trufflehog-git.json`

5) TruffleHog – working tree (all results)
   - `trufflehog filesystem --json /Users/carlos/workspace/re-frame > infra/gcp/security/reports/trufflehog-fs.json`

6) TruffleHog – working tree (verified only)
   - `trufflehog filesystem --only-verified --json /Users/carlos/workspace/re-frame > infra/gcp/security/reports/trufflehog-fs-verified.json`

Immediate Containment (local hygiene)
- Verified `.gitignore` already excludes `.env` and `.next/`.
- Will add ignores for `.claude/`, `backend/.venv/`, and `reframe_diag_*/` to avoid accidental inclusion of sensitive/generated files.
- Pre-commit guardrail to be added: gitleaks protect hook.

Credential Rotation (action required outside repo)
- Any real API keys/tokens found must be revoked/rotated at the upstream provider before publishing remediation work or pushing to remote. Do this first for:
  - AI provider keys present in `.env` (e.g., OpenAI, xAI, OpenRouter), if they were ever committed or shared.
  - Any Google API key observed in local files or diagnostic outputs.
  - Any preview/encryption keys that were committed (none confirmed committed; values seen in build artifacts only were untracked).

History Purge Plan (prepared, not executed here)
1) Mirror clone, operate on the mirror
   - `git clone --mirror git@github.com:macayaven/re-frame.git`
   - `cd re-frame.git`

2) Remove known sensitive files across history (adjust globs as needed)
   - `java -jar $(brew --prefix)/opt/bfg/libexec/bfg.jar --delete-files '{*.pem,*.key,.env,.env.*,id_rsa*,*.p12}' .`

3) Replace secrets by value or regex across history
   - Create `replacements.txt` with lines like (examples):
     - `regex:\bAIza[0-9A-Za-z\-_.]{35}\b==>GOOGLE_API_KEY_REDACTED`
     - `regex:\bxai-[A-Za-z0-9]{70,}\b==>XAI_API_KEY_REDACTED`
     - `regex:\bsk-[A-Za-z0-9]{20,}\b==>OPENAI_API_KEY_REDACTED`
   - Run: `java -jar $(brew --prefix)/opt/bfg/libexec/bfg.jar --replace-text ../replacements.txt .`

4) Cleanup + force push rewritten history (requires repo admin)
   - `git reflog expire --expire=now --all`
   - `git gc --prune=now --aggressive`
   - `git push --force`

5) Fix the working copy after rewrite
   - `cd .. && cd re-frame`
   - `git rm -r --cached .env .env.* *.pem *.key id_rsa* || true`
   - Append to `.gitignore`: patterns for `.env`, keys, and sensitive files
   - `git add .gitignore`
   - `git commit -m "Remove secrets and ignore sensitive files"`
   - `git push`

Guardrails Going Forward
- Local pre-commit
  - Add to `backend/.pre-commit-config.yaml`:
    ```yaml
    - repo: https://github.com/gitleaks/gitleaks
      rev: v8.28.0
      hooks:
        - id: gitleaks
          args: ["protect", "--staged", "--redact", "--verbose"]
    ```
  - `pipx install pre-commit && pre-commit install`

- CI
  - Enable GitHub Advanced Security secret scanning if available.
  - Optional minimal GitHub Action using `gitleaks/gitleaks-action@v2` with `fetch-depth: 0`.

Operational Notes
- Force-pushing a rewritten history will invalidate existing forks/clones; all contributors must re-clone.
- Do not store real credentials in `.env` checked into git. Use GCP Secret Manager and runtime injection; commit an `.env.example` instead.
