#!/usr/bin/env python3
"""
Clean up duplicate entries and fix repository URLs
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

def clean_duplicate_entries():
    """Clean up duplicate entries and fix repository URLs"""
    print("🧹 Cleaning up duplicate entries and fixing repository URLs...")
    
    try:
        client = Client(auth=settings.NOTION_TOKEN)
        database_id = settings.NOTION_DATABASE_ID
        
        # Get all pages from the database
        response = client.databases.query(database_id=database_id)
        pages = response.get('results', [])
        
        print(f"📊 Found {len(pages)} total pages in database")
        
        # Group pages by repository name to find duplicates
        repo_groups = {}
        issue_pages = []
        
        for page in pages:
            properties = page.get('properties', {})
            
            # Check if this looks like an issue entry (has "Issue #" in title or description)
            title_prop = properties.get('Repository', {})
            if title_prop.get('type') == 'title':
                title_content = title_prop.get('title', [])
                if title_content:
                    title_text = title_content[0].get('plain_text', '')
                    if 'Issue #' in title_text:
                        issue_pages.append({
                            'page_id': page['id'],
                            'title': title_text,
                            'url': page['url']
                        })
        
        print(f"🔍 Found {len(issue_pages)} issue-related pages")
        
        if issue_pages:
            print("\nIssue pages found:")
            for i, page in enumerate(issue_pages, 1):
                print(f"   {i}. {page['title']}")
            
            # Ask user what to do
            print(f"\n🤔 Would you like to:")
            print("1. Delete all issue pages (they'll be recreated correctly)")
            print("2. Keep them and just run the sync to create correct entries")
            print("3. Cancel and do nothing")
            
            choice = input("Enter your choice (1-3): ").strip()
            
            if choice == '1':
                print(f"\n🗑️ Deleting {len(issue_pages)} issue pages...")
                for page in issue_pages:
                    try:
                        client.pages.update(
                            page_id=page['page_id'],
                            archived=True
                        )
                        print(f"   ✅ Archived: {page['title']}")
                    except Exception as e:
                        print(f"   ❌ Failed to archive {page['title']}: {e}")
                
                print(f"\n✅ Cleanup complete! Now run the sync to create correct entries:")
                print("python manage.py sync_github_issues")
                
            elif choice == '2':
                print(f"\n⏭️ Keeping existing pages. Run sync to create correct entries:")
                print("python manage.py sync_github_issues")
                
            else:
                print("❌ Operation cancelled")
        else:
            print("✅ No issue pages found to clean up")
            print("Run the sync to create entries with correct repository URLs:")
            print("python manage.py sync_github_issues")
        
    except Exception as e:
        print(f"❌ Failed to clean up entries: {e}")

if __name__ == '__main__':
    clean_duplicate_entries()
