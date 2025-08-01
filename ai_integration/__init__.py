import logging
import google.generativeai as genai
from typing import Dict, Optional
from django.conf import settings


logger = logging.getLogger('gemini_service')


class GeminiService:
    """Service class for Gemini AI interactions"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'GEMINI_API_KEY', None)
        
        if not self.api_key or self.api_key == 'your-gemini-api-key-here':
            logger.warning("GEMINI_API_KEY is not configured. AI descriptions will be disabled.")
            self.enabled = False
            return
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.enabled = True
            logger.info("Gemini AI service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI: {e}")
            self.enabled = False
    
    def enhance_issue_description(self, issue_data: Dict) -> str:
        """
        Use Gemini AI to generate an enhanced description for a GitHub issue
        
        Args:
            issue_data: Parsed GitHub issue data
        
        Returns:
            Enhanced description string
        """
        if not self.enabled:
            return self._create_basic_description(issue_data)
        
        try:
            # Prepare the prompt for Gemini
            prompt = self._build_enhancement_prompt(issue_data)
            
            # Generate enhanced description
            response = self.model.generate_content(prompt)
            enhanced_description = response.text
            
            logger.info(f"Generated enhanced description for issue #{issue_data.get('number')}")
            return enhanced_description
            
        except Exception as e:
            logger.warning(f"Failed to generate AI description for issue #{issue_data.get('number')}: {e}")
            return self._create_basic_description(issue_data)
    
    def _build_enhancement_prompt(self, issue_data: Dict) -> str:
        """
        Build a prompt for Gemini to enhance the issue description
        
        Args:
            issue_data: GitHub issue data
        
        Returns:
            Formatted prompt string
        """
        repo_name = f"{issue_data.get('repository_owner')}/{issue_data.get('repository_name')}"
        issue_title = issue_data.get('title', '')
        issue_number = issue_data.get('number', 'Unknown')
        issue_state = issue_data.get('state', 'open')
        assignee = issue_data.get('assignee_login', 'Not assigned')
        labels = [label.get('name', '') for label in issue_data.get('labels', [])]
        issue_body = issue_data.get('body', '')
        created_at = issue_data.get('created_at', '')
        updated_at = issue_data.get('updated_at', '')
        
        prompt = f"""
Create a professional and well-formatted description for a GitHub issue entry in a Notion database. 

Here's the GitHub issue information:
- Repository: {repo_name}
- Issue #{issue_number}: {issue_title}
- Status: {issue_state.title()}
- Assignee: {assignee}
- Labels: {', '.join(labels) if labels else 'None'}
- Created: {created_at}
- Updated: {updated_at}
- GitHub URL: {issue_data.get('html_url', '')}

Original Issue Description:
{issue_body if issue_body else 'No description provided'}

Please create a concise, professional description that:
1. Summarizes the issue clearly
2. Highlights the key points and requirements
3. Mentions any important technical details
4. Includes the current status and assignee
5. Keeps it under 500 words
6. Uses markdown formatting for better readability

Format it as a well-structured description suitable for a project management dashboard.
"""
        
        return prompt
    
    def _create_basic_description(self, issue_data: Dict) -> str:
        """
        Create a basic description without AI enhancement
        
        Args:
            issue_data: GitHub issue data
        
        Returns:
            Basic formatted description
        """
        repo_name = f"{issue_data.get('repository_owner')}/{issue_data.get('repository_name')}"
        issue_title = issue_data.get('title', '')
        issue_number = issue_data.get('number', 'Unknown')
        issue_state = issue_data.get('state', 'open')
        assignee = issue_data.get('assignee_login', 'Not assigned')
        labels = [label.get('name', '') for label in issue_data.get('labels', [])]
        
        description_parts = [
            f"**Issue #{issue_number}:** {issue_title}",
            f"**Repository:** {repo_name}",
            f"**Status:** {issue_state.title()}",
            f"**Assignee:** {assignee}",
            f"**GitHub URL:** {issue_data.get('html_url', '')}",
        ]
        
        if labels:
            description_parts.append(f"**Labels:** {', '.join(labels)}")
        
        if issue_data.get('body'):
            body_preview = issue_data.get('body')[:300]
            if len(issue_data.get('body', '')) > 300:
                body_preview += "..."
            description_parts.append(f"**Description:**\n{body_preview}")
        
        return "\n".join(description_parts)
    
    def summarize_repository_activity(self, issues: list) -> str:
        """
        Generate a summary of repository activity based on issues
        
        Args:
            issues: List of issue data
        
        Returns:
            Summary description
        """
        if not self.enabled or not issues:
            return f"Repository has {len(issues)} assigned issues"
        
        try:
            # Prepare summary prompt
            repo_name = f"{issues[0].get('repository_owner')}/{issues[0].get('repository_name')}"
            issue_summaries = []
            
            for issue in issues:
                issue_summaries.append(
                    f"- Issue #{issue.get('number')}: {issue.get('title')} ({issue.get('state')})"
                )
            
            prompt = f"""
Analyze the following GitHub issues for repository {repo_name} and create a brief summary of the current activity and status:

Issues:
{chr(10).join(issue_summaries)}

Provide a concise 2-3 sentence summary that highlights:
1. Overall repository activity level
2. Key issues or themes
3. Current status overview

Keep it professional and informative for a project dashboard.
"""
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.warning(f"Failed to generate repository summary: {e}")
            return f"Repository {repo_name} has {len(issues)} assigned issues"
