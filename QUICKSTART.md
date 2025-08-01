# Quick Start Guide

## 1. Setup Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your values:
```env
GITHUB_TOKEN=ghp_your_github_token_here
GITHUB_USERNAME=your_github_username
NOTION_TOKEN=secret_your_notion_token_here
NOTION_DATABASE_ID=your_notion_database_id
```

## 2. Test Setup

Run the setup script to test connections:
```bash
python setup.py
```

Or test connections directly:
```bash
python manage.py sync_github_issues --test-connections
```

## 3. Manual Sync

Sync all your assigned GitHub issues:
```bash
python manage.py sync_github_issues
```

Sync a specific issue by URL:
```bash
python manage.py sync_github_issues --github-url https://github.com/owner/repo/issues/123
```

Sync all issues from a repository:
```bash
python manage.py sync_github_issues --repository owner/repo
```

## 4. Check Results

View sync status:
```bash
python manage.py sync_github_issues --status
```

## 5. Automate (Optional)

Set up a scheduled task or cron job to run:
```bash
python manage.py sync_github_issues --sync-type scheduled
```

## Common Commands

- **Full sync**: `python manage.py sync_github_issues`
- **Test connections**: `python manage.py sync_github_issues --test-connections`
- **Sync by URL**: `python manage.py sync_github_issues --github-url GITHUB_ISSUE_URL`
- **Sync repository**: `python manage.py sync_github_issues --repository owner/repo`
- **Check status**: `python manage.py sync_github_issues --status`

## VS Code Tasks

Use Ctrl+Shift+P → "Tasks: Run Task":
- "Sync GitHub Issues to Notion"
- "Check Sync Status"
- "Test API Connections"
