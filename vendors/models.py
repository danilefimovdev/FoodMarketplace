from datetime import time, datetime
from django.db import models
from accounts.models import UserProfile, User
from vendors.services.service import notify_vendor_of_status_change


class VendorQuerySet(models.QuerySet):

    def valid_vendors(self):
        return self.filter(is_approved=True, user__is_active=True, is_listed=True)


class Vendor(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user')
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='user_profile')
    vendor_name = models.CharField(max_length=50, unique=True)
    vendor_slug = models.SlugField(max_length=100, unique=True)
    vendor_license = models.ImageField(upload_to='vendors/license')
    is_approved = models.BooleanField(default=False)
    is_listed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    objects = VendorQuerySet().as_manager()

    def __str__(self):
        return self.vendor_name

    @property
    def is_open(self):
        now = datetime.now()
        today = datetime.isoweekday(now)
        current_opening_hours = OpeningHour.objects.get_by_vendor_and_day(self, today)

        current_time = now.strftime("%H:%M")

        if not current_opening_hours.is_closed:
            start = str(datetime.strptime(current_opening_hours.from_hour, "%H:%M").time())
            end = str(datetime.strptime(current_opening_hours.to_hour, "%H:%M").time())
            if end > current_time > start:
                is_open = True
            else:
                is_open = False
        else:
            is_open = False
        return is_open

    def save(self, *args, **kwargs):
        if self.pk is not None:
            # Update
            vendor = Vendor.objects.get(pk=self.pk)
            status_changed = True if self.is_approved != vendor.is_approved else False
            notify_vendor_of_status_change(approve_state=bool(self.is_approved), email=vendor.user.email,
                                           first_name=vendor.user.first_name, status_changed=status_changed)
        return super(Vendor, self).save()


DAYS = [
    (1, "Monday"),
    (2, "Tuesday"),
    (3, "Wednesday"),
    (4, "Thursday"),
    (5, "Friday"),
    (6, "Saturday"),
    (7, "Sunday"),
]


HOUR_OF_DAY_24 = [(time(h, m).strftime('%H:%M'), time(h, m).strftime('%H:%M')) for h in range(0, 24) for m in (0, 30)]


class OpeningHourQuerySet(models.QuerySet):

    def get_by_vendor_and_day(self, vendor, day):
        return self.get(vendor=vendor, day=day)


class OpeningHour(models.Model):

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField(choices=HOUR_OF_DAY_24, max_length=10, blank=True, null=True)
    to_hour = models.CharField(choices=HOUR_OF_DAY_24, max_length=10, blank=True, null=True)
    is_closed = models.BooleanField(default=False)

    objects = OpeningHourQuerySet().as_manager()

    class Meta:
        ordering = ('day', '-from_hour')
        unique_together = ('vendor', 'day')

    def __str__(self):
        return self.get_day_display()
