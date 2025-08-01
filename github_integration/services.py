import requests
import logging
from datetime import datetime
from typing import List, Dict, Optional
from django.conf import settings


logger = logging.getLogger('github_integration')


class GitHubService:
    """Service class for GitHub API interactions"""
    
    def __init__(self):
        self.token = settings.GITHUB_TOKEN
        self.username = settings.GITHUB_USERNAME
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        if not self.token:
            raise ValueError("GITHUB_TOKEN is required in environment variables")
        if not self.username:
            raise ValueError("GITHUB_USERNAME is required in environment variables")
    
    def _make_request(self, url: str, params: Optional[Dict] = None) -> Dict:
        """Make authenticated request to GitHub API"""
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API request failed: {e}")
            raise
    
    def get_assigned_issues(self, state: str = "open", per_page: int = 100) -> List[Dict]:
        """
        Fetch all issues assigned to the authenticated user
        
        Args:
            state: Issue state ('open', 'closed', 'all') - defaults to 'open'
            per_page: Number of issues per page (max 100)
        
        Returns:
            List of issue dictionaries
        """
        logger.info(f"Fetching assigned issues for user: {self.username}")
        
        all_issues = []
        page = 1
        
        while True:
            params = {
                "assignee": self.username,
                "state": state,
                "per_page": per_page,
                "page": page,
                "sort": "updated",
                "direction": "desc"
            }
            
            url = f"{self.base_url}/issues"
            issues_data = self._make_request(url, params)
            
            if not issues_data:
                break
            
            all_issues.extend(issues_data)
            logger.info(f"Fetched page {page} with {len(issues_data)} issues")
            
            # If we got less than per_page items, we're done
            if len(issues_data) < per_page:
                break
            
            page += 1
        
        logger.info(f"Total assigned issues fetched: {len(all_issues)}")
        return all_issues
    
    def get_issue_by_id(self, owner: str, repo: str, issue_number: int) -> Dict:
        """
        Fetch a specific issue by repository and issue number
        
        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: Issue number
        
        Returns:
            Issue dictionary
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}"
        return self._make_request(url)
    
    def get_user_repositories(self, type_filter: str = "all") -> List[Dict]:
        """
        Get repositories for the authenticated user
        
        Args:
            type_filter: Repository type ('all', 'owner', 'public', 'private', 'member')
        
        Returns:
            List of repository dictionaries
        """
        params = {
            "type": type_filter,
            "sort": "updated",
            "per_page": 100
        }
        
        url = f"{self.base_url}/user/repos"
        return self._make_request(url, params)
    
    def parse_issue_data(self, issue_data: Dict) -> Dict:
        """
        Parse GitHub issue data into a standardized format
        
        Args:
            issue_data: Raw GitHub API issue data
        
        Returns:
            Parsed issue dictionary
        """
        # Extract repository information from the URL
        repo_url = issue_data.get('repository_url', '')
        repo_parts = repo_url.split('/')
        repo_owner = repo_parts[-2] if len(repo_parts) >= 2 else ''
        repo_name = repo_parts[-1] if len(repo_parts) >= 1 else ''
        
        # Parse dates
        created_at = self._parse_github_date(issue_data.get('created_at'))
        updated_at = self._parse_github_date(issue_data.get('updated_at'))
        closed_at = self._parse_github_date(issue_data.get('closed_at'))
        
        # Extract assignee information
        assignee = issue_data.get('assignee', {})
        assignee_login = assignee.get('login', '') if assignee else ''
        
        # Extract labels
        labels = [
            {
                'name': label.get('name', ''),
                'color': label.get('color', ''),
                'description': label.get('description', '')
            }
            for label in issue_data.get('labels', [])
        ]
        
        return {
            'github_id': issue_data.get('id'),
            'number': issue_data.get('number'),
            'title': issue_data.get('title', ''),
            'body': issue_data.get('body', ''),
            'state': issue_data.get('state', 'open'),
            'assignee_login': assignee_login,
            'repository_name': repo_name,
            'repository_owner': repo_owner,
            'html_url': issue_data.get('html_url', ''),
            'created_at': created_at,
            'updated_at': updated_at,
            'closed_at': closed_at,
            'labels': labels,
        }
    
    def _parse_github_date(self, date_string: Optional[str]) -> Optional[datetime]:
        """Parse GitHub ISO date string to datetime object"""
        if not date_string:
            return None
        
        try:
            # GitHub returns dates in ISO format like: 2024-01-01T12:00:00Z
            return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        except (ValueError, AttributeError) as e:
            logger.warning(f"Failed to parse date '{date_string}': {e}")
            return None
    
    def check_api_rate_limit(self) -> Dict:
        """Check GitHub API rate limit status"""
        url = f"{self.base_url}/rate_limit"
        return self._make_request(url)
