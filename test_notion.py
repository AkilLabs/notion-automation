#!/usr/bin/env python3
"""
Simple Notion connection test
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

def test_notion_basic():
    """Test basic Notion connection"""
    print("🔍 Testing Notion API connection...")
    
    try:
        client = Client(auth=settings.NOTION_TOKEN)
        
        # Try to list databases (this should work if the token is valid)
        print("✅ Notion client initialized successfully")
        print(f"   Token starts with: {settings.NOTION_TOKEN[:10]}...")
        
        # Try to access the specific database
        database_id = settings.NOTION_DATABASE_ID
        print(f"   Trying to access database: {database_id}")
        
        try:
            database_info = client.databases.retrieve(database_id=database_id)
            print("✅ Database found!")
            title = database_info.get('title', [{}])[0].get('plain_text', 'Unnamed')
            print(f"   Database title: {title}")
            print(f"   Properties: {len(database_info.get('properties', {}))}")
            
        except Exception as e:
            print(f"❌ Database access failed: {e}")
            print("\n🔧 Troubleshooting steps:")
            print("1. Make sure your database ID is correct")
            print("2. Share your database with your Notion integration:")
            print("   - Go to your Notion database")
            print("   - Click '...' (three dots) in the top right")
            print("   - Click 'Connect to' and select your integration")
            print("3. Make sure your integration has the right permissions")
            
            # Try to search for databases
            try:
                print("\n🔍 Searching for available databases...")
                search_results = client.search(filter={"property": "object", "value": "database"})
                databases = search_results.get('results', [])
                
                if databases:
                    print(f"   Found {len(databases)} databases:")
                    for db in databases[:5]:  # Show first 5
                        db_title = db.get('title', [{}])[0].get('plain_text', 'Unnamed')
                        db_id = db.get('id', 'Unknown')
                        print(f"   - {db_title} (ID: {db_id})")
                else:
                    print("   No databases found. Make sure to share at least one database with your integration.")
            except Exception as search_e:
                print(f"   Could not search databases: {search_e}")
        
    except Exception as e:
        print(f"❌ Notion connection failed: {e}")
        print("\n🔧 Check your NOTION_TOKEN in the .env file")

if __name__ == '__main__':
    test_notion_basic()
