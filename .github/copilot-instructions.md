<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Notion GitHub Automation Project

This is a Django-based automation project that synchronizes GitHub assigned issues to a Notion dashboard.

## Project Structure
- `github_integration/` - Handles GitHub API interactions and fetching assigned issues
- `notion_integration/` - Manages Notion API operations and database updates
- `automation/` - Contains the main automation logic and orchestration

## Key Features
- Fetches assigned GitHub issues for authenticated users
- Creates and updates corresponding pages in Notion databases
- Maintains synchronization between GitHub issue status and Notion entries
- Supports environment-based configuration for API keys

## API Integration Guidelines
- Use GitHub REST API v4 for fetching issues
- Use Notion API v1 for database operations
- Implement proper error handling and rate limiting
- Use environment variables for sensitive credentials

## Development Notes
- Follow Django best practices for app organization
- Use Django management commands for automation tasks
- Implement proper logging for debugging and monitoring
- Consider using Django signals for event-driven updates
