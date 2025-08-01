from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from automation.services import AutomationService
import logging
import json

logger = logging.getLogger('automation')

def health_check(request):
    """Health check endpoint for Render"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'GitHub-Notion Automation',
        'version': '1.0.0'
    })

@csrf_exempt
@require_http_methods(["POST"])
def manual_sync(request):
    """Manual sync trigger endpoint"""
    try:
        # Get state parameter from request, default to 'open'
        state = request.POST.get('state', 'open')
        if state not in ['open', 'closed', 'all']:
            state = 'open'
            
        automation_service = AutomationService()
        result = automation_service.sync_assigned_issues('manual_web', state)
        
        return JsonResponse({
            'success': True,
            'message': 'Sync completed successfully',
            'issues_processed': result.issues_processed,
            'issues_synced': result.issues_synced,
            'duration': str(result.duration),
            'status': result.status
        })
        
    except Exception as e:
        logger.error(f"Manual sync failed: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_http_methods(["GET"])
def sync_issues_get(request):
    """GET endpoint to sync GitHub issues to Notion"""
    try:
        # Get state parameter from query string, default to 'open'
        state = request.GET.get('state', 'open')
        if state not in ['open', 'closed', 'all']:
            state = 'open'
            
        automation_service = AutomationService()
        result = automation_service.sync_assigned_issues('manual_get', state)
        
        return JsonResponse({
            'success': True,
            'message': f'GitHub {state} issues synced to Notion successfully',
            'issues_processed': result.issues_processed,
            'issues_synced': result.issues_synced,
            'duration': str(result.duration),
            'status': result.status,
            'sync_type': 'GET request',
            'issue_state': state
        })
        
    except Exception as e:
        logger.error(f"GET sync failed: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to sync GitHub issues to Notion'
        }, status=500)

@csrf_exempt 
@require_http_methods(["POST"])
def webhook_sync(request):
    """GitHub webhook endpoint for automatic sync"""
    try:
        # Parse GitHub webhook payload
        payload = json.loads(request.body)
        action = payload.get('action', '')
        
        # Only sync on issue assignment/update events
        if action in ['assigned', 'opened', 'edited', 'reopened']:
            # For most actions, only sync open issues
            automation_service = AutomationService()
            result = automation_service.sync_assigned_issues('webhook', 'open')
        elif action == 'closed':
            # For closed action, sync all issues to update status
            automation_service = AutomationService()
            result = automation_service.sync_assigned_issues('webhook', 'all')
        else:
            return JsonResponse({
                'success': True,
                'message': f'No sync needed for action: {action}'
            })
            
        return JsonResponse({
            'success': True,
            'message': f'Webhook sync completed for action: {action}',
            'issues_processed': result.issues_processed,
            'issues_synced': result.issues_synced
        })
            
    except Exception as e:
        logger.error(f"Webhook sync failed: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def sync_status(request):
    """Get sync status and basic info"""
    try:
        from django.conf import settings
        
        return JsonResponse({
            'github_configured': bool(settings.GITHUB_TOKEN),
            'notion_configured': bool(settings.NOTION_TOKEN),
            'gemini_configured': bool(settings.GEMINI_API_KEY),
            'database_id': settings.NOTION_DATABASE_ID,
            'username': settings.GITHUB_USERNAME
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)
