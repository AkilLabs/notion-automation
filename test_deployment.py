#!/usr/bin/env python3
"""
Test deployment readiness
"""

import os
import sys
from pathlib import Path

def test_deployment_readiness():
    """Test if the project is ready for deployment"""
    print("🔍 Testing Deployment Readiness...")
    print("=" * 50)
    
    issues = []
    warnings = []
    
    # Check required files
    required_files = [
        'requirements.txt',
        'build.sh',
        'Procfile',
        'manage.py',
        'DEPLOY.md'
    ]
    
    print("📁 Checking required files...")
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file}")
            issues.append(f"Missing {file}")
    
    # Check environment variables
    print("\n🔑 Checking environment variables...")
    required_env_vars = [
        'GITHUB_TOKEN',
        'GITHUB_USERNAME', 
        'NOTION_TOKEN',
        'NOTION_DATABASE_ID',
        'GEMINI_API_KEY'
    ]
    
    from dotenv import load_dotenv
    load_dotenv()
    
    for var in required_env_vars:
        value = os.getenv(var)
        if value and value != f'your-{var.lower().replace("_", "-")}-here':
            print(f"   ✅ {var}")
        else:
            print(f"   ❌ {var}")
            issues.append(f"Missing or placeholder value for {var}")
    
    # Check Django configuration
    print("\n⚙️  Testing Django configuration...")
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notion_github_automation.settings')
        import django
        django.setup()
        
        from django.conf import settings
        from django.core.management import execute_from_command_line
        
        print("   ✅ Django settings loaded")
        print("   ✅ Apps configured")
        
    except Exception as e:
        print(f"   ❌ Django configuration error: {e}")
        issues.append(f"Django configuration issue: {e}")
    
    # Test API integrations
    print("\n🔌 Testing API integrations...")
    try:
        from automation.services import AutomationService
        automation_service = AutomationService()
        print("   ✅ Automation service initialized")
        
        from ai_integration.services import GeminiService
        gemini_service = GeminiService()
        if gemini_service.enabled:
            print("   ✅ Gemini AI service enabled")
        else:
            print("   ⚠️  Gemini AI service disabled (check API key)")
            warnings.append("Gemini AI not configured")
            
    except Exception as e:
        print(f"   ❌ Service initialization error: {e}")
        issues.append(f"Service error: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    if issues:
        print("❌ DEPLOYMENT NOT READY")
        print("\nIssues to fix:")
        for issue in issues:
            print(f"   • {issue}")
    else:
        print("✅ DEPLOYMENT READY!")
        
    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"   ⚠️  {warning}")
    
    print("\n📋 Next Steps:")
    if issues:
        print("   1. Fix the issues listed above")
        print("   2. Run this test again")
        print("   3. Push to GitHub when ready")
    else:
        print("   1. Push your code to GitHub:")
        print("      git add .")
        print("      git commit -m 'Deploy to Render'")
        print("      git push origin main")
        print("   2. Follow DEPLOY.md instructions")
        print("   3. Set up environment variables in Render")
        print("   4. Deploy!")
    
    return len(issues) == 0

if __name__ == '__main__':
    test_deployment_readiness()
