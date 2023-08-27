import datetime

from django.db import models
from django.db.models import QuerySet

from accounts.models import User
from menu.models import FoodItem
from vendors.models import Vendor

request_object = None


class Payment(models.Model):
    PAYMENT_METHOD = (
        ('PayPal', 'PayPal'),
        # ('Cash', 'Cash'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100)
    payment_method = models.CharField(choices=PAYMENT_METHOD, max_length=100)
    amount = models.CharField(max_length=10)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.transaction_id


class OrderQuerySet(models.QuerySet):
    def paid_orders_by_user(self, user):
        return self.filter(user=user, is_ordered=True)

    def current_month_orders_by_vendor(self, vendor_pk, today):
        return Order.objects.filter(vendor__in=[vendor_pk],
                                    created_at__month=today.month,
                                    created_at__year=today.year)

    def current_day_orders_by_vendor(self, vendor_pk, today):
        return Order.objects.filter(vendor__in=[vendor_pk],
                                    created_at__day=today.day,
                                    created_at__month=today.month,
                                    created_at__year=today.year)


class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)

    def get_total_revenue(self, orders: QuerySet, vendor_id: int) -> float:
        revenue = 0
        for order in orders:
            revenue += order.get_total_by_vendor(vendor_id=vendor_id)
        return round(revenue, 2)

    def paid_orders_by_user(self, user):
        return self.get_queryset().paid_orders_by_user(user)

    def current_month_orders_by_vendor(self, vendor_pk: int, today: datetime.datetime):
        return self.get_queryset().current_month_orders_by_vendor(vendor_pk, today)

    def current_day_orders_by_vendor(self, vendor_pk: int, today: datetime.datetime):
        return self.get_queryset().current_day_orders_by_vendor(vendor_pk, today)


class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed')
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    vendor = models.ManyToManyField(Vendor, blank=True)
    order_number = models.CharField(max_length=28)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(max_length=50)
    address = models.CharField(max_length=200)
    country = models.CharField(max_length=15, blank=True)
    state = models.CharField(max_length=15, blank=True)
    city = models.CharField(max_length=50)
    pin_code = models.CharField(max_length=10, blank=True, null=True)
    total = models.FloatField(max_length=10)
    total_data = models.JSONField(blank=True, null=True)
    tax_data = models.JSONField(blank=True, help_text="Data format: {'tax_ty}")
    total_tax = models.FloatField()
    payment_method = models.CharField(max_length=25)
    status = models.CharField(choices=STATUS, default='New')
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = OrderManager()

    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'

    def order_placed_to(self):
        return ', '.join([str(i) for i in self.vendor.all()])

    def get_total_by_vendor(self, vendor_id: int) -> float:

        total_data = self.total_data
        data = total_data.get(str(vendor_id))
        subtotal = 0
        for subtotal_, tax_data in data.items():
            subtotal += float(subtotal_)
        return subtotal


    def __str__(self):
        return self.order_number


class OrderedFood(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fooditem = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.fooditem.food_title
