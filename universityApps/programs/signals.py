from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import AcademicProgram
from .services import (
    create_program_settings_for_program, 
    create_program_structure,
    )

@receiver(post_save, sender=AcademicProgram)
def create_program_settings(sender, instance, created, **kwargs):
    if created:
        # Create program settings
        create_program_settings_for_program(instance, standard_duration_years=4.0)

        # Create academic levels
        create_program_structure(instance)