import json

from django.core.management.base import BaseCommand
from django.utils import timezone

from analytics.evaluation import generate_evaluation_report, print_evaluation_report


class Command(BaseCommand):
    help = 'Generate evaluation metrics for the system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output in JSON format',
        )
        parser.add_argument(
            '--save',
            action='store_true',
            help='Save report to file',
        )

    def handle(self, *args, **options):
        if options.get('json'):
            report = generate_evaluation_report()
            self.stdout.write(json.dumps(report, indent=2))
        else:
            print_evaluation_report()
        if options.get('save'):
            report = generate_evaluation_report()
            filename = f"evaluation_report_{timezone.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            self.stdout.write(self.style.SUCCESS(f"\n Report saved to {filename}"))
