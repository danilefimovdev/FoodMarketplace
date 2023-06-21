import json

from django.db import models
from accounts.models import User
from menu.models import FoodItem
from vendors.models import Vendor

request_object = None


class Payment(models.Model):
    PAYMENT_METHOD = (
        ('PayPal', 'PayPal'),
        ('Cash', 'Cash'),
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


class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
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
    pin_code = models.CharField(max_length=10)
    total = models.FloatField(max_length=10)
    total_data = models.JSONField(blank=True, null=True)
    tax_data = models.JSONField(blank=True, help_text="Data format: {'tax_ty}")
    total_tax = models.FloatField()
    payment_method = models.CharField(max_length=25)
    status = models.CharField(choices=STATUS, default='New')
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = OrderQuerySet().as_manager()

    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'

    def order_placed_to(self):
        return ', '.join([str(i) for i in self.vendor.all()])

    def get_data_by_vendor(self) -> dict:
        vendor = Vendor.objects.get(user=request_object.user)
        if self.total_data:
            total_data = self.total_data
            data = total_data.get(str(vendor.id))
            subtotal = 0
            taxes_amount = 0
            tax_dict = {}
            for subtotal_, tax_data in data.items():
                subtotal += float(subtotal_)
                tax_dict.update(tax_data)
                for tax in tax_data.values():
                    for tax_amount in tax.values():
                        taxes_amount += float(tax_amount)
            total = subtotal + taxes_amount
            context = {
                'subtotal': subtotal,
                'tax_dict': tax_dict,
                'total': round(total, 2),
                'taxes_amount': taxes_amount,
            }
            return context

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
