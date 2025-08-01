import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from notion_client import Client
from django.conf import settings
from ai_integration.services import GeminiService


logger = logging.getLogger('notion_integration')


class NotionService:
    """Service class for Notion API interactions"""
    
    def __init__(self):
        self.token = settings.NOTION_TOKEN
        self.database_id = settings.NOTION_DATABASE_ID
        
        if not self.token:
            raise ValueError("NOTION_TOKEN is required in environment variables")
        if not self.database_id:
            raise ValueError("NOTION_DATABASE_ID is required in environment variables")
        
        self.client = Client(auth=self.token)
        self.gemini_service = GeminiService()  # Initialize Gemini AI service
    
    def create_issue_page(self, issue_data: Dict) -> Optional[str]:
        """
        Create a new page in Notion database for a GitHub issue
        
        Args:
            issue_data: Parsed GitHub issue data
        
        Returns:
            Notion page ID if successful, None otherwise
        """
        try:
            # Prepare properties for the Notion page
            properties = self._build_page_properties(issue_data)
            
            # Create the page
            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            
            page_id = response.get('id')
            logger.info(f"Created Notion page for issue #{issue_data.get('github_id')}: {page_id}")
            
            # Add issue content as page content
            self._add_issue_content(page_id, issue_data)
            
            return page_id
            
        except Exception as e:
            logger.error(f"Failed to create Notion page for issue #{issue_data.get('github_id')}: {e}")
            return None
    
    def update_issue_page(self, page_id: str, issue_data: Dict) -> bool:
        """
        Update an existing Notion page with new issue data
        
        Args:
            page_id: Notion page ID
            issue_data: Updated GitHub issue data
        
        Returns:
            True if successful, False otherwise
        """
        try:
            properties = self._build_page_properties(issue_data)
            
            self.client.pages.update(
                page_id=page_id,
                properties=properties
            )
            
            logger.info(f"Updated Notion page {page_id} for issue #{issue_data.get('github_id')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update Notion page {page_id}: {e}")
            return False
    
    def _build_page_properties(self, issue_data: Dict) -> Dict:
        """
        Build Notion page properties adapted to the user's existing database structure
        
        Args:
            issue_data: Parsed GitHub issue data
        
        Returns:
            Dictionary of Notion properties
        """
        # For the existing database structure, we'll create issue-focused entries
        # but adapt them to the available properties
        
        repo_name = f"{issue_data.get('repository_owner')}/{issue_data.get('repository_name')}"
        issue_title = issue_data.get('title', '')
        issue_number = issue_data.get('number', 'Unknown')
        issue_state = issue_data.get('state', 'open')
        assignee = issue_data.get('assignee_login', '')
        
        # Use just the repository name as the title
        page_title = repo_name
        
        # Use Gemini AI to create an enhanced description
        enhanced_description = self.gemini_service.enhance_issue_description(issue_data)
        
        properties = {
            "Repository": {
                "title": [
                    {
                        "text": {
                            "content": page_title  # Use repository name as title
                        }
                    }
                ]
            },
            "Description": {
                "rich_text": [
                    {
                        "text": {
                            "content": enhanced_description
                        }
                    }
                ]
            },
            "Repository URL": {
                "url": issue_data.get('html_url', f"https://github.com/{repo_name}")
            },
            "Last Activity": {
                "rich_text": [
                    {
                        "text": {
                            "content": f"Updated: {issue_data.get('updated_at', 'Unknown')}"
                        }
                    }
                ]
            },
            "Issues": {
                "number": 1  # This represents one issue
            },
            "Assigned Issues": {
                "number": 1 if assignee else 0
            }
        }
        
        # Set priority based on labels if available
        labels = issue_data.get('labels', [])
        priority_labels = ['critical', 'high', 'urgent', 'important']
        
        for label in labels:
            label_name = label.get('name', '').lower()
            if any(priority in label_name for priority in priority_labels):
                if 'critical' in label_name or 'urgent' in label_name:
                    priority = "Critical"
                elif 'high' in label_name or 'important' in label_name:
                    priority = "High"
                else:
                    priority = "Medium"
                
                properties["Priority"] = {
                    "select": {
                        "name": priority
                    }
                }
                break
        
        return properties
    
    def _add_issue_content(self, page_id: str, issue_data: Dict) -> None:
        """
        Add the issue body as content to the Notion page
        
        Args:
            page_id: Notion page ID
            issue_data: GitHub issue data
        """
        try:
            body = issue_data.get('body', '')
            if not body:
                return
            
            # Split body into chunks if it's too long (Notion has limits)
            max_length = 2000  # Notion text block limit
            body_chunks = [body[i:i+max_length] for i in range(0, len(body), max_length)]
            
            blocks = []
            for chunk in body_chunks:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": chunk
                                }
                            }
                        ]
                    }
                })
            
            if blocks:
                self.client.blocks.children.append(
                    block_id=page_id,
                    children=blocks
                )
                
        except Exception as e:
            logger.warning(f"Failed to add content to Notion page {page_id}: {e}")
    
    def _format_date_for_notion(self, date_obj: Optional[datetime]) -> Optional[str]:
        """
        Format datetime object for Notion API
        
        Args:
            date_obj: Python datetime object
        
        Returns:
            ISO formatted date string or None
        """
        if not date_obj:
            return None
        
        try:
            return date_obj.isoformat()
        except Exception as e:
            logger.warning(f"Failed to format date {date_obj}: {e}")
            return None
    
    def get_database_info(self) -> Dict:
        """
        Get information about the Notion database
        
        Returns:
            Database information dictionary
        """
        try:
            response = self.client.databases.retrieve(database_id=self.database_id)
            return response
        except Exception as e:
            logger.error(f"Failed to retrieve database info: {e}")
            raise
    
    def search_pages_by_issue_url(self, issue_url: str) -> List[Dict]:
        """
        Search for existing Notion pages by exact GitHub issue URL to prevent duplicates
        
        Args:
            issue_url: GitHub issue URL (e.g., https://github.com/owner/repo/issues/1)
        
        Returns:
            List of matching Notion pages
        """
        try:
            # Search by exact Repository URL match
            response = self.client.databases.query(
                database_id=self.database_id,
                filter={
                    "property": "Repository URL",
                    "url": {
                        "equals": issue_url
                    }
                }
            )
            
            results = response.get('results', [])
            logger.info(f"Found {len(results)} existing pages for URL: {issue_url}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search for issue URL {issue_url}: {e}")
            return []

    def search_pages_by_issue_id(self, github_issue_id: int) -> List[Dict]:
        """
        Search for existing Notion pages by GitHub URL to prevent duplicates
        
        Args:
            github_issue_id: GitHub issue ID
        
        Returns:
            List of matching Notion pages
        """
        try:
            # First try to search by Repository URL (which contains the issue URL)
            response = self.client.databases.query(
                database_id=self.database_id,
                filter={
                    "property": "Repository URL",
                    "url": {
                        "contains": f"/issues/"
                    }
                }
            )
            
            results = response.get('results', [])
            
            # Filter results to find exact match for this issue ID
            matching_pages = []
            for page in results:
                properties = page.get('properties', {})
                repo_url_prop = properties.get('Repository URL', {})
                
                if repo_url_prop.get('type') == 'url':
                    url = repo_url_prop.get('url', '')
                    # Check if this URL contains our specific issue ID
                    if f"/issues/{github_issue_id}" in url or f"#{github_issue_id}" in url:
                        matching_pages.append(page)
            
            logger.info(f"Found {len(matching_pages)} existing pages for issue #{github_issue_id}")
            return matching_pages
            
        except Exception as e:
            logger.error(f"Failed to search for issue #{github_issue_id}: {e}")
            return []
    
    def create_database_if_not_exists(self, parent_page_id: str) -> str:
        """
        Create a new database for GitHub issues if it doesn't exist
        
        Args:
            parent_page_id: Parent Notion page ID
        
        Returns:
            Database ID
        """
        try:
            database_properties = {
                "Title": {"title": {}},
                "Issue ID": {"number": {}},
                "Status": {
                    "select": {
                        "options": [
                            {"name": "Open", "color": "green"},
                            {"name": "Closed", "color": "red"}
                        ]
                    }
                },
                "Repository": {"rich_text": {}},
                "Assignee": {"rich_text": {}},
                "GitHub URL": {"url": {}},
                "Labels": {"multi_select": {"options": []}},
                "Created Date": {"date": {}},
                "Updated Date": {"date": {}},
                "Closed Date": {"date": {}}
            }
            
            response = self.client.databases.create(
                parent={"page_id": parent_page_id},
                title=[
                    {
                        "type": "text",
                        "text": {
                            "content": "GitHub Issues Dashboard"
                        }
                    }
                ],
                properties=database_properties
            )
            
            database_id = response.get('id')
            logger.info(f"Created new Notion database: {database_id}")
            return database_id
            
        except Exception as e:
            logger.error(f"Failed to create Notion database: {e}")
            raise
