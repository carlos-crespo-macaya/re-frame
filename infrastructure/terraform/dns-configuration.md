# DNS Configuration for re-frame.social

## Overview
This document provides the DNS configuration required for the re-frame.social domain. The domain is registered with name.com and needs to be configured to work with our GCP infrastructure.

## Current Infrastructure Status
- Domain: re-frame.social (expires June 20, 2026)
- Registrar: name.com
- Frontend: Firebase Hosting (to be configured)
- Backend API: Cloud Run (to be configured)

## Required DNS Records

### Frontend (Firebase Hosting)
```
# Root domain A records (Firebase IPs)
Type: A     | Name: @    | Value: 151.101.1.195
Type: A     | Name: @    | Value: 151.101.65.195

# WWW subdomain
Type: CNAME | Name: www  | Value: re-frame-social.web.app
```

### Backend API (Cloud Run)
```
Type: CNAME | Name: api  | Value: [Cloud Run service URL - to be determined after deployment]
```

### Email Forwarding (Optional for P0)
```
# MX Records for email forwarding
Type: MX    | Name: @    | Priority: 10 | Value: mx1.name.com
Type: MX    | Name: @    | Priority: 20 | Value: mx2.name.com

# TXT Record for SPF
Type: TXT   | Name: @    | Value: "v=spf1 include:spf.name.com ~all"
```

## Configuration Steps

### 1. Firebase Hosting Domain Setup
1. Add domain to Firebase Hosting via Firebase Console or Terraform
2. Firebase will provide verification TXT record
3. Add verification record to name.com DNS
4. Wait for verification (typically 10-30 minutes)
5. Add A records pointing to Firebase IPs

### 2. Cloud Run Domain Mapping
1. Deploy Cloud Run service first
2. Get the service URL (format: `https://[service-name]-[hash]-[region].a.run.app`)
3. Add CNAME record for api subdomain
4. Configure domain mapping in Cloud Run

### 3. Email Forwarding Setup (Optional)
1. Enable email forwarding in name.com dashboard
2. Add MX records as specified above
3. Configure forwarding rules (e.g., info@re-frame.social -> actual email)

## Verification Commands

```bash
# Check DNS propagation
dig re-frame.social
dig www.re-frame.social
dig api.re-frame.social

# Check specific record types
dig re-frame.social A
dig www.re-frame.social CNAME
dig api.re-frame.social CNAME

# Check from different DNS servers
dig @8.8.8.8 re-frame.social
dig @1.1.1.1 re-frame.social
```

## TTL Recommendations
- A records: 300 (5 minutes) during setup, 3600 (1 hour) after verification
- CNAME records: 300 during setup, 3600 after verification
- MX records: 3600
- TXT records: 300 during setup, 3600 after verification

## Important Notes
1. DNS propagation can take up to 48 hours globally
2. Keep TTL low during initial setup for faster changes
3. Firebase automatically provisions SSL certificates after domain verification
4. Cloud Run also auto-provisions SSL certificates for custom domains
5. Always verify HTTPS works before increasing TTL values

## Troubleshooting
- If domain verification fails, check TXT record is exactly as provided
- For SSL issues, ensure domain is fully propagated before expecting certificates
- Use online DNS checkers to verify global propagation
- Check Firebase/Cloud Run logs for domain-specific errors