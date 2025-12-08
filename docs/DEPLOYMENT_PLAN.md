# Complete Deployment Plan - Railway

This document provides a comprehensive step-by-step guide for deploying the AI Case Interview Simulator to Railway, including all required environment variables, external services, and storage solutions.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [External Services Required](#external-services-required)
3. [Environment Variables Checklist](#environment-variables-checklist)
4. [Storage Solutions](#storage-solutions)
5. [Step-by-Step Deployment](#step-by-step-deployment)
6. [Post-Deployment Setup](#post-deployment-setup)
7. [Verification Checklist](#verification-checklist)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before deploying, ensure you have:

- ✅ Railway account (sign up at https://railway.app)
- ✅ GitHub/GitLab/Bitbucket account with your code repository
- ✅ OpenAI API account with billing enabled
- ✅ (Optional) Cloudflare account for R2 storage
- ✅ (Optional) Domain name (if using custom domain)

---

## External Services Required

### 1. **OpenAI API** (Required)

**Purpose**: 
- Case generation (GPT-4o-mini)
- Interviewer responses (GPT-4o-mini)
- Performance evaluation (GPT-4o-mini)
- Coaching feedback (GPT-4o-mini)
- Audio/video transcription (Whisper API)

**Setup**:
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to API Keys: https://platform.openai.com/api-keys
4. Create a new secret key
5. **Important**: Set up billing and usage limits to prevent unexpected charges
6. Copy the API key (starts with `sk-...`)

**Cost Considerations**:
- GPT-4o-mini: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
- Whisper API: ~$0.006 per minute of audio
- Monitor usage in OpenAI dashboard

**Environment Variable**: `OPENAI_API_KEY`

---

### 2. **PostgreSQL Database** (Required - Provided by Railway)

**Purpose**: 
- Store all application data (users, sessions, cases, messages, evaluations)
- Railway automatically provides PostgreSQL service

**Setup**: 
- Add PostgreSQL service in Railway dashboard
- Railway automatically sets `DATABASE_URL`

**Environment Variable**: `DATABASE_URL` (auto-set by Railway)

---

### 3. **Redis** (Required - Provided by Railway)

**Purpose**: 
- WebSocket channel layer for real-time chat
- Session management for Django Channels

**Setup**: 
- Add Redis service in Railway dashboard
- Railway automatically sets `REDIS_URL`

**Environment Variable**: `REDIS_URL` (auto-set by Railway)

---

### 4. **Cloudflare R2** (Recommended for Persistent Storage)

**Purpose**: 
- Store casebook PDF files persistently
- Store user recordings (video/audio files)
- Store any media files that need to persist across deployments

**Why Cloudflare R2?**
- ✅ S3-compatible API (easy integration)
- ✅ No egress fees (unlike AWS S3)
- ✅ Free tier: 10GB storage, 1M Class A operations/month
- ✅ Fast global CDN
- ✅ Persistent storage (survives Railway deployments)

**Setup**:
1. Go to https://dash.cloudflare.com/
2. Sign up or log in
3. Navigate to R2: https://dash.cloudflare.com/?to=/:account/r2
4. Create a new R2 bucket (e.g., `case-interview-simulator`)
5. Go to "Manage R2 API Tokens"
6. Create API token with:
   - Permissions: Object Read & Write
   - Bucket: Your bucket name
7. Copy:
   - Account ID (found in R2 dashboard URL)
   - Bucket name
   - API token

**Environment Variables**:
- `CLOUDFLARE_R2_ACCOUNT_ID`
- `CLOUDFLARE_R2_BUCKET_NAME`
- `CLOUDFLARE_R2_ACCESS_KEY_ID` (from API token)
- `CLOUDFLARE_R2_SECRET_ACCESS_KEY` (from API token)
- `CLOUDFLARE_R2_ENDPOINT_URL` (e.g., `https://<account-id>.r2.cloudflarestorage.com`)

**Alternative**: If not using R2, Railway volumes can store files, but they're ephemeral and may be lost during redeployments.

---

### 5. **Anthropic API** (Optional - Alternative to OpenAI)

**Purpose**: Alternative LLM provider if you want to use Claude models

**Setup**: 
1. Go to https://console.anthropic.com/
2. Create API key
3. Set up billing

**Environment Variable**: `ANTHROPIC_API_KEY` (optional)

---

### 6. **AssemblyAI** (Optional - Alternative Transcription)

**Purpose**: Alternative transcription service (currently using OpenAI Whisper)

**Setup**: 
1. Go to https://www.assemblyai.com/
2. Sign up and get API key

**Environment Variable**: `ASSEMBLYAI_API_KEY` (optional)

---

### 7. **Pinecone** (Optional - For Advanced RAG)

**Purpose**: Vector database for more advanced RAG capabilities (currently using CrewAI's PDFSearchTool)

**Setup**: 
1. Go to https://www.pinecone.io/
2. Create account and index
3. Get API key and environment

**Environment Variables**:
- `PINECONE_API_KEY` (optional)
- `PINECONE_ENVIRONMENT` (optional)
- `PINECONE_INDEX_NAME` (optional, default: `case-interviews`)

---

## Environment Variables Checklist

### Required Variables

Set these in Railway's "Variables" section:

```bash
# Django Core
SECRET_KEY=<generate-secure-random-key>
DEBUG=False
ALLOWED_HOSTS=<your-railway-domain>.railway.app

# Database (Auto-set by Railway PostgreSQL)
DATABASE_URL=<auto-set-by-railway>

# Redis (Auto-set by Railway Redis)
REDIS_URL=<auto-set-by-railway>

# OpenAI API (Required)
OPENAI_API_KEY=sk-...
```

### Optional Variables

```bash
# Cloudflare R2 Storage (Recommended)
CLOUDFLARE_R2_ACCOUNT_ID=<your-account-id>
CLOUDFLARE_R2_BUCKET_NAME=case-interview-simulator
CLOUDFLARE_R2_ACCESS_KEY_ID=<from-api-token>
CLOUDFLARE_R2_SECRET_ACCESS_KEY=<from-api-token>
CLOUDFLARE_R2_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com

# Alternative APIs (Optional)
ANTHROPIC_API_KEY=sk-ant-...
ASSEMBLYAI_API_KEY=...
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=...
PINECONE_INDEX_NAME=case-interviews

# Logging (Optional)
DJANGO_LOG_LEVEL=INFO
```

### How to Generate SECRET_KEY

Run locally:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Or:
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

---

## Storage Solutions

### Option 1: Cloudflare R2 (Recommended)

**Best for**: Persistent storage of casebook PDFs, recordings, and media files

**Advantages**:
- ✅ Persistent across deployments
- ✅ No egress fees
- ✅ S3-compatible (easy Django integration)
- ✅ Free tier available
- ✅ Fast global CDN

**Implementation**:
1. Install `django-storages` and `boto3`:
   ```bash
   pip install django-storages boto3
   ```

2. Update `settings.py`:
   ```python
   # Add to INSTALLED_APPS
   INSTALLED_APPS = [
       # ... existing apps
       'storages',
   ]
   
   # Configure R2 storage
   if env('CLOUDFLARE_R2_ACCOUNT_ID', default=None):
       DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
       AWS_ACCESS_KEY_ID = env('CLOUDFLARE_R2_ACCESS_KEY_ID')
       AWS_SECRET_ACCESS_KEY = env('CLOUDFLARE_R2_SECRET_ACCESS_KEY')
       AWS_STORAGE_BUCKET_NAME = env('CLOUDFLARE_R2_BUCKET_NAME')
       AWS_S3_ENDPOINT_URL = env('CLOUDFLARE_R2_ENDPOINT_URL')
       AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.r2.cloudflarestorage.com'
       AWS_DEFAULT_ACL = 'public-read'  # Or 'private' for private files
   ```

3. Upload casebook PDF to R2:
   - Use Cloudflare dashboard or AWS CLI
   - Or create a management command to upload

**For Casebook PDF**:
- Upload `Darden-Case-Book-2018-2019.pdf` to R2 bucket
- Update `CaseGenerator` to fetch from R2 if not found locally

---

### Option 2: Railway Volumes (Temporary)

**Best for**: Development/testing only

**Advantages**:
- ✅ Simple setup
- ✅ No additional service needed

**Disadvantages**:
- ❌ Ephemeral (may be lost on redeploy)
- ❌ Limited to Railway's storage limits
- ❌ Not suitable for production

**Implementation**:
- Railway volumes are automatically mounted
- Files stored in `MEDIA_ROOT` persist in volumes
- **Warning**: May be lost during major updates

---

### Option 3: AWS S3 (Alternative)

**Best for**: If you already use AWS

**Setup**: Similar to R2 but use AWS credentials

**Environment Variables**:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_STORAGE_BUCKET_NAME`
- `AWS_S3_REGION_NAME`

---

### Recommended Storage Strategy

1. **Casebook PDF**: Store in Cloudflare R2
   - Upload once during initial setup
   - Accessible from all deployments
   - Fast retrieval for RAG

2. **User Recordings**: Store in Cloudflare R2
   - Persistent across deployments
   - Private access (use signed URLs)
   - No egress fees for playback

3. **Generated Cases**: Store in PostgreSQL (already implemented)
   - Cases are stored in `cases.Case` model
   - JSON fields for context and exhibits
   - No additional storage needed

4. **Static Files**: Served by WhiteNoise (Railway)
   - CSS, JavaScript, images
   - Collected during deployment
   - No additional storage needed

---

## Step-by-Step Deployment

### Step 1: Prepare Your Repository

1. Ensure all code is committed and pushed to GitHub:
   ```bash
   git add .
   git commit -m "Prepare for Railway deployment"
   git push origin main
   ```

2. Verify these files exist:
   - ✅ `Procfile`
   - ✅ `runtime.txt`
   - ✅ `requirements.txt`
   - ✅ `.gitignore` (excludes `.env`, `db.sqlite3`, etc.)

---

### Step 2: Create Railway Project

1. Go to https://railway.app and sign in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub account (if first time)
5. Select your repository (`mgt-802` or your repo name)
6. Railway will automatically detect Django and start building

---

### Step 3: Add PostgreSQL Database

1. In your Railway project, click **"+ New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway automatically:
   - Creates PostgreSQL instance
   - Sets `DATABASE_URL` environment variable
   - Provides connection details

4. **Note the connection details** (for local testing if needed)

---

### Step 4: Add Redis

1. In your Railway project, click **"+ New"**
2. Select **"Database"** → **"Add Redis"**
3. Railway automatically:
   - Creates Redis instance
   - Sets `REDIS_URL` environment variable

---

### Step 5: Configure Environment Variables

1. In Railway project, go to your **web service** (not database)
2. Click **"Variables"** tab
3. Add the following variables:

#### Required Variables:

```bash
SECRET_KEY=<your-generated-secret-key>
DEBUG=False
ALLOWED_HOSTS=<your-railway-domain>.railway.app
OPENAI_API_KEY=sk-<your-openai-key>
```

**Note**: 
- `DATABASE_URL` and `REDIS_URL` are automatically set by Railway
- `RAILWAY_PUBLIC_DOMAIN` is automatically set by Railway
- You can use `RAILWAY_PUBLIC_DOMAIN` in `ALLOWED_HOSTS` or set it manually

#### Optional Variables (if using):

```bash
# Cloudflare R2
CLOUDFLARE_R2_ACCOUNT_ID=<account-id>
CLOUDFLARE_R2_BUCKET_NAME=case-interview-simulator
CLOUDFLARE_R2_ACCESS_KEY_ID=<access-key>
CLOUDFLARE_R2_SECRET_ACCESS_KEY=<secret-key>
CLOUDFLARE_R2_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com

# Alternative APIs
ANTHROPIC_API_KEY=...
ASSEMBLYAI_API_KEY=...
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=...
PINECONE_INDEX_NAME=case-interviews
```

4. Click **"Save"** after adding each variable

---

### Step 6: Set Up Cloudflare R2 (Recommended)

1. **Create R2 Bucket**:
   - Go to Cloudflare dashboard → R2
   - Click **"Create bucket"**
   - Name: `case-interview-simulator`
   - Location: Choose closest to your Railway region

2. **Create API Token**:
   - Go to **"Manage R2 API Tokens"**
   - Click **"Create API Token"**
   - Name: `railway-deployment`
   - Permissions: **Object Read & Write**
   - Bucket: Select your bucket
   - Copy the **Access Key ID** and **Secret Access Key**

3. **Upload Casebook PDF**:
   - In R2 bucket, click **"Upload"**
   - Upload `Darden-Case-Book-2018-2019.pdf`
   - Note the file path/name

4. **Add R2 Variables to Railway**:
   - Add all `CLOUDFLARE_R2_*` variables from above

---

### Step 7: Deploy

1. Railway automatically deploys when you:
   - Push to your main branch, OR
   - Manually trigger deployment

2. **Monitor Deployment**:
   - Go to **"Deployments"** tab
   - Watch the build logs
   - Check for errors

3. **Expected Build Steps**:
   ```
   Installing dependencies...
   Running migrations...
   Collecting static files...
   Starting server...
   ```

---

### Step 8: Verify Deployment

1. **Check Build Logs**:
   - Look for: "Application startup complete"
   - No errors in red

2. **Access Your App**:
   - Railway provides URL: `https://<your-app>.railway.app`
   - Open in browser
   - Should see login page

3. **Check Database**:
   - Migrations should run automatically
   - Database should be initialized

---

## Post-Deployment Setup

### 1. Create Superuser

1. In Railway, go to your **web service**
2. Click **"Deployments"** → Latest deployment
3. Click **"View Logs"** → **"Shell"** (or use Railway CLI)
4. Run:
   ```bash
   python manage.py createsuperuser
   ```
5. Follow prompts to create admin account

---

### 2. Upload Casebook PDF to R2 (If Using)

**Option A: Via Cloudflare Dashboard**
1. Go to R2 bucket in Cloudflare
2. Click **"Upload"**
3. Upload `Darden-Case-Book-2018-2019.pdf`
4. Note the file name

**Option B: Via Management Command** (if implemented)
```bash
python manage.py upload_casebook_to_r2
```

**Option C: Via Railway Shell**
```bash
# If file is in your repo, you can upload via AWS CLI
aws s3 cp Darden-Case-Book-2018-2019.pdf s3://case-interview-simulator/ \
  --endpoint-url https://<account-id>.r2.cloudflarestorage.com
```

---

### 3. Seed Initial Cases (Optional)

1. In Railway shell:
   ```bash
   python manage.py seed_cases
   ```
   Or:
   ```bash
   python manage.py generate_candidate_cases
   ```

---

### 4. Configure Custom Domain (Optional)

1. In Railway project, go to **"Settings"** → **"Domains"**
2. Click **"Custom Domain"**
3. Enter your domain (e.g., `case-interview.yourdomain.com`)
4. Follow DNS configuration instructions
5. Update `ALLOWED_HOSTS` to include your custom domain

---

### 5. Set Up Monitoring

1. **Railway Metrics**:
   - Monitor CPU, Memory, Network usage
   - Set up alerts for high usage

2. **OpenAI Usage**:
   - Monitor API usage in OpenAI dashboard
   - Set up usage limits/alerts

3. **Error Tracking** (Optional):
   - Consider Sentry or similar for error tracking
   - Add to `requirements.txt` and configure

---

## Verification Checklist

After deployment, verify:

### Application
- [ ] App loads at Railway URL
- [ ] Login page displays
- [ ] Can create new user account
- [ ] Can log in successfully
- [ ] Dashboard loads

### Database
- [ ] Migrations ran successfully
- [ ] Can access admin panel (`/admin`)
- [ ] Can create superuser
- [ ] Database persists data

### WebSockets
- [ ] Can start an interview
- [ ] Chat messages send/receive in real-time
- [ ] No WebSocket connection errors

### Case Generation
- [ ] Can generate a case
- [ ] Case saves to database
- [ ] RAG works (if casebook uploaded)

### Recording
- [ ] Can start/stop recording
- [ ] Recording uploads successfully
- [ ] Transcription processes (check after a few minutes)

### Storage
- [ ] Casebook PDF accessible (if using R2)
- [ ] Recordings stored persistently
- [ ] Media files serve correctly

### API Keys
- [ ] OpenAI API works (case generation)
- [ ] Transcription works (if tested)
- [ ] No API key errors in logs

---

## Troubleshooting

### Build Fails

**Error**: `ModuleNotFoundError`
- **Solution**: Check `requirements.txt` has all dependencies
- Verify Python version in `runtime.txt` matches

**Error**: `Database connection failed`
- **Solution**: Ensure PostgreSQL service is running
- Check `DATABASE_URL` is set (auto-set by Railway)

**Error**: `Static files not found`
- **Solution**: Verify `collectstatic` runs in `Procfile`
- Check WhiteNoise is in `MIDDLEWARE`

---

### Runtime Errors

**Error**: `ERR_TOO_MANY_REDIRECTS`
- **Solution**: 
  - Set `SECURE_SSL_REDIRECT = False` (already in settings)
  - Verify `ALLOWED_HOSTS` matches Railway domain exactly
  - Check `CSRF_TRUSTED_ORIGINS` includes Railway domain

**Error**: `WebSocket connection failed`
- **Solution**: 
  - Ensure Redis service is running
  - Check `REDIS_URL` is set
  - Verify `CHANNEL_LAYERS` configuration

**Error**: `OPENAI_API_KEY not found`
- **Solution**: 
  - Verify API key is set in Railway variables
  - Check key starts with `sk-`
  - Ensure no extra spaces in variable value

---

### Storage Issues

**Error**: `Casebook PDF not found`
- **Solution**: 
  - If using R2: Verify file uploaded and path is correct
  - Check `CLOUDFLARE_R2_*` variables are set
  - Verify bucket permissions

**Error**: `Recording upload fails`
- **Solution**: 
  - Check file size limits
  - Verify media storage configuration
  - Check R2 bucket permissions (if using)

---

### Performance Issues

**Slow case generation**:
- Check OpenAI API rate limits
- Monitor API usage in OpenAI dashboard
- Consider upgrading OpenAI tier if needed

**High memory usage**:
- Check Railway resource limits
- Consider upgrading Railway plan
- Optimize case generation (reduce context size)

---

## Cost Estimation

### Railway
- **Hobby Plan**: $5/month (512MB RAM, 1GB storage)
- **Developer Plan**: $20/month (2GB RAM, 8GB storage)
- **Pro Plan**: $100/month (8GB RAM, 100GB storage)

### OpenAI
- **GPT-4o-mini**: ~$0.15-0.60 per 1M tokens
- **Whisper**: ~$0.006 per minute
- **Estimated**: $10-50/month for moderate usage

### Cloudflare R2
- **Free Tier**: 10GB storage, 1M operations/month
- **Paid**: $0.015/GB storage, $4.50 per 1M Class A operations

### Total Estimated Cost
- **Minimum**: ~$15-25/month (Railway Hobby + OpenAI)
- **Recommended**: ~$30-70/month (Railway Developer + OpenAI + R2)

---

## Next Steps

After successful deployment:

1. ✅ Test all features end-to-end
2. ✅ Set up monitoring and alerts
3. ✅ Configure backup strategy (database backups)
4. ✅ Document your deployment URL and credentials
5. ✅ Share with team/users
6. ✅ Set up CI/CD for automatic deployments

---

## Support Resources

- **Railway Docs**: https://docs.railway.app/
- **Django Deployment**: https://docs.djangoproject.com/en/4.2/howto/deployment/
- **Cloudflare R2 Docs**: https://developers.cloudflare.com/r2/
- **OpenAI API Docs**: https://platform.openai.com/docs/

---

## Security Reminders

⚠️ **Never commit**:
- `.env` files
- API keys
- `SECRET_KEY`
- Database credentials

✅ **Always**:
- Use environment variables for secrets
- Enable HTTPS (Railway does this automatically)
- Keep dependencies updated
- Monitor API usage
- Set up usage limits

---

**Last Updated**: 2024-12-07

