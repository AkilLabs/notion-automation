import logging
from datetime import datetime
from typing import List, Dict, Tuple

from github_integration.services import GitHubService
from notion_integration.services import NotionService


logger = logging.getLogger('automation')


class SyncResult:
    """Simple class to track sync results without database"""
    def __init__(self, sync_type: str = 'manual'):
        self.sync_type = sync_type
        self.started_at = datetime.now()
        self.completed_at = None
        self.issues_processed = 0
        self.issues_synced = 0
        self.errors_count = 0
        self.error_messages = []
        self.status = 'running'
    
    @property
    def duration(self):
        """Calculate sync duration"""
        end_time = self.completed_at or datetime.now()
        return end_time - self.started_at
    
    def mark_completed(self):
        self.status = 'completed'
        self.completed_at = datetime.now()
    
    def mark_failed(self, error_message=''):
        self.status = 'failed'
        self.completed_at = datetime.now()
        if error_message:
            self.error_messages.append(error_message)
    
    def add_error(self, error_message):
        self.errors_count += 1
        self.error_messages.append(error_message)


class AutomationService:
    """Main service for orchestrating GitHub to Notion synchronization"""
    
    def __init__(self):
        self.github_service = GitHubService()
        self.notion_service = NotionService()
    
    def sync_assigned_issues(self, sync_type: str = 'manual', state: str = 'open') -> SyncResult:
        """
        Main method to sync all assigned GitHub issues directly to Notion
        
        Args:
            sync_type: Type of sync ('manual', 'scheduled', 'webhook')
            state: Issue state to sync ('open', 'closed', 'all')
        
        Returns:
            SyncResult instance with sync results
        """
        # Create sync result tracker
        sync_result = SyncResult(sync_type)
        logger.info(f"Starting {sync_type} sync for {state} issues")
        
        try:
            # Fetch assigned issues from GitHub (only open issues by default)
            github_issues = self.github_service.get_assigned_issues(state=state)
            sync_result.issues_processed = len(github_issues)
            
            logger.info(f"Processing {len(github_issues)} GitHub issues")
            
            synced_count = 0
            
            for issue_data in github_issues:
                try:
                    success = self._process_single_issue(issue_data)
                    if success:
                        synced_count += 1
                    
                except Exception as e:
                    error_msg = f"Failed to process issue #{issue_data.get('id')}: {str(e)}"
                    logger.error(error_msg)
                    sync_result.add_error(error_msg)
            
            sync_result.issues_synced = synced_count
            
            if sync_result.errors_count == 0:
                sync_result.mark_completed()
                logger.info(f"Sync completed successfully. {synced_count}/{len(github_issues)} issues synced")
            else:
                sync_result.status = 'partial'
                sync_result.completed_at = datetime.now()
                logger.warning(f"Sync completed with errors. {synced_count}/{len(github_issues)} issues synced")
        
        except Exception as e:
            error_msg = f"Sync failed: {str(e)}"
            logger.error(error_msg)
            sync_result.mark_failed(error_msg)
        
        return sync_result
    
    def _process_single_issue(self, github_issue_data: Dict) -> bool:
        """
        Process a single GitHub issue and sync directly to Notion
        
        Args:
            github_issue_data: Raw GitHub API issue data
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Parse GitHub issue data
            parsed_data = self.github_service.parse_issue_data(github_issue_data)
            github_id = parsed_data.get('github_id')
            
            if not github_id:
                logger.warning("Issue missing GitHub ID, skipping")
                return False
            
            # Check if issue already exists in Notion by using the issue URL
            issue_url = parsed_data.get('html_url', '')
            existing_pages = self.notion_service.search_pages_by_issue_url(issue_url)
            
            if existing_pages:
                # Update existing Notion page
                page_id = existing_pages[0]['id']
                success = self.notion_service.update_issue_page(page_id, parsed_data)
                
                if success:
                    logger.info(f"Updated existing Notion page for issue #{github_id}")
                    return True
                else:
                    logger.warning(f"Failed to update Notion page for issue #{github_id}")
                    return False
            else:
                # Create new Notion page
                page_id = self.notion_service.create_issue_page(parsed_data)
                
                if page_id:
                    logger.info(f"Created new Notion page for issue #{github_id}")
                    return True
                else:
                    logger.warning(f"Failed to create Notion page for issue #{github_id}")
                    return False
                
        except Exception as e:
            logger.error(f"Failed to process issue: {e}")
            raise
    
    def sync_single_issue_by_url(self, github_url: str) -> Tuple[bool, str]:
        """
        Sync a single issue by GitHub URL
        
        Args:
            github_url: GitHub issue URL (e.g., https://github.com/owner/repo/issues/123)
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Parse GitHub URL to extract owner, repo, and issue number
            url_parts = github_url.strip('/').split('/')
            if len(url_parts) < 4 or 'github.com' not in github_url:
                return False, "Invalid GitHub URL format"
            
            owner = url_parts[-4]
            repo = url_parts[-3]
            issue_number = int(url_parts[-1])
            
            # Fetch issue data from GitHub
            github_data = self.github_service.get_issue_by_id(owner, repo, issue_number)
            
            # Process the issue
            success = self._process_single_issue(github_data)
            
            if success:
                return True, f"Successfully synced issue from {github_url}"
            else:
                return False, f"Failed to sync issue from {github_url}"
            
        except Exception as e:
            error_msg = f"Error syncing issue from {github_url}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def sync_repository_issues(self, owner: str, repo: str, assignee: str = None) -> SyncResult:
        """
        Sync all issues from a specific repository
        
        Args:
            owner: Repository owner
            repo: Repository name
            assignee: Filter by assignee (optional, defaults to configured username)
        
        Returns:
            SyncResult instance
        """
        sync_result = SyncResult('repository')
        assignee = assignee or self.github_service.username
        
        try:
            logger.info(f"Syncing issues from {owner}/{repo} assigned to {assignee}")
            
            # Get all issues for the repository
            all_issues = []
            page = 1
            
            while True:
                params = {
                    "assignee": assignee,
                    "state": "all",
                    "per_page": 100,
                    "page": page,
                    "sort": "updated",
                    "direction": "desc"
                }
                
                url = f"{self.github_service.base_url}/repos/{owner}/{repo}/issues"
                issues_data = self.github_service._make_request(url, params)
                
                if not issues_data:
                    break
                
                all_issues.extend(issues_data)
                
                if len(issues_data) < 100:
                    break
                
                page += 1
            
            sync_result.issues_processed = len(all_issues)
            synced_count = 0
            
            for issue_data in all_issues:
                try:
                    success = self._process_single_issue(issue_data)
                    if success:
                        synced_count += 1
                except Exception as e:
                    error_msg = f"Failed to process issue #{issue_data.get('id')}: {str(e)}"
                    sync_result.add_error(error_msg)
            
            sync_result.issues_synced = synced_count
            
            if sync_result.errors_count == 0:
                sync_result.mark_completed()
            else:
                sync_result.status = 'partial'
                sync_result.completed_at = datetime.now()
            
        except Exception as e:
            sync_result.mark_failed(str(e))
        
        return sync_result
    
    def get_sync_status(self) -> Dict:
        """
        Get current sync status and statistics (without database)
        
        Returns:
            Dictionary with sync statistics
        """
        try:
            # Get GitHub API rate limit info
            rate_limit = self.github_service.check_api_rate_limit()
            
            # Get basic info about assigned issues
            github_issues = self.github_service.get_assigned_issues(per_page=1)
            
            return {
                'github_issues_available': len(github_issues) if github_issues else 0,
                'github_rate_limit': rate_limit,
                'last_checked': datetime.now().isoformat(),
                'database_mode': False,
                'message': 'Running in direct sync mode (no local database)'
            }
            
        except Exception as e:
            logger.error(f"Failed to get sync status: {e}")
            return {'error': str(e)}
    
    def test_connections(self) -> Dict:
        """
        Test GitHub and Notion connections
        
        Returns:
            Dictionary with connection test results
        """
        results = {
            'github': {'status': 'unknown', 'message': ''},
            'notion': {'status': 'unknown', 'message': ''},
            'overall': 'unknown'
        }
        
        # Test GitHub connection
        try:
            rate_limit = self.github_service.check_api_rate_limit()
            results['github']['status'] = 'success'
            results['github']['message'] = f"Connected. Rate limit: {rate_limit['resources']['core']['remaining']}/{rate_limit['resources']['core']['limit']}"
        except Exception as e:
            results['github']['status'] = 'failed'
            results['github']['message'] = str(e)
        
        # Test Notion connection
        try:
            database_info = self.notion_service.get_database_info()
            database_title = database_info.get('title', [{}])[0].get('plain_text', 'Unnamed')
            results['notion']['status'] = 'success'
            results['notion']['message'] = f"Connected to database: {database_title}"
        except Exception as e:
            results['notion']['status'] = 'failed'
            results['notion']['message'] = str(e)
        
        # Overall status
        if results['github']['status'] == 'success' and results['notion']['status'] == 'success':
            results['overall'] = 'success'
        elif results['github']['status'] == 'success' or results['notion']['status'] == 'success':
            results['overall'] = 'partial'
        else:
            results['overall'] = 'failed'
        
        return results
