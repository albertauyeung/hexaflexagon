# Deployment Guide for Google Cloud Run

This guide walks you through deploying the Hexaflexagon Generator web application to Google Cloud Run.

## Prerequisites

1. **Google Cloud Account**: Create one at [cloud.google.com](https://cloud.google.com)
2. **gcloud CLI**: Install the Google Cloud SDK from [cloud.google.com/sdk](https://cloud.google.com/sdk/docs/install)
3. **Docker**: Install Docker from [docker.com](https://www.docker.com/get-started)

## Setup

### 1. Install gcloud CLI

If you haven't already, install the Google Cloud CLI:

```bash
# For macOS (using Homebrew)
brew install google-cloud-sdk

# For other platforms, visit:
# https://cloud.google.com/sdk/docs/install
```

### 2. Initialize gcloud

```bash
# Login to your Google account
gcloud auth login

# Set your project (replace PROJECT_ID with your actual project ID)
gcloud config set project PROJECT_ID

# If you don't have a project yet, create one:
gcloud projects create PROJECT_ID --name="Hexaflexagon Generator"
```

### 3. Enable Required APIs

```bash
# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Enable Container Registry API
gcloud services enable containerregistry.googleapis.com

# Enable Artifact Registry API (recommended over Container Registry)
gcloud services enable artifactregistry.googleapis.com
```

## Deployment Steps

### Option 1: Deploy Directly from Source (Recommended)

Cloud Run can build and deploy directly from your source code:

```bash
# Deploy from the project root directory
gcloud run deploy hexaflexagon-generator \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --port 8080
```

This command will:
- Build your Docker image automatically
- Push it to Google Container Registry
- Deploy it to Cloud Run
- Make it publicly accessible

### Option 2: Build and Deploy Manually

If you prefer more control over the build process:

#### Step 1: Build the Docker Image

```bash
# Set your project ID
export PROJECT_ID=your-project-id

# Build the image
docker build -t gcr.io/$PROJECT_ID/hexaflexagon-generator:latest .
```

#### Step 2: Test Locally (Optional)

```bash
# Run the container locally
docker run -p 8080:8080 gcr.io/$PROJECT_ID/hexaflexagon-generator:latest

# Visit http://localhost:8080 in your browser
```

#### Step 3: Push to Container Registry

```bash
# Configure Docker to use gcloud as a credential helper
gcloud auth configure-docker

# Push the image
docker push gcr.io/$PROJECT_ID/hexaflexagon-generator:latest
```

#### Step 4: Deploy to Cloud Run

```bash
gcloud run deploy hexaflexagon-generator \
  --image gcr.io/$PROJECT_ID/hexaflexagon-generator:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --port 8080
```

## Configuration Options

### Memory and CPU

Adjust based on your needs:

```bash
# Minimal (for low traffic)
--memory 256Mi --cpu 1

# Standard (recommended)
--memory 512Mi --cpu 1

# High performance
--memory 1Gi --cpu 2
```

### Scaling

Configure autoscaling:

```bash
--min-instances 0 \      # Scale to zero when no traffic
--max-instances 10 \     # Maximum concurrent instances
--concurrency 80         # Requests per instance
```

### Region Selection

Choose a region close to your users:

```bash
# US
--region us-central1
--region us-east1

# Europe
--region europe-west1

# Asia
--region asia-northeast1

# See all regions:
gcloud run regions list
```

## Post-Deployment

### Get Your Service URL

After deployment, you'll see output like:

```
Service URL: https://hexaflexagon-generator-xxxxxxxxx-uc.a.run.app
```

### View Logs

```bash
# Stream logs
gcloud run services logs tail hexaflexagon-generator --region us-central1

# View logs in Cloud Console
gcloud run services describe hexaflexagon-generator --region us-central1
```

### Update the Service

To deploy updates:

```bash
# Using source deploy (easiest)
gcloud run deploy hexaflexagon-generator --source .

# Or rebuild and push new image
docker build -t gcr.io/$PROJECT_ID/hexaflexagon-generator:latest .
docker push gcr.io/$PROJECT_ID/hexaflexagon-generator:latest
gcloud run deploy hexaflexagon-generator \
  --image gcr.io/$PROJECT_ID/hexaflexagon-generator:latest
```

## Custom Domain (Optional)

### 1. Verify Domain Ownership

```bash
gcloud domains verify example.com
```

### 2. Map Domain

```bash
gcloud run domain-mappings create \
  --service hexaflexagon-generator \
  --domain hexaflexagon.example.com \
  --region us-central1
```

### 3. Update DNS

Add the DNS records shown in the output to your domain provider.

## Environment Variables (Optional)

If you need to add environment variables:

```bash
gcloud run services update hexaflexagon-generator \
  --set-env-vars "KEY1=value1,KEY2=value2"
```

## Monitoring and Costs

### View Metrics

Monitor your service in the [Cloud Console](https://console.cloud.google.com/run):
- Request count
- Request latency
- Container instances
- Memory usage
- CPU utilization

### Pricing

Cloud Run pricing is based on:
- **Request count**: First 2 million requests/month are free
- **Compute time**: Only pay when handling requests
- **Memory and CPU**: Billed per 100ms of usage

With `--min-instances 0`, you only pay when someone uses the app.

Estimated monthly cost for low traffic: **$0-5**

## Security Best Practices

### 1. Require Authentication (Optional)

To restrict access:

```bash
gcloud run services update hexaflexagon-generator \
  --no-allow-unauthenticated
```

### 2. Set Resource Limits

```bash
--max-instances 10  # Prevent runaway costs
--cpu-throttling    # Reduce costs when idle
```

### 3. Use Secret Manager

For sensitive data:

```bash
# Create a secret
echo -n "secret-value" | gcloud secrets create my-secret --data-file=-

# Grant Cloud Run access
gcloud secrets add-iam-policy-binding my-secret \
  --member=serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor

# Use in deployment
gcloud run deploy hexaflexagon-generator \
  --set-secrets="SECRET_KEY=my-secret:latest"
```

## Troubleshooting

### Container fails to start

Check logs:
```bash
gcloud run services logs read hexaflexagon-generator --limit 50
```

Common issues:
- Port mismatch (ensure listening on PORT env var)
- Missing dependencies
- File permissions

### Out of memory

Increase memory allocation:
```bash
gcloud run services update hexaflexagon-generator --memory 1Gi
```

### Slow cold starts

Set minimum instances:
```bash
gcloud run services update hexaflexagon-generator --min-instances 1
```

## Cleanup

To delete the service and save costs:

```bash
gcloud run services delete hexaflexagon-generator --region us-central1
```

## Continuous Deployment with GitHub Actions

The repo ships a workflow at `.github/workflows/deploy.yml` that deploys to Cloud Run on every push to `main`. It uses Workload Identity Federation, so no long-lived service account keys are stored in GitHub.

### One-time setup

Run these commands locally once. Replace the placeholders.

```bash
export PROJECT_ID=<your-gcp-project-id>
export PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')
export GITHUB_REPO=albertauyeung/hexaflexagon
export SA_NAME=github-deployer
export POOL=github-pool
export PROVIDER=github-provider

# Enable APIs
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  iamcredentials.googleapis.com \
  --project "$PROJECT_ID"

# Create the deployer service account
gcloud iam service-accounts create "$SA_NAME" \
  --display-name="GitHub Actions deployer" \
  --project "$PROJECT_ID"

export SA_EMAIL="$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

# Roles needed to build with Cloud Build and deploy to Cloud Run
for role in roles/run.admin roles/cloudbuild.builds.editor \
            roles/artifactregistry.writer roles/storage.admin \
            roles/iam.serviceAccountUser roles/logging.viewer; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SA_EMAIL" --role="$role"
done

# Create a Workload Identity Pool + GitHub OIDC provider
gcloud iam workload-identity-pools create "$POOL" \
  --project="$PROJECT_ID" --location=global \
  --display-name="GitHub Actions pool"

gcloud iam workload-identity-pools providers create-oidc "$PROVIDER" \
  --project="$PROJECT_ID" --location=global \
  --workload-identity-pool="$POOL" \
  --display-name="GitHub OIDC" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner" \
  --attribute-condition="assertion.repository_owner=='${GITHUB_REPO%%/*}'" \
  --issuer-uri="https://token.actions.githubusercontent.com"

# Allow the GitHub repo to impersonate the service account
gcloud iam service-accounts add-iam-policy-binding "$SA_EMAIL" \
  --project="$PROJECT_ID" \
  --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$POOL/attribute.repository/$GITHUB_REPO"

# Print the values to paste into GitHub
echo "WIF_PROVIDER=projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$POOL/providers/$PROVIDER"
echo "WIF_SERVICE_ACCOUNT=$SA_EMAIL"
echo "GCP_PROJECT_ID=$PROJECT_ID"
```

### GitHub repository configuration

In **Settings → Secrets and variables → Actions → Variables** add three repository variables:

| Name | Value |
|---|---|
| `GCP_PROJECT_ID` | your project ID |
| `WIF_PROVIDER` | `projects/<PROJECT_NUMBER>/locations/global/workloadIdentityPools/github-pool/providers/github-provider` |
| `WIF_SERVICE_ACCOUNT` | `github-deployer@<PROJECT_ID>.iam.gserviceaccount.com` |

(They're variables, not secrets — none of these values are sensitive.)

### Trigger a deploy

Push to `main`, or run the workflow manually from the **Actions** tab.

## Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)
- [FastAPI Deployment Best Practices](https://fastapi.tiangolo.com/deployment/)
- [Container Image Best Practices](https://cloud.google.com/architecture/best-practices-for-building-containers)
- [google-github-actions/auth](https://github.com/google-github-actions/auth) — Workload Identity Federation reference
