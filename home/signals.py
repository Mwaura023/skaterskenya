from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

@receiver(post_save, sender=User)
def handle_user_profile(sender, instance, created, **kwargs):
    """
    The only signal handler you need - safely creates and manages profiles
    """
    if created:
        Profile.objects.get_or_create(user=instance)
    elif hasattr(instance, 'profile'):
        instance.profile.save()