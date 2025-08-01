#!/usr/bin/env python3
"""
Find all Notion databases to locate the correct one for issues
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

def find_all_databases():
    """Find all accessible Notion databases"""
    print("🔍 Finding all accessible Notion databases...")
    
    try:
        client = Client(auth=settings.NOTION_TOKEN)
        
        # Search for all databases
        search_results = client.search(
            filter={
                "property": "object", 
                "value": "database"
            }
        )
        
        databases = search_results.get('results', [])
        
        if not databases:
            print("❌ No databases found. Make sure to share databases with your integration.")
            return
        
        print(f"✅ Found {len(databases)} database(s):")
        print()
        
        for i, db in enumerate(databases, 1):
            db_id = db.get('id', 'Unknown')
            db_title = 'Unnamed'
            
            # Get database title
            title_property = db.get('title', [])
            if title_property and len(title_property) > 0:
                db_title = title_property[0].get('plain_text', 'Unnamed')
            
            print(f"{i}. {db_title}")
            print(f"   ID: {db_id}")
            
            # Check if this is the current database
            current_db_id = settings.NOTION_DATABASE_ID.replace('-', '')
            if db_id.replace('-', '') == current_db_id:
                print("   ⭐ CURRENTLY USED")
            
            # Get database properties to understand structure
            try:
                db_details = client.databases.retrieve(database_id=db_id)
                properties = db_details.get('properties', {})
                prop_names = list(properties.keys())
                print(f"   Properties: {', '.join(prop_names[:5])}")
                if len(prop_names) > 5:
                    print(f"               ...and {len(prop_names) - 5} more")
                
                # Check if this looks like an issues database
                issue_indicators = ['Issue ID', 'GitHub URL', 'Assignee', 'Issue', 'Title']
                if any(indicator in prop_names for indicator in issue_indicators):
                    print("   🎯 LOOKS LIKE ISSUES DATABASE")
                
            except Exception as e:
                print(f"   ⚠️ Could not read properties: {e}")
            
            print()
        
        print("="*60)
        print("📋 To switch to the correct database:")
        print("1. Choose the database ID for 'My Assigned Issue'")
        print("2. Update your .env file with the correct NOTION_DATABASE_ID")
        print("3. Make sure the database has the right properties for issues")
        
    except Exception as e:
        print(f"❌ Error finding databases: {e}")

if __name__ == '__main__':
    find_all_databases()
