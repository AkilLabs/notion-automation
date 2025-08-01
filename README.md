# GitHub to Notion Automation

A Django-based automation system that synchronizes your assigned GitHub issues directly to a Notion dashboard, making it easy to track and manage your tasks in one place.

## Features

- **Direct Sync**: Fetches GitHub issues and creates/updates Notion pages directly without local database
- **Real-time Updates**: Keeps issue status, labels, and content synchronized between GitHub and Notion
- **Multiple Sync Options**: Sync all assigned issues, specific repositories, or individual issues by URL
- **Connection Testing**: Built-in tools to verify GitHub and Notion API connectivity
- **Management Commands**: CLI commands for all sync operations
- **Rate Limit Handling**: Respects GitHub API rate limits and provides status information

## Project Structure

```
notion_github_automation/
├── automation/                 # Main automation logic
│   ├── management/commands/    # Django management commands
│   └── services.py            # Direct sync orchestration (no database)
├── github_integration/         # GitHub API integration
│   └── services.py            # GitHub API client and data parsing
├── notion_integration/         # Notion API integration
│   └── services.py            # Notion API client and page management
└── notion_github_automation/   # Django project settings
    └── settings.py            # Configuration and API settings
```

## Prerequisites

- Python 3.8+
- Django 5.1+
- GitHub Personal Access Token
- Notion Integration Token
- Notion Database ID

## Installation

1. **Clone and Setup**:
   ```bash
   git clone <your-repo>
   cd notion_automation
   pip install django python-dotenv requests notion-client
   ```

2. **Configure Environment**:
   Create a `.env` file in the project root:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   
   # GitHub API Configuration
   GITHUB_TOKEN=your-github-personal-access-token
   GITHUB_USERNAME=your-github-username
   
   # Notion API Configuration
   NOTION_TOKEN=your-notion-integration-token
   NOTION_DATABASE_ID=your-notion-database-id
   
   LOG_LEVEL=INFO
   ```

3. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Create Superuser** (optional, for admin access):
   ```bash
   python manage.py createsuperuser
   ```

## Setup Instructions

### 1. GitHub Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token with these scopes:
   - `repo` (for private repos) or `public_repo` (for public repos only)
   - `read:user` (to read user information)
3. Copy the token to your `.env` file as `GITHUB_TOKEN`

### 2. Notion Integration

1. **Create Notion Integration**:
   - Go to [Notion Developers](https://developers.notion.com/)
   - Create a new integration
   - Copy the Internal Integration Token to your `.env` file as `NOTION_TOKEN`

2. **Create Notion Database**:
   - Create a new page in Notion
   - Add a database with these properties:
     - `Title` (Title)
     - `Issue ID` (Number)
     - `Status` (Select: Open, Closed)
     - `Repository` (Text)
     - `Assignee` (Text)
     - `GitHub URL` (URL)
     - `Labels` (Multi-select)
     - `Created Date` (Date)
     - `Updated Date` (Date)
     - `Closed Date` (Date)

3. **Get Database ID**:
   - Share your database with your integration
   - Copy the database ID from the URL: `https://notion.so/yourworkspace/DATABASE_ID?v=...`
   - Add it to your `.env` file as `NOTION_DATABASE_ID`

## Usage

### Command Line Interface

**Full Sync** (sync all assigned issues):
```bash
python manage.py sync_github_issues
```

**Test API Connections**:
```bash
python manage.py sync_github_issues --test-connections
```

**Sync Single Issue by URL**:
```bash
python manage.py sync_github_issues --github-url https://github.com/owner/repo/issues/123
```

**Sync Repository Issues**:
```bash
python manage.py sync_github_issues --repository owner/repo
```

**Check Status**:
```bash
python manage.py sync_github_issues --status
```

**Scheduled Sync**:
```bash
python manage.py sync_github_issues --sync-type scheduled
```

### Django Admin Interface

The Django admin is not needed for this direct sync approach. All operations are performed via command line.

### Web Interface (Optional)

Start the development server to access the Django admin:
```bash
python manage.py runserver
```

## Configuration Options

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GITHUB_TOKEN` | GitHub Personal Access Token | Yes |
| `GITHUB_USERNAME` | Your GitHub username | Yes |
| `NOTION_TOKEN` | Notion Integration Token | Yes |
| `NOTION_DATABASE_ID` | Notion Database ID | Yes |
| `SECRET_KEY` | Django secret key | Yes |
| `DEBUG` | Debug mode (True/False) | No |
| `LOG_LEVEL` | Logging level (DEBUG/INFO/WARNING/ERROR) | No |

### Sync Types

- **Manual**: Triggered manually via command line
- **Scheduled**: For use with cron jobs or task schedulers
- **Webhook**: For future webhook integration

## Automation Setup

### Cron Job (Linux/macOS)

Add to your crontab to run sync every hour:
```bash
0 * * * * cd /path/to/your/project && python manage.py sync_github_issues --sync-type scheduled
```

### Task Scheduler (Windows)

Create a scheduled task that runs:
```cmd
C:\path\to\python.exe C:\path\to\your\project\manage.py sync_github_issues --sync-type scheduled
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**:
   - Verify your GitHub token has correct permissions
   - Check that your Notion integration has access to the database

2. **Rate Limit Issues**:
   - GitHub API has rate limits (5000 requests/hour for authenticated users)
   - Use `--status` flag to check current rate limit

3. **Notion Database Errors**:
   - Ensure your database has all required properties
   - Verify the database ID is correct
   - Check that the integration has write access

4. **Sync Failures**:
   - Check logs in `automation.log`
   - Use Django admin to view detailed error messages
   - Run with `LOG_LEVEL=DEBUG` for verbose output

### Debug Mode

Enable debug logging:
```env
LOG_LEVEL=DEBUG
DEBUG=True
```

Then run:
```bash
python manage.py sync_github_issues --status
```

## API Documentation

### GitHub API Usage

The system uses GitHub REST API v3 to:
- Fetch assigned issues: `GET /issues?assignee={username}`
- Get repository information
- Handle pagination automatically
- Respect rate limits

### Notion API Usage

The system uses Notion API v1 to:
- Create database pages
- Update existing pages
- Query existing issues
- Handle rich text content

## Development

### Adding Features

1. **Custom Fields**: Modify `NotionService._build_page_properties()` to add new Notion properties
2. **Filters**: Update `GitHubService.get_assigned_issues()` to add issue filtering
3. **Webhooks**: Extend the automation service to handle GitHub webhooks

### Testing

Run the Django development server:
```bash
python manage.py runserver
```

Test the sync manually:
```bash
python manage.py sync_github_issues --issue-id YOUR_ISSUE_ID
```

## Security Considerations

- Store sensitive tokens in environment variables, never in code
- Use HTTPS for production deployments
- Regularly rotate your GitHub and Notion tokens
- Review GitHub token permissions regularly

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in `automation.log`
3. Create an issue in the GitHub repository
