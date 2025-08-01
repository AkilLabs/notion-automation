#!/usr/bin/env python3
"""
Create a new Notion database for GitHub issues
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

def create_issues_database():
    """Create a new database specifically for GitHub issues"""
    print("🔧 Creating new GitHub Issues database...")
    
    try:
        client = Client(auth=settings.NOTION_TOKEN)
        
        # You'll need to provide a parent page ID
        print("❗ To create a new database, I need a parent page ID.")
        print("   1. Go to any page in your Notion workspace")
        print("   2. Copy the page URL")
        print("   3. Extract the page ID from the URL")
        print("   Example: https://notion.so/workspace/PAGE_ID")
        print()
        
        # For now, let's show what the database properties should look like
        database_properties = {
            "Title": {"title": {}},
            "Issue ID": {"number": {}},
            "Status": {
                "select": {
                    "options": [
                        {"name": "Open", "color": "green"},
                        {"name": "Closed", "color": "red"},
                        {"name": "In Progress", "color": "yellow"}
                    ]
                }
            },
            "Repository": {"rich_text": {}},
            "Assignee": {"rich_text": {}},
            "GitHub URL": {"url": {}},
            "Labels": {"multi_select": {"options": []}},
            "Priority": {
                "select": {
                    "options": [
                        {"name": "High", "color": "red"},
                        {"name": "Medium", "color": "yellow"},
                        {"name": "Low", "color": "blue"}
                    ]
                }
            },
            "Created Date": {"date": {}},
            "Updated Date": {"date": {}},
            "Closed Date": {"date": {}}
        }
        
        print("🎯 The new database should have these properties:")
        for prop_name, prop_config in database_properties.items():
            prop_type = list(prop_config.keys())[0]
            print(f"   • {prop_name} ({prop_type})")
        
        print("\n" + "="*50)
        print("📋 Manual Steps:")
        print("1. Create a new page in Notion")
        print("2. Add a database with the properties listed above")
        print("3. Share the database with your integration")
        print("4. Copy the database ID and update your .env file")
        print("5. Or provide a parent page ID to create it automatically")
        
        return database_properties
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {}

if __name__ == '__main__':
    create_issues_database()
