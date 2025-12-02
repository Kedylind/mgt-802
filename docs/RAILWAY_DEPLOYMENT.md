# Railway Deployment Guide

This guide will help you deploy the AI Case Interview Simulator to Railway.

## Prerequisites

1. A Railway account (sign up at https://railway.app)
2. Your code pushed to a Git repository (GitHub, GitLab, or Bitbucket)

## Step 1: Create a New Project on Railway

1. Go to https://railway.app and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo" (or your Git provider)
4. Select your repository

## Step 2: Add a PostgreSQL Database

1. In your Railway project, click "+ New"
2. Select "Database" → "Add PostgreSQL"
3. Railway will automatically create a PostgreSQL database
4. Note the connection details (you'll need the DATABASE_URL)

## Step 3: Add Redis (for WebSockets)

1. In your Railway project, click "+ New"
2. Select "Database" → "Add Redis"
3. Railway will automatically create a Redis instance
4. Note the connection details (you'll need the REDIS_URL)

## Step 4: Configure Environment Variables

In your Railway project, go to "Variables" and add the following:

### Required Variables:

```
SECRET_KEY=<generate-a-secure-random-key>
DEBUG=False
ALLOWED_HOSTS=your-app-name.railway.app
DATABASE_URL=<automatically-set-by-railway-postgres>
REDIS_URL=<automatically-set-by-railway-redis>
```

### Optional API Keys (if using AI features):

```
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
ASSEMBLYAI_API_KEY=your-assemblyai-key
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=your-pinecone-env
PINECONE_INDEX_NAME=case-interviews
```

### How to Generate SECRET_KEY:

Run this command locally:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Or use:
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

## Step 5: Deploy

1. Railway will automatically detect your project and start building
2. The deployment will:
   - Install dependencies from `requirements.txt`
   - Run database migrations
   - Collect static files
   - Start the Gunicorn server

## Step 6: Create a Superuser

After deployment, you need to create a superuser to access the admin panel:

1. In Railway, go to your service
2. Click on the service → "Deployments" → Click on the latest deployment
3. Click "View Logs" → "Shell"
4. Run:
   ```bash
   python manage.py createsuperuser
   ```
5. Follow the prompts to create your admin account

## Step 7: Access Your Application

1. Railway will provide you with a public URL (e.g., `your-app.railway.app`)
2. Access your app at: `https://your-app.railway.app`
3. Access admin at: `https://your-app.railway.app/admin`

## Important Notes

### Database
- **DO NOT** commit `db.sqlite3` to git (it's already in `.gitignore`)
- Railway will use PostgreSQL automatically via the `DATABASE_URL` environment variable
- Your local SQLite database will NOT be deployed

### Static Files
- Static files are collected during deployment using `collectstatic`
- WhiteNoise middleware serves static files in production
- Media files (user uploads) should be stored in Railway's volume or use a service like S3

### WebSockets
- Redis is required for WebSocket functionality
- If Redis is not configured, the app will fall back to in-memory channel layer (not recommended for production)

### Environment Variables
- Never commit `.env` files to git
- All secrets should be set in Railway's environment variables
- Railway automatically provides `DATABASE_URL` and `REDIS_URL` when you add those services

## Troubleshooting

### Build Fails
- Check that `requirements.txt` has all dependencies
- Verify Python version in `runtime.txt` matches Railway's supported versions

### Database Connection Errors
- Ensure PostgreSQL service is added and running
- Check that `DATABASE_URL` is set correctly (Railway sets this automatically)

### Static Files Not Loading
- Verify `collectstatic` ran during deployment
- Check that `STATIC_ROOT` is set correctly
- Ensure WhiteNoise is in `MIDDLEWARE`

### WebSocket Errors
- Ensure Redis service is added and running
- Check that `REDIS_URL` is set correctly
- Verify `CHANNEL_LAYERS` configuration in settings

## Monitoring

- View logs in Railway dashboard
- Check deployment status
- Monitor resource usage (CPU, Memory, Network)

## Updating Your Deployment

Simply push to your Git repository's main branch, and Railway will automatically redeploy!

```bash
git add .
git commit -m "Your changes"
git push origin main
```

