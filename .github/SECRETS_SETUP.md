# GitHub Secrets Configuration Guide

## Required Secrets

These secrets must be added to your GitHub repository settings under Settings → Secrets and variables → Actions.

### 1. Firebase Secrets (Required)

#### `FIREBASE_SERVICE_ACCOUNT` (Required)
The Firebase service account JSON key for deployment.

**How to get it:**
1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your project
3. Go to Project Settings → Service Accounts
4. Click "Generate new private key"
5. Copy the entire JSON content
6. Add it as a secret in GitHub

#### `FIREBASE_PROJECT_ID` (Required)
Your Firebase project ID.

**How to get it:**
1. Go to Firebase Console → Project Settings
2. Copy the Project ID (e.g., `re-frame-social`)

### 2. Firebase Environment Variables (Required for Build)

These are public configuration values but need to be in secrets for the build process:

- `NEXT_PUBLIC_FIREBASE_API_KEY`
- `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`
- `NEXT_PUBLIC_FIREBASE_PROJECT_ID`
- `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET`
- `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID`
- `NEXT_PUBLIC_FIREBASE_APP_ID`
- `NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID`

**How to get them:**
1. Go to Firebase Console → Project Settings
2. Scroll down to "Your apps" → Web app
3. Copy the Firebase configuration object values

Example:
```javascript
const firebaseConfig = {
  REDACTED
  authDomain: "...",          // → NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN
  projectId: "...",           // → NEXT_PUBLIC_FIREBASE_PROJECT_ID
  storageBucket: "...",       // → NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET
  messagingSenderId: "...",   // → NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID
  appId: "...",               // → NEXT_PUBLIC_FIREBASE_APP_ID
  measurementId: "..."        // → NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID
};
```

### 3. Optional Secrets

#### `CODECOV_TOKEN` (Optional)
For code coverage reporting.

**How to get it:**
1. Sign up at [codecov.io](https://codecov.io)
2. Add your repository
3. Copy the upload token

#### `SNYK_TOKEN` (Optional)
For enhanced security scanning.

**How to get it:**
1. Sign up at [snyk.io](https://snyk.io)
2. Go to Account Settings → Auth Token
3. Copy your auth token

## How to Add Secrets

1. Go to your repository on GitHub
2. Click on "Settings" tab
3. In the left sidebar, click "Secrets and variables" → "Actions"
4. Click "New repository secret"
5. Add the secret name and value
6. Click "Add secret"

## Verification

After adding all secrets, you can verify they're working by:

1. Making a small change and pushing to trigger the CI workflow
2. Checking the Actions tab to see if workflows run successfully
3. For deployment, push to main branch and check if it deploys

## Environment Setup

For production deployments, you may also want to create an environment:

1. Go to Settings → Environments
2. Click "New environment"
3. Name it "production"
4. Add protection rules:
   - Required reviewers
   - Restrict to main branch
5. Add environment secrets (same as above)

## Local Development

For local development, create a `.env.local` file:

```bash
NEXT_PUBLIC_FIREBASE_API_KEY=your-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-auth-domain
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-storage-bucket
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
NEXT_PUBLIC_FIREBASE_APP_ID=your-app-id
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=your-measurement-id
```

**Note:** Never commit `.env.local` to version control!

## Troubleshooting

### Deployment Fails
- Check if `FIREBASE_SERVICE_ACCOUNT` is valid JSON
- Verify `FIREBASE_PROJECT_ID` matches your project
- Ensure service account has necessary permissions

### Build Fails
- Verify all `NEXT_PUBLIC_*` variables are set
- Check if values are correctly formatted (no extra quotes)

### Security Scan Fails
- `SNYK_TOKEN` is optional; workflows will continue without it
- Security scans may find vulnerabilities in dependencies

## Security Notes

- Never share these secrets
- Rotate service account keys periodically
- Use environment protection for production secrets
- Audit secret access in Settings → Secrets → Access