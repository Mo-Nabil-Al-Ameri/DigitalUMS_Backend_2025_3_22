from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import GroupSchedule, LectureBroadcast

@receiver(post_save, sender=GroupSchedule)
def auto_create_broadcast(sender, instance, created, **kwargs):
    if created and instance.is_online:
        LectureBroadcast.objects.get_or_create(schedule=instance)
