# Deployment Guide

This guide walks through deploying the posts-system to Google Cloud Platform (project: crystalloids-candidates).

## Prerequisites

- Google Cloud SDK (`gcloud`) installed and authenticated
- Project ID: `crystalloids-candidates`
- Appropriate IAM permissions in the GCP project

## Step 1: Enable Required GCP APIs

```bash
# Set your project
gcloud config set project crystalloids-candidates

# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  firestore.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  firebase.googleapis.com
```

## Step 2: Create Firestore Database

```bash
# Create Firestore database in Native mode in us-central1
gcloud firestore databases create --location=us-central1 --type=firestore-native
```

## Step 3: Deploy Firestore Configuration

```bash
# Deploy Firestore indexes
cd backend
firebase deploy --only firestore:indexes --project crystalloids-candidates

# Deploy Firestore security rules
firebase deploy --only firestore:rules --project crystalloids-candidates
```

## Step 4: Create Service Account for Backend

```bash
# Create service account
gcloud iam service-accounts create posts-backend-sa \
  --display-name="Posts Backend Service Account" \
  --project=crystalloids-candidates

# Grant Firestore permissions
gcloud projects add-iam-policy-binding crystalloids-candidates \
  --member="serviceAccount:posts-backend-sa@crystalloids-candidates.iam.gserviceaccount.com" \
  --role="roles/datastore.user"

# Grant Secret Manager access
gcloud projects add-iam-policy-binding crystalloids-candidates \
  --member="serviceAccount:posts-backend-sa@crystalloids-candidates.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## Step 5: Create Secrets in Secret Manager

```bash
# Generate a random SECRET_KEY (or use your own)
SECRET_KEY=$(openssl rand -base64 32)

# Create secrets
echo -n "$SECRET_KEY" | gcloud secrets create SECRET_KEY \
  --data-file=- \
  --replication-policy="automatic" \
  --project=crystalloids-candidates

# For DEV_MODE, we'll use placeholder values for OAuth credentials
echo -n "placeholder-client-id" | gcloud secrets create GOOGLE_CLIENT_ID \
  --data-file=- \
  --replication-policy="automatic" \
  --project=crystalloids-candidates

echo -n "placeholder-client-secret" | gcloud secrets create GOOGLE_CLIENT_SECRET \
  --data-file=- \
  --replication-policy="automatic" \
  --project=crystalloids-candidates
```

**Note:** These are placeholder values since we're using DEV_MODE=true. If you want to enable real OAuth later, update these secrets with actual Google OAuth credentials.

## Step 6: Create Artifact Registry Repository

```bash
# Create Docker repository in us-central1
gcloud artifacts repositories create posts-system \
  --repository-format=docker \
  --location=us-central1 \
  --description="Posts system Docker images" \
  --project=crystalloids-candidates
```

## Step 7: Deploy Backend to Cloud Run

### Option A: Using Cloud Build (Recommended)

```bash
cd backend

# Submit build to Cloud Build
gcloud builds submit \
  --config=cloudbuild.yaml \
  --project=crystalloids-candidates
```

### Option B: Manual Deployment

```bash
cd backend

# Build and push Docker image
docker build -t us-central1-docker.pkg.dev/crystalloids-candidates/posts-system/backend:latest .
docker push us-central1-docker.pkg.dev/crystalloids-candidates/posts-system/backend:latest

# Deploy to Cloud Run
gcloud run deploy posts-backend \
  --image=us-central1-docker.pkg.dev/crystalloids-candidates/posts-system/backend:latest \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --service-account=posts-backend-sa@crystalloids-candidates.iam.gserviceaccount.com \
  --set-env-vars=DB_TYPE=firestore,GCP_PROJECT_ID=crystalloids-candidates,DEV_MODE=true,FRONTEND_URL=https://crystalloids-candidates.web.app,ALGORITHM=HS256,ACCESS_TOKEN_EXPIRE_MINUTES=30,ALLOWED_ORIGINS='["https://crystalloids-candidates.web.app","https://crystalloids-candidates.firebaseapp.com"]' \
  --set-secrets=SECRET_KEY=SECRET_KEY:latest,GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID:latest,GOOGLE_CLIENT_SECRET=GOOGLE_CLIENT_SECRET:latest \
  --min-instances=0 \
  --max-instances=10 \
  --memory=512Mi \
  --cpu=1 \
  --timeout=300 \
  --concurrency=80 \
  --project=crystalloids-candidates
```

**After deployment, note the Cloud Run service URL** (e.g., `https://posts-backend-xxxxx-uc.a.run.app`)

## Step 8: Update Frontend Configuration

Once the backend is deployed, you need to update the frontend Cloud Build configuration with the actual backend URL.

```bash
# Get the Cloud Run URL
BACKEND_URL=$(gcloud run services describe posts-backend \
  --region=us-central1 \
  --platform=managed \
  --format='value(status.url)' \
  --project=crystalloids-candidates)

echo "Backend URL: $BACKEND_URL"
```

Now edit `frontend/cloudbuild.yaml` and update line 15 and line 29:
- Line 15: `- 'VITE_API_URL=<YOUR_BACKEND_URL>'`
- Line 29: Replace `_CLOUD_RUN_SERVICE_HASH: 'REPLACE_WITH_ACTUAL_HASH'` with the actual hash from the URL

Also update `frontend/.env.production`:
```bash
cd frontend
echo "VITE_API_URL=$BACKEND_URL" > .env.production
```

## Step 9: Initialize Firebase in Frontend

```bash
cd frontend

# Login to Firebase
firebase login

# Initialize Firebase (if not already done)
firebase use crystalloids-candidates
```

## Step 10: Deploy Frontend to Firebase Hosting

### Option A: Using Cloud Build (Recommended)

```bash
cd frontend

# Submit build to Cloud Build
gcloud builds submit \
  --config=cloudbuild.yaml \
  --project=crystalloids-candidates
```

### Option B: Manual Deployment

```bash
cd frontend

# Install dependencies
npm install

# Build the frontend
VITE_API_URL=$BACKEND_URL npm run build

# Deploy to Firebase Hosting
firebase deploy --only hosting --project crystalloids-candidates
```

**Your frontend will be available at:** `https://crystalloids-candidates.web.app`

## Step 11: Set Up Cloud Build Triggers for CI/CD (Optional)

To enable automatic deployments on git push:

### Backend Trigger

```bash
gcloud builds triggers create github \
  --repo-name=posts-system \
  --repo-owner=<YOUR_GITHUB_USERNAME> \
  --branch-pattern="^main$" \
  --build-config=backend/cloudbuild.yaml \
  --included-files="backend/**" \
  --name=deploy-backend \
  --project=crystalloids-candidates
```

### Frontend Trigger

```bash
gcloud builds triggers create github \
  --repo-name=posts-system \
  --repo-owner=<YOUR_GITHUB_USERNAME> \
  --branch-pattern="^main$" \
  --build-config=frontend/cloudbuild.yaml \
  --included-files="frontend/**" \
  --name=deploy-frontend \
  --project=crystalloids-candidates
```

## Verification

After deployment, verify everything works:

1. **Backend Health Check:**
   ```bash
   curl $BACKEND_URL/api/health
   # Should return: {"status":"healthy","message":"Service is running"}
   ```

2. **Frontend Access:**
   - Open `https://crystalloids-candidates.web.app` in your browser
   - Click "Continue as John Doe" or "Continue as Alice Smith"
   - Try creating a post
   - Try adding comments

## Environment Variables Summary

### Backend (Cloud Run)
- `DB_TYPE=firestore` - Use Firestore database
- `GCP_PROJECT_ID=crystalloids-candidates` - GCP project ID
- `DEV_MODE=true` - Enable mock users (no real OAuth needed)
- `FRONTEND_URL=https://crystalloids-candidates.web.app` - Frontend URL for redirects
- `ALGORITHM=HS256` - JWT algorithm
- `ACCESS_TOKEN_EXPIRE_MINUTES=30` - Token expiry time
- `ALLOWED_ORIGINS=[...]` - CORS allowed origins

### Secrets (Secret Manager)
- `SECRET_KEY` - JWT secret key
- `GOOGLE_CLIENT_ID` - Google OAuth client ID (placeholder for DEV_MODE)
- `GOOGLE_CLIENT_SECRET` - Google OAuth client secret (placeholder for DEV_MODE)

## Troubleshooting

### Backend Issues

**Check logs:**
```bash
gcloud run services logs read posts-backend \
  --region=us-central1 \
  --project=crystalloids-candidates \
  --limit=50
```

**Update service:**
```bash
# Re-deploy with same settings
gcloud builds submit --config=backend/cloudbuild.yaml --project=crystalloids-candidates
```

### Frontend Issues

**Check build logs:**
```bash
gcloud builds list --project=crystalloids-candidates --limit=5
gcloud builds log <BUILD_ID> --project=crystalloids-candidates
```

**Verify Firebase hosting:**
```bash
firebase hosting:channel:list --project=crystalloids-candidates
```

### Firestore Issues

**View Firestore data:**
```bash
# Open Firestore console
gcloud firestore databases describe --format="value(name)" --project=crystalloids-candidates
```

Or visit: https://console.cloud.google.com/firestore/databases/-default-/data/panel?project=crystalloids-candidates

## Cost Considerations

With the current configuration:
- **Cloud Run:** Pay-per-use, min-instances=0 means no cost when idle
- **Firestore:** Free tier includes 50K reads/day, 20K writes/day
- **Firebase Hosting:** Free tier includes 10GB storage, 360MB/day transfer
- **Cloud Build:** Free tier includes 120 build-minutes/day

For a testing/development environment, this should stay within free tier limits.

## Next Steps

1. **Monitor your deployment** in the GCP Console
2. **Set up alerting** for errors or high costs
3. **Consider adding** application logging and monitoring
4. **When ready for production:**
   - Set `DEV_MODE=false`
   - Add real Google OAuth credentials
   - Update CORS and FRONTEND_URL settings
   - Adjust min/max instances based on traffic
   - Set up custom domain for Firebase Hosting
