import logging

from django.core.management.base import BaseCommand, CommandError

from rates.utils import load_latest_rates, generate_all_rates, save_rates

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Get and store latest rates from The Open Exchange Rates service'

    def handle(self, *args, **options):
        try:
            data = load_latest_rates()
            rates = generate_all_rates(data)
            save_rates(rates)
        except Exception as e:
            logger.error('Error for getting latest rates: {}'.format(e))
            raise CommandError('Error for getting latest rates: {}'.format(e))

        self.stdout.write(self.style.SUCCESS('Successfully updated rates'))
