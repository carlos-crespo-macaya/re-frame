# CI/CD Setup Guide

This document describes the CI/CD pipeline configuration for re-frame.social.

## Overview

Our CI/CD pipeline is built on GitHub Actions and includes:
- Continuous Integration (CI) for all branches
- Automated deployment to Firebase Hosting
- Security scanning and dependency updates
- Pull request validation and preview deployments

## Workflows

### 1. Continuous Integration (`ci.yml`)
Runs on every push and pull request.

**Jobs:**
- **Lint**: Runs ESLint to check code style
- **Type Check**: Validates TypeScript types
- **Test**: Runs Jest tests with coverage
- **Build**: Creates production build
- **Accessibility**: Runs Lighthouse CI tests
- **Security**: Performs security scanning

### 2. Deploy (`deploy.yml`)
Deploys to Firebase Hosting when pushing to `main`.

**Process:**
1. Runs all tests
2. Builds the application
3. Deploys to Firebase Hosting
4. Creates deployment summary

### 3. PR Validation (`pr-validation.yml`)
Validates pull requests before merge.

**Checks:**
- PR title follows semantic format
- Commit messages follow convention
- PR size is reasonable
- No merge conflicts
- Creates preview deployment

### 4. Security (`security.yml`)
Scheduled weekly security scans.

**Scans:**
- Dependency audit
- CodeQL analysis
- Trivy vulnerability scan
- OSV vulnerability scan

### 5. Release (`release.yml`)
Creates releases when tags are pushed.

**Actions:**
- Generates changelog
- Creates GitHub release
- Uploads build artifacts
- Deploys to production

## Required Secrets

Configure these in GitHub repository settings:

```bash
# Firebase
FIREBASE_SERVICE_ACCOUNT
FIREBASE_PROJECT_ID
NEXT_PUBLIC_FIREBASE_API_KEY
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN
NEXT_PUBLIC_FIREBASE_PROJECT_ID
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID
NEXT_PUBLIC_FIREBASE_APP_ID
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID

# Optional
CODECOV_TOKEN
SNYK_TOKEN
```

## Branch Protection Rules

Configure for `main` branch:

1. **Require pull request reviews**
   - Required approving reviews: 1
   - Dismiss stale reviews
   - Require review from CODEOWNERS

2. **Require status checks**
   - Require branches to be up to date
   - Required checks:
     - `lint`
     - `typecheck`
     - `test`
     - `build`

3. **Require conversation resolution**
   - All conversations must be resolved

4. **Include administrators**
   - Apply rules to administrators

## Local Development

### Running CI Checks Locally

```bash
# Lint
pnpm lint

# Type check
pnpm tsc --noEmit

# Test
pnpm test

# Test with coverage
pnpm test:ci

# Build
pnpm build
```

### Pre-commit Hooks

Consider adding husky for pre-commit checks:

```bash
pnpm add -D husky lint-staged
npx husky init
```

Add to `.husky/pre-commit`:
```bash
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

npx lint-staged
```

## Deployment

### Manual Deployment

```bash
# Deploy to Firebase
firebase deploy --only hosting
```

### Preview Deployments

PRs automatically get preview deployments. The URL is commented on the PR.

### Production Deployment

Push to `main` or create a release tag:

```bash
# Create a release
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0
```

## Monitoring

### Build Status
Check workflow runs at: `https://github.com/macayaven/re-frame/actions`

### Security Alerts
View security alerts at: `https://github.com/macayaven/re-frame/security`

### Dependency Updates
Dependabot creates PRs weekly for dependency updates.

## Troubleshooting

### Failed Deployments
1. Check workflow logs
2. Verify Firebase credentials
3. Ensure build passes locally

### Failed Tests
1. Run tests locally: `pnpm test`
2. Check for environment differences
3. Clear Jest cache: `pnpm jest --clearCache`

### Security Scan Failures
1. Run `pnpm audit` locally
2. Update dependencies: `pnpm update`
3. Check security advisories

## Best Practices

1. **Keep PRs small**: Easier to review and test
2. **Write descriptive commits**: Follow conventional commits
3. **Update tests**: Include tests with new features
4. **Monitor performance**: Check Lighthouse scores
5. **Review security alerts**: Address promptly

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Firebase Hosting Documentation](https://firebase.google.com/docs/hosting)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)