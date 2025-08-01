from django.urls import path
from . import views

app_name = 'automation'

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('sync/manual/', views.manual_sync, name='manual_sync'),
    path('sync/', views.sync_issues_get, name='sync_issues_get'),  # GET endpoint for sync
    path('sync/webhook/', views.webhook_sync, name='webhook_sync'),
    path('sync/status/', views.sync_status, name='sync_status'),
]
