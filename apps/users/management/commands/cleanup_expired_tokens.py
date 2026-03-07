from django.core.management.base import BaseCommand
from users.utils import (
    cleanup_expired_tokens,
    cleanup_expired_verification_tokens,
    cleanup_expired_reset_tokens
)


class Command(BaseCommand):
    help = 'Clean up expired tokens from database'
    
    def handle(self, *args, **options):
        self.stdout.write('Starting token cleanup...')
        
        # Cleanup blacklisted tokens
        count1 = cleanup_expired_tokens()
        self.stdout.write(f'Cleaned up {count1} expired blacklist tokens')
        
        # Cleanup verification tokens
        count2 = cleanup_expired_verification_tokens()
        self.stdout.write(f'Cleaned up {count2} expired verification tokens')
        
        # Cleanup reset tokens
        count3 = cleanup_expired_reset_tokens()
        self.stdout.write(f'Cleaned up {count3} expired reset tokens')
        
        total = count1 + count2 + count3
        self.stdout.write(self.style.SUCCESS(f'Successfully cleaned up {total} tokens'))
#Run with: python manage.py cleanup_expired_tokens