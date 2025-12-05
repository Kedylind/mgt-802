"""
Management command to pre-generate candidate cases for the database.

Usage:
    python manage.py generate_candidate_cases --count 10 --type consulting
"""
from django.core.management.base import BaseCommand
from cases.models import Case
from agents.case_generator import CaseGenerator


class Command(BaseCommand):
    help = 'Pre-generate candidate cases for the interview simulator.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of cases to generate (default: 10)'
        )
        parser.add_argument(
            '--type',
            type=str,
            default='consulting',
            choices=['consulting', 'product_management'],
            help='Type of cases to generate (default: consulting)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing cases before generating'
        )

    def handle(self, *args, **options):
        count = options['count']
        case_type = options['type']
        clear = options['clear']

        if clear:
            Case.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared all existing cases.'))

        existing_count = Case.objects.count()
        if existing_count >= count:
            self.stdout.write(
                self.style.WARNING(
                    f'Database already has {existing_count} cases. '
                    f'Use --clear to regenerate.'
                )
            )
            return

        cases_to_generate = count - existing_count
        self.stdout.write(
            self.style.SUCCESS(f'Generating {cases_to_generate} candidate cases...')
        )

        try:
            generator = CaseGenerator()
            cases = generator.generate_candidates(
                base_topic="Strategic Business Challenge",
                n=cases_to_generate,
                case_type=case_type,
                save=True,
                user=None
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Successfully generated {len(cases)} candidate cases.'
                )
            )

            # Display generated cases
            for i, case in enumerate(cases, 1):
                self.stdout.write(
                    f'  {i}. {case.get("title", "Untitled")} '
                    f'({case.get("case_type", case_type)})'
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error generating cases: {e}')
            )
            import traceback
            traceback.print_exc()
