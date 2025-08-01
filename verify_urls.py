#!/usr/bin/env python3
"""
Verify repository URLs in the database
"""

import os
import sys
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notion_github_automation.settings')
import django
django.setup()

from notion_client import Client
from django.conf import settings

def verify_repository_urls():
    """Verify that repository URLs are correctly formatted"""
    print("🔍 Verifying repository URLs in Notion database...")
    
    try:
        client = Client(auth=settings.NOTION_TOKEN)
        database_id = settings.NOTION_DATABASE_ID
        
        # Get all pages from the database
        response = client.databases.query(database_id=database_id)
        pages = response.get('results', [])
        
        print(f"📊 Found {len(pages)} total pages in database")
        print("\nRepository URLs:")
        print("=" * 60)
        
        for i, page in enumerate(pages, 1):
            properties = page.get('properties', {})
            
            # Get repository name (title)
            title_prop = properties.get('Repository', {})
            title = "Unknown"
            if title_prop.get('type') == 'title' and title_prop.get('title'):
                title = title_prop['title'][0].get('plain_text', 'Unknown')
            
            # Get repository URL
            url_prop = properties.get('Repository URL', {})
            repo_url = "No URL"
            if url_prop.get('type') == 'url':
                repo_url = url_prop.get('url', 'No URL')
            
            print(f"{i}. {title}")
            print(f"   URL: {repo_url}")
            
            # Check if URL format is correct
            if repo_url and repo_url != "No URL":
                if "/issues/" in repo_url:
                    print("   ❌ ISSUE: Contains '/issues/' - should be just repository URL")
                elif repo_url.startswith("https://github.com/") and repo_url.count("/") == 4:
                    print("   ✅ CORRECT: Proper repository URL format")
                else:
                    print("   ⚠️  UNKNOWN: Unexpected URL format")
            else:
                print("   ⚠️  MISSING: No repository URL found")
            
            print()
        
    except Exception as e:
        print(f"❌ Failed to verify URLs: {e}")

if __name__ == '__main__':
    verify_repository_urls()
