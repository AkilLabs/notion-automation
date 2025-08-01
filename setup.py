#!/usr/bin/env python3
"""
Setup script for GitHub to Notion automation
This script helps you configure the environment and test the connections
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notion_github_automation.settings')
django.setup()

from github_integration.services import GitHubService
from notion_integration.services import NotionService


def check_environment():
    """Check if all required environment variables are set"""
    required_vars = [
        'GITHUB_TOKEN',
        'GITHUB_USERNAME', 
        'NOTION_TOKEN',
        'NOTION_DATABASE_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these in your .env file")
        return False
    
    print("✅ All required environment variables are set")
    return True


def test_github_connection():
    """Test GitHub API connection"""
    print("\n🔍 Testing GitHub connection...")
    
    try:
        github_service = GitHubService()
        rate_limit = github_service.check_api_rate_limit()
        
        print("✅ GitHub connection successful")
        print(f"   API Rate Limit: {rate_limit['resources']['core']['remaining']}/{rate_limit['resources']['core']['limit']}")
        
        # Test fetching issues
        issues = github_service.get_assigned_issues(per_page=1)
        print(f"   Found {len(issues)} assigned issue(s) in first page")
        
        return True
        
    except Exception as e:
        print(f"❌ GitHub connection failed: {e}")
        return False


def test_notion_connection():
    """Test Notion API connection"""
    print("\n🔍 Testing Notion connection...")
    
    try:
        notion_service = NotionService()
        database_info = notion_service.get_database_info()
        
        print("✅ Notion connection successful")
        print(f"   Database: {database_info.get('title', [{}])[0].get('plain_text', 'Unnamed')}")
        print(f"   Properties: {len(database_info.get('properties', {}))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Notion connection failed: {e}")
        return False


def run_test_sync():
    """Run a test sync to verify everything works"""
    print("\n🚀 Running test sync...")
    
    try:
        from automation.services import AutomationService
        
        automation_service = AutomationService()
        
        # Get status first
        status = automation_service.get_sync_status()
        print(f"   GitHub issues available: {status.get('github_issues_available', 'Unknown')}")
        
        # Run a limited sync (just first few issues)
        github_service = automation_service.github_service
        test_issues = github_service.get_assigned_issues(per_page=2)  # Just test with 2 issues
        
        if not test_issues:
            print("   No assigned issues found to test with")
            return True
        
        print(f"   Testing with {len(test_issues)} issues...")
        
        sync_result = automation_service.sync_assigned_issues('manual')
        
        if sync_result.status == 'completed':
            print("✅ Test sync completed successfully")
            print(f"   Issues processed: {sync_result.issues_processed}")
            print(f"   Issues synced: {sync_result.issues_synced}")
        else:
            print(f"⚠️ Test sync completed with status: {sync_result.status}")
            if sync_result.error_messages:
                print(f"   Errors: {'; '.join(sync_result.error_messages)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test sync failed: {e}")
        return False


def main():
    """Main setup function"""
    print("🔧 GitHub to Notion Automation Setup")
    print("=" * 40)
    
    # Check environment
    if not check_environment():
        return
    
    # Test connections
    github_ok = test_github_connection()
    notion_ok = test_notion_connection()
    
    if not github_ok or not notion_ok:
        print("\n❌ Setup incomplete. Please fix the connection issues above.")
        return
    
    # Run test sync
    print("\n" + "=" * 40)
    choice = input("Would you like to run a test sync? (y/n): ").lower().strip()
    
    if choice == 'y':
        if run_test_sync():
            print("\n🎉 Setup completed successfully!")
            print("\nNext steps:")
            print("1. Check your Notion database to see the synced issues")
            print("2. Run 'python manage.py sync_github_issues --status' to check status")
            print("3. Set up automated sync with cron job or task scheduler")
            print("4. Access Django admin at http://localhost:8000/admin/ (after running 'python manage.py runserver')")
        else:
            print("\n⚠️ Setup completed but test sync failed. Check the logs for details.")
    else:
        print("\n✅ Connection tests passed. You can now run syncs manually.")


if __name__ == '__main__':
    main()
