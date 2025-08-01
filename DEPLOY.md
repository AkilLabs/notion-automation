# GitHub-Notion Automation - Render Deployment

This Django application automatically syncs your assigned GitHub issues to a Notion database with AI-enhanced descriptions powered by Gemini.

## 🚀 Deploy to Render

### Step 1: Prepare Your Repository

1. Push your code to GitHub:
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

### Step 2: Deploy on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:

   **Basic Settings:**
   - **Name**: `notion-github-automation`
   - **Region**: Choose your preferred region
   - **Branch**: `main`
   - **Root Directory**: Leave empty
   - **Runtime**: `Python 3`

   **Build & Deploy:**
   - **Build Command**: `chmod +x build.sh && ./build.sh`
   - **Start Command**: `gunicorn notion_github_automation.wsgi:application`

### Step 3: Environment Variables

Add these environment variables in Render:

```
# Django Settings
SECRET_KEY=your-secure-django-secret-key
DEBUG=False
RENDER=True

# GitHub API Configuration
GITHUB_TOKEN=your-github-personal-access-token
GITHUB_USERNAME=your-github-username

# Notion API Configuration
NOTION_TOKEN=your-notion-integration-token
NOTION_DATABASE_ID=your-notion-database-id

# Gemini AI Configuration
GEMINI_API_KEY=your-gemini-api-key

# Logging
LOG_LEVEL=INFO
```

### Step 4: Generate Secret Key

Generate a secure Django secret key:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

## 🔧 API Endpoints

Once deployed, your service will have these endpoints:

- **Health Check**: `GET /api/health/`
- **Manual Sync (POST)**: `POST /api/sync/manual/`
- **Manual Sync (GET)**: `GET /api/sync/` (supports `?state=open|closed|all`)
- **Webhook Sync**: `POST /api/sync/webhook/`
- **Sync Status**: `GET /api/sync/status/`

## 🎯 Usage Examples

### Manual Sync via API (only open issues)
```bash
curl -X POST https://your-app.onrender.com/api/sync/manual/
```

### Manual Sync via GET (with state parameter)
```bash
# Sync only open issues (default)
curl "https://your-app.onrender.com/api/sync/?state=open"

# Sync all issues (including closed)
curl "https://your-app.onrender.com/api/sync/?state=all"

# Sync only closed issues
curl "https://your-app.onrender.com/api/sync/?state=closed"
```

### Health Check
```bash
curl https://your-app.onrender.com/api/health/
```

### Status Check
```bash
curl https://your-app.onrender.com/api/sync/status/
```

## 🔗 GitHub Webhook Setup (Optional)

To automatically sync when issues are updated:

1. Go to your GitHub repository
2. Settings → Webhooks → Add webhook
3. **Payload URL**: `https://your-app.onrender.com/api/sync/webhook/`
4. **Content type**: `application/json`
5. **Events**: Select "Issues"
6. Click "Add webhook"

## 📋 Features

✅ **Automatic Sync**: Syncs assigned GitHub issues to Notion  
✅ **AI Descriptions**: Uses Gemini AI for enhanced issue descriptions  
✅ **Duplicate Prevention**: Won't create duplicate entries  
✅ **Web API**: Manual and webhook-triggered sync  
✅ **Production Ready**: Configured for Render deployment  

## 🔄 Manual Sync Options

### Command Line (locally or via Render console)
```bash
# Sync only open issues (default)
python manage.py sync_github_issues --state open

# Sync all issues (including closed)
python manage.py sync_github_issues --state all

# Sync only closed issues
python manage.py sync_github_issues --state closed
```

## 🔄 Scheduled Sync (Optional)

You can set up scheduled sync using Render's Cron Jobs:

1. Create a new "Cron Job" service
2. **Command**: `python manage.py sync_github_issues`
3. **Schedule**: `0 */6 * * *` (every 6 hours)

## 🐛 Troubleshooting

- Check logs in Render dashboard
- Verify all environment variables are set
- Test endpoints manually
- Ensure GitHub token has proper permissions
- Verify Notion integration is connected to your database

## 📞 Support

If you encounter issues:
1. Check the deployment logs in Render
2. Verify your API keys and tokens
3. Test the endpoints manually
4. Review the GitHub and Notion API permissions
