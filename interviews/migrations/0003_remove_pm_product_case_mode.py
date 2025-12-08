# Generated migration to remove pm_product_case mode

from django.db import migrations, models


def migrate_pm_product_case_to_interviewer_led(apps, schema_editor):
    """
    Convert any existing pm_product_case mode sessions to interviewer_led.
    This is a reasonable default since pm_product_case was interviewer-led in behavior.
    """
    InterviewSession = apps.get_model('interviews', 'InterviewSession')
    InterviewSession.objects.filter(mode='pm_product_case').update(mode='interviewer_led')


def reverse_migration(apps, schema_editor):
    """
    Reverse migration - convert interviewer_led back to pm_product_case if needed.
    Note: This is not a perfect reversal, but necessary for migration rollback.
    """
    InterviewSession = apps.get_model('interviews', 'InterviewSession')
    # We can't perfectly reverse this, so we'll just leave them as interviewer_led


class Migration(migrations.Migration):

    dependencies = [
        ('interviews', '0002_interviewsession_current_phase'),
    ]

    operations = [
        # First, migrate existing data
        migrations.RunPython(
            migrate_pm_product_case_to_interviewer_led,
            reverse_migration
        ),
        # Then, update the model field choices
        migrations.AlterField(
            model_name='interviewsession',
            name='mode',
            field=models.CharField(
                choices=[
                    ('interviewer_led', 'Interviewer-Led'),
                    ('candidate_led', 'Candidate-Led'),
                ],
                max_length=20
            ),
        ),
    ]

