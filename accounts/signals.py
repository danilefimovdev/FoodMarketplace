from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import UserProfile, User


@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        print('User profile was created')
    else:
        try:
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        except Exception:
            # create the userprofile if not exist
            UserProfile.objects.create(user=instance)
            print("Profile didn't exist but I created one")
        print('User was updated')