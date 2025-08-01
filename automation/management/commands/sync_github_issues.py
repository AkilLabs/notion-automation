from django.core.management.base import BaseCommand, CommandError
from automation.services import AutomationService


class Command(BaseCommand):
    help = 'Sync assigned GitHub issues to Notion dashboard'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--sync-type',
            type=str,
            default='manual',
            choices=['manual', 'scheduled', 'webhook'],
            help='Type of sync operation'
        )
        
        parser.add_argument(
            '--github-url',
            type=str,
            help='Sync a specific issue by GitHub URL (e.g., https://github.com/owner/repo/issues/123)'
        )
        
        parser.add_argument(
            '--repository',
            type=str,
            help='Sync all issues from a specific repository (format: owner/repo)'
        )
        
        parser.add_argument(
            '--status',
            action='store_true',
            help='Show current sync status instead of running sync'
        )
        
        parser.add_argument(
            '--test-connections',
            action='store_true',
            help='Test GitHub and Notion API connections'
        )
    
    def handle(self, *args, **options):
        automation_service = AutomationService()
        
        try:
            # Test connections
            if options['test_connections']:
                self.test_connections(automation_service)
                return
            
            # Show status
            if options['status']:
                self.show_status(automation_service)
                return
            
            # Sync single issue by URL
            if options['github_url']:
                self.sync_single_issue_by_url(automation_service, options['github_url'])
                return
            
            # Sync repository
            if options['repository']:
                self.sync_repository(automation_service, options['repository'])
                return
            
            # Full sync
            self.run_full_sync(automation_service, options['sync_type'])
            
        except Exception as e:
            raise CommandError(f'Sync failed: {e}')
    
    def run_full_sync(self, automation_service, sync_type):
        """Run full sync of all assigned issues"""
        self.stdout.write(f'Starting {sync_type} sync of assigned GitHub issues...')
        
        sync_result = automation_service.sync_assigned_issues(sync_type)
        
        if sync_result.status == 'completed':
            self.stdout.write(
                self.style.SUCCESS(
                    f'Sync completed successfully!\n'
                    f'Issues processed: {sync_result.issues_processed}\n'
                    f'Issues synced: {sync_result.issues_synced}\n'
                    f'Duration: {sync_result.completed_at - sync_result.started_at}'
                )
            )
        elif sync_result.status == 'partial':
            self.stdout.write(
                self.style.WARNING(
                    f'Sync completed with errors.\n'
                    f'Issues processed: {sync_result.issues_processed}\n'
                    f'Issues synced: {sync_result.issues_synced}\n'
                    f'Errors: {sync_result.errors_count}\n'
                    f'Error messages:\n{chr(10).join(sync_result.error_messages)}'
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f'Sync failed!\n'
                    f'Error: {chr(10).join(sync_result.error_messages)}'
                )
            )
    
    def sync_single_issue_by_url(self, automation_service, github_url):
        """Sync a single issue by GitHub URL"""
        self.stdout.write(f'Syncing issue from {github_url}...')
        
        success, message = automation_service.sync_single_issue_by_url(github_url)
        
        if success:
            self.stdout.write(self.style.SUCCESS(message))
        else:
            self.stdout.write(self.style.ERROR(message))
    
    def sync_repository(self, automation_service, repository):
        """Sync all issues from a repository"""
        try:
            owner, repo = repository.split('/')
        except ValueError:
            self.stdout.write(self.style.ERROR('Repository format should be owner/repo'))
            return
        
        self.stdout.write(f'Syncing issues from {repository}...')
        
        sync_result = automation_service.sync_repository_issues(owner, repo)
        
        if sync_result.status == 'completed':
            self.stdout.write(
                self.style.SUCCESS(
                    f'Repository sync completed successfully!\n'
                    f'Issues processed: {sync_result.issues_processed}\n'
                    f'Issues synced: {sync_result.issues_synced}'
                )
            )
        elif sync_result.status == 'partial':
            self.stdout.write(
                self.style.WARNING(
                    f'Repository sync completed with errors.\n'
                    f'Issues processed: {sync_result.issues_processed}\n'
                    f'Issues synced: {sync_result.issues_synced}\n'
                    f'Errors: {sync_result.errors_count}'
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'Repository sync failed: {chr(10).join(sync_result.error_messages)}')
            )
    
    def test_connections(self, automation_service):
        """Test API connections"""
        self.stdout.write('Testing API connections...')
        
        results = automation_service.test_connections()
        
        # GitHub connection
        if results['github']['status'] == 'success':
            self.stdout.write(self.style.SUCCESS(f"✅ GitHub: {results['github']['message']}"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ GitHub: {results['github']['message']}"))
        
        # Notion connection
        if results['notion']['status'] == 'success':
            self.stdout.write(self.style.SUCCESS(f"✅ Notion: {results['notion']['message']}"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ Notion: {results['notion']['message']}"))
        
        # Overall status
        if results['overall'] == 'success':
            self.stdout.write(self.style.SUCCESS('\n🎉 All connections successful! Ready to sync.'))
        elif results['overall'] == 'partial':
            self.stdout.write(self.style.WARNING('\n⚠️ Some connections failed. Check configuration.'))
        else:
            self.stdout.write(self.style.ERROR('\n❌ All connections failed. Check your credentials.'))
    
    def show_status(self, automation_service):
        """Show current sync status"""
        status = automation_service.get_sync_status()
        
        if 'error' in status:
            self.stdout.write(self.style.ERROR(f"Error getting status: {status['error']}"))
            return
        
        self.stdout.write(self.style.SUCCESS('=== Sync Status ==='))
        self.stdout.write(f"Mode: Direct sync (no database)")
        self.stdout.write(f"GitHub issues available: {status.get('github_issues_available', 'Unknown')}")
        self.stdout.write(f"Last checked: {status.get('last_checked', 'Never')}")
        
        # GitHub rate limit info
        rate_limit = status.get('github_rate_limit', {})
        if rate_limit:
            core_limit = rate_limit.get('resources', {}).get('core', {})
            self.stdout.write(f"\n=== GitHub API Rate Limit ===")
            self.stdout.write(f"Remaining: {core_limit.get('remaining', 'N/A')}")
            self.stdout.write(f"Limit: {core_limit.get('limit', 'N/A')}")
            if core_limit.get('reset'):
                import datetime
                reset_time = datetime.datetime.fromtimestamp(core_limit['reset'])
                self.stdout.write(f"Resets at: {reset_time}")
        
        self.stdout.write(f"\n💡 Tip: Use --test-connections to verify your API setup")
