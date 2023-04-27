from django.db import models

from accounts.models import UserProfile, User
from accounts.utils import send_notification


class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user')
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='user_profile')
    vendor_name = models.CharField(max_length=50)
    vendor_license = models.ImageField(upload_to='vendors/license')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vendor_name

    def save(self, *args, **kwargs):
        if self.pk is not None:
            # Update
            orig = Vendor.objects.get(pk=self.pk)
            if orig.is_approved != self.is_approved:
                email_template = 'accounts/email/admin_approval_email.html'
                context = {
                    'user': self.user,
                    'is_approved': self.is_approved
                }

                if self.is_approved is True:
                    message_subject = 'Congratulations! Your restaurant has been approved.'
                else:
                    message_subject = 'We are sorry! You are not eligible for ' \
                                   'publishing your food menu on our marketplace.'

                send_notification(message_subject, email_template, context)
        return super(Vendor, self).save()