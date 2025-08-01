#!/usr/bin/env python3
"""
Test Gemini AI integration
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

from ai_integration.services import GeminiService

def test_gemini_integration():
    """Test Gemini AI service"""
    print("🤖 Testing Gemini AI Integration...")
    
    # Sample issue data for testing
    sample_issue = {
        'repository_owner': 'AkilLabs',
        'repository_name': 'history-extension',
        'title': 'Demo',
        'number': 1,
        'state': 'open',
        'assignee_login': 'AkilLabs',
        'labels': [{'name': 'enhancement'}, {'name': 'good first issue'}],
        'body': 'This is a demo issue for testing the Chrome extension history functionality.',
        'html_url': 'https://github.com/AkilLabs/history-extension/issues/1',
        'created_at': '2025-01-01T10:00:00Z',
        'updated_at': '2025-01-01T10:30:00Z'
    }
    
    try:
        gemini_service = GeminiService()
        
        if not gemini_service.enabled:
            print("❌ Gemini AI is not enabled. Please configure GEMINI_API_KEY in your .env file.")
            print("📝 To get your API key:")
            print("   1. Go to https://aistudio.google.com/app/apikey")
            print("   2. Create a new API key")
            print("   3. Add it to your .env file as: GEMINI_API_KEY=your-api-key-here")
            return
        
        print("✅ Gemini AI service initialized successfully!")
        print("\n🔄 Generating enhanced description...")
        
        enhanced_description = gemini_service.enhance_issue_description(sample_issue)
        
        print("\n📄 Enhanced Description:")
        print("=" * 60)
        print(enhanced_description)
        print("=" * 60)
        
        print("\n✅ Gemini integration test completed successfully!")
        print("📌 The automation will now use AI-enhanced descriptions for all GitHub issues.")
        
    except Exception as e:
        print(f"❌ Failed to test Gemini integration: {e}")
        print("🔧 Make sure your GEMINI_API_KEY is correctly configured in the .env file.")

if __name__ == '__main__':
    test_gemini_integration()
