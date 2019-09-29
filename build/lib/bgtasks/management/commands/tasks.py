# Python
import logging

# Django
from django.conf import settings
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run background job and rpc'

    def handle(self, *args, **options):
        from ...amqp import start

        if settings.DEBUG:
            logger.warning('Disable DJANGO debug mode')

        logger.info('Start tasks')
        start()
        logger.info('Finish tasks')
