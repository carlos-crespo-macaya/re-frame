# Identity-Aware Proxy (IAP) Configuration Guide

This guide explains how to configure Google Cloud's Identity-Aware Proxy (IAP) to protect your re-frame demo deployment.

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
- [OAuth Configuration](#oauth-configuration)
- [IAP Activation](#iap-activation)
- [Access Management](#access-management)
- [Testing IAP](#testing-iap)
- [Troubleshooting](#troubleshooting)
- [Security Best Practices](#security-best-practices)

## Overview

Identity-Aware Proxy (IAP) provides a secure way to control access to your application without using a VPN. It verifies user identity and context to determine if a user should be granted access.

### Benefits
- **Zero Trust Security**: Verifies every request
- **No VPN Required**: Access from anywhere securely
- **Fine-grained Access Control**: Control who can access what
- **Audit Logging**: Track all access attempts
- **Integration with Google Workspace**: Use existing organizational accounts

## Prerequisites

1. **GCP Project** with billing enabled
2. **Domain ownership** verified in Google Search Console
3. **gcloud CLI** installed and authenticated
4. **GitHub repository** with admin access for secrets

## Initial Setup

### 1. Enable Required APIs

```bash
gcloud services enable iap.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
```

### 2. Configure OAuth Consent Screen

1. Go to [APIs & Services → OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent)
2. Select user type:
   - **Internal**: Only users in your Google Workspace (recommended for demos)
   - **External**: Any Google account (requires additional verification)
3. Fill in required information:
   - App name: `re-frame Demo`
   - User support email: Your email
   - Authorized domains: 
     - `run.app` (for Cloud Run default domains)
     - Your organization domain (if using Google Workspace)
   - Developer contact: Your email

## OAuth Configuration

### 1. Create OAuth 2.0 Credentials

1. Go to [APIs & Services → Credentials](https://console.cloud.google.com/apis/credentials)
2. Click **Create Credentials** → **OAuth client ID**
3. Configure:
   - Application type: `Web application`
   - Name: `re-frame IAP`
   - Authorized redirect URIs:
     ```
     https://iap.googleapis.com/v1/oauth/clientIds/[CLIENT_ID]:handleRedirect
     ```
     (You'll update this after getting the CLIENT_ID)

### 2. Store Credentials Securely

```bash
# Store in Secret Manager
echo -n "YOUR_CLIENT_ID" | gcloud secrets create iap-client-id --data-file=-
echo -n "YOUR_CLIENT_SECRET" | gcloud secrets create iap-client-secret --data-file=-

# Grant access to service account
gcloud secrets add-iam-policy-binding iap-client-id \
  --member="serviceAccount:github-actions-deploy@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding iap-client-secret \
  --member="serviceAccount:github-actions-deploy@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### 3. Add to GitHub Secrets

Add these secrets to your GitHub repository:
- `IAP_CLIENT_ID`: Your OAuth client ID
- `IAP_CLIENT_SECRET`: Your OAuth client secret

## IAP Activation

### 1. Enable IAP for Cloud Run Service

The GitHub Actions workflow automatically enables IAP during deployment. Manual activation:

```bash
# Enable IAP for the frontend service
gcloud iap web enable \
  --resource-type=backend-services \
  --oauth2-client-id=YOUR_CLIENT_ID \
  --oauth2-client-secret=YOUR_CLIENT_SECRET \
  --service=re-frame-frontend
```

### 2. Configure Backend Service

Update the backend CORS configuration to accept requests from the IAP domain:

```python
# In backend main.py
allowed_origins = [
    "https://re-frame-frontend-HASH-REGION.run.app",
    "https://YOUR_CUSTOM_DOMAIN.com",  # If using custom domain
]
```

## Access Management

### 1. Grant Access to Users

```bash
# Grant access to specific user
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="user:demo@example.com" \
  --role="roles/iap.httpsResourceAccessor"

# Grant access to Google Group
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="group:demo-users@example.com" \
  --role="roles/iap.httpsResourceAccessor"

# Grant access to entire domain (be careful!)
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="domain:example.com" \
  --role="roles/iap.httpsResourceAccessor"
```

### 2. Create Access Levels (Advanced)

For more granular control, use Access Context Manager:

```bash
# Create access level for specific IP ranges
gcloud access-context-manager levels create demo_access \
  --title="Demo Access" \
  --basic-level-spec=ipSubnetworks="203.0.113.0/24,198.51.100.0/24" \
  --combine-function=AND
```

## Testing IAP

### 1. Verify IAP is Active

```bash
# Check IAP status
gcloud iap web get-iam-policy \
  --resource-type=backend-services \
  --service=re-frame-frontend
```

### 2. Test Access

1. **Authorized User**:
   - Navigate to your service URL
   - Should see Google login screen
   - After authentication, access granted

2. **Unauthorized User**:
   - Navigate to your service URL
   - After authentication, should see "Access Denied"

### 3. Test with curl

```bash
# Get identity token
REDACTED)

# Test with token
curl -H "Authorization: Bearer $TOKEN" \
     https://re-frame-frontend-HASH-REGION.run.app
```

## Troubleshooting

### Common Issues

1. **"Access Denied" for authorized users**
   - Check IAM policy bindings
   - Verify OAuth consent screen configuration
   - Ensure cookies are enabled

2. **CORS errors**
   - Backend must include IAP domain in allowed origins
   - Check for proper headers in responses

3. **Redirect loops**
   - Clear browser cookies
   - Check OAuth redirect URI configuration
   - Verify service is healthy

### Debug Commands

```bash
# Check IAP configuration
gcloud iap web describe \
  --resource-type=backend-services \
  --service=re-frame-frontend

# View access logs
gcloud logging read \
  "resource.type=cloud_run_revision AND 
   resource.labels.service_name=re-frame-frontend AND
   httpRequest.requestUrl=~'.*iap.*'" \
  --limit=50

# Test backend directly (bypassing IAP)
gcloud run services proxy re-frame-backend --region=REGION
```

## Security Best Practices

### 1. Principle of Least Privilege
- Only grant access to users who need it
- Use groups for easier management
- Regularly audit access lists

### 2. Monitoring
```bash
# Set up alert for failed access attempts
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="IAP Access Denied Alert" \
  --condition-display-name="High number of access denials" \
  --condition-expression='
    resource.type="cloud_run_revision"
    AND jsonPayload.httpRequest.status=403
    AND rate(1m) > 10
  '
```

### 3. Regular Audits
- Review IAM policies monthly
- Check OAuth consent screen settings
- Monitor for unusual access patterns

### 4. Additional Security Layers
- Enable VPC Service Controls for additional network security
- Use Binary Authorization for container security
- Implement Cloud Armor for DDoS protection

## Custom Domain Setup (Optional)

If using a custom domain with IAP:

1. **Add domain mapping**:
   ```bash
   gcloud run domain-mappings create \
     --service=re-frame-frontend \
     --domain=demo.example.com \
     --region=REGION
   ```

2. **Update DNS records** as instructed

3. **Update OAuth redirect URIs** to include custom domain

4. **Update backend CORS** to accept custom domain

## Cost Considerations

IAP pricing:
- **No charge** for authentication requests
- **Standard Cloud Run charges** apply
- **Logging costs** if extensive logging enabled

## Next Steps

1. Configure monitoring dashboards
2. Set up automated access reviews
3. Implement custom error pages
4. Configure session timeout policies
5. Enable Cloud Armor for additional protection

## References

- [IAP Documentation](https://cloud.google.com/iap/docs)
- [Cloud Run with IAP](https://cloud.google.com/run/docs/authenticating/iap)
- [Access Context Manager](https://cloud.google.com/access-context-manager/docs)
- [Cloud Armor](https://cloud.google.com/armor/docs)