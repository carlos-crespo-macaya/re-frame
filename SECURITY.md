# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of re-frame.social seriously. If you have discovered a security vulnerability, please follow these steps:

### 1. Do NOT Create a Public Issue

Security vulnerabilities should NOT be reported through public GitHub issues.

### 2. Report Via Email

Please email security concerns to: [security@re-frame.social](mailto:security@re-frame.social)

Include the following information:
- Type of vulnerability
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### 3. Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 5 business days
- **Resolution Timeline**: Depends on severity
  - Critical: 7-14 days
  - High: 14-30 days
  - Medium: 30-60 days
  - Low: 60-90 days

### 4. Disclosure Policy

- We will work with you to understand and resolve the issue quickly
- We will keep you informed about the progress toward fixing the vulnerability
- We will credit you for the discovery (unless you prefer to remain anonymous)
- We ask that you give us reasonable time to resolve the issue before public disclosure

## Security Best Practices

When contributing to re-frame.social, please follow these security best practices:

### Code Security
- Never commit sensitive data (API keys, passwords, tokens)
- Use environment variables for configuration
- Validate and sanitize all user inputs
- Follow the principle of least privilege

### Dependencies
- Keep dependencies up to date
- Review dependency licenses
- Check for known vulnerabilities before adding new dependencies
- Use `npm audit` or `pnpm audit` regularly

### Authentication & Authorization
- Implement proper session management
- Use secure communication (HTTPS)
- Follow OWASP guidelines

### Data Protection
- No user data is stored on the client
- Audio data is not persisted
- Follow privacy-by-design principles

## Security Features

re-frame.social implements several security features:

1. **Content Security Policy (CSP)**: Restrictive CSP headers prevent XSS attacks
2. **No Data Storage**: No user data is stored client-side
3. **Secure Headers**: Security headers configured in `next.config.js`
4. **Input Validation**: All user inputs are validated and sanitized
5. **Regular Updates**: Dependencies are regularly updated via Dependabot

## Contact

For any security-related questions, contact: [security@re-frame.social](mailto:security@re-frame.social)