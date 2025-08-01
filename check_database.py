#!/usr/bin/env python3
"""
Check Notion database properties
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

def check_database_properties():
    """Check what properties exist in the Notion database"""
    print("🔍 Checking Notion database properties...")
    
    try:
        client = Client(auth=settings.NOTION_TOKEN)
        database_id = settings.NOTION_DATABASE_ID
        
        database_info = client.databases.retrieve(database_id=database_id)
        properties = database_info.get('properties', {})
        
        print(f"✅ Database: {database_info.get('title', [{}])[0].get('plain_text', 'Unnamed')}")
        print(f"📊 Found {len(properties)} properties:")
        print()
        
        for prop_name, prop_info in properties.items():
            prop_type = prop_info.get('type', 'unknown')
            print(f"   • {prop_name} ({prop_type})")
            
            # Show options for select/multi-select
            if prop_type == 'select' and 'select' in prop_info:
                options = prop_info['select'].get('options', [])
                if options:
                    option_names = [opt.get('name', '') for opt in options]
                    print(f"     Options: {', '.join(option_names)}")
            elif prop_type == 'multi_select' and 'multi_select' in prop_info:
                options = prop_info['multi_select'].get('options', [])
                if options:
                    option_names = [opt.get('name', '') for opt in options]
                    print(f"     Options: {', '.join(option_names)}")
        
        print("\n" + "="*50)
        print("🔧 Based on your database, I'll update the automation to match these properties.")
        
        return properties
        
    except Exception as e:
        print(f"❌ Failed to check database properties: {e}")
        return {}

if __name__ == '__main__':
    check_database_properties()
