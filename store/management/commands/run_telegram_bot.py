"""
Django management command to run the Telegram bot in polling mode.
Usage: python manage.py run_telegram_bot
"""
import logging
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Start the Premium Shop Telegram Bot (polling mode)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🤖 Starting Premium Shop Telegram Bot...'))

        try:
            from store.telegram_bot.bot import create_application
            app = create_application()

            self.stdout.write(self.style.SUCCESS('✅ Bot is running! Press Ctrl+C to stop.'))
            # run_polling blocks until Ctrl+C
            app.run_polling(drop_pending_updates=True)

        except ValueError as e:
            self.stderr.write(self.style.ERROR(f'❌ Configuration error: {e}'))
            self.stderr.write(
                'Make sure TELEGRAM_BOT_TOKEN is set in your .env file.'
            )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'❌ Fatal error: {e}'))
            logger.exception("Bot crashed")
            raise
