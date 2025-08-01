#!/usr/bin/env python3
"""
Update .env file with the correct database ID
"""

import os
from pathlib import Path

def update_env_database():
    """Help update the .env file with correct database ID"""
    print("🔧 Database ID Updater")
    print("=" * 40)
    
    # First, let's run the database finder
    print("Step 1: Finding your databases...")
    os.system("python find_databases.py")
    
    print("\n" + "=" * 40)
    print("📋 Instructions:")
    print("1. Share your 'My Assigned Issue' database with your Notion integration:")
    print("   - Go to your 'My Assigned Issue' database in Notion")
    print("   - Click '...' (three dots) in top right")
    print("   - Click 'Connect to' and select your integration")
    print()
    print("2. Run this script again to see the new database")
    print("3. Copy the database ID for 'My Assigned Issue'")
    print("4. Update your .env file:")
    
    print("\nCurrent .env content:")
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if 'NOTION_DATABASE_ID' in line:
                    print(f"   Line {i+1}: {line.strip()}")
                    print("   ↓ Replace with:")
                    print("   NOTION_DATABASE_ID=your-new-database-id-here")
    
    print("\n" + "=" * 40)
    database_id = input("Enter your 'My Assigned Issue' database ID (or press Enter to skip): ").strip()
    
    if database_id:
        # Update the .env file
        if env_path.exists():
            with open(env_path, 'r') as f:
                content = f.read()
            
            # Replace the database ID
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('NOTION_DATABASE_ID='):
                    lines[i] = f'NOTION_DATABASE_ID={database_id}'
                    break
            
            with open(env_path, 'w') as f:
                f.write('\n'.join(lines))
            
            print(f"✅ Updated .env with new database ID: {database_id}")
            print("\nNow test the connection:")
            print("python manage.py sync_github_issues --test-connections")
        else:
            print("❌ .env file not found")
    else:
        print("⏭️ Skipping update. You can manually edit the .env file.")

if __name__ == '__main__':
    update_env_database()
