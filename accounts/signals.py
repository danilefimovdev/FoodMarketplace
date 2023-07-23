from django.db.models import ImageField
from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import UserProfile, User


@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    if created:
        # user = User.objects.get(pk=instance)
        # print(user.role, 'user.role')
        # if user.role == 1:
        #     image = ImageField(upload_to='food_marketplace/static/images/default-restaurant.png')
        #     UserProfile.objects.create(user=instance, profile_picture=image)
        # else:
        #     UserProfile.objects.create(user=instance)
        UserProfile.objects.create(user=instance)
    else:
        try:
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        except Exception:
            # create the userprofile if not exist
            UserProfile.objects.create(user=instance)
        print('User was updated')
