from django.db import models
from django.db.models import Q

from vendors.models import Vendor


# TODO Add sub category: fastfood/burgers; fastfood/pizza;
# TODO Remove the ability of creation vendors' own categories.
#      They must choose between existing categories;

class Category(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=50)
    slug = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_available_count(self):
        count = FoodItem.objects.filter(Q(is_available=True) & Q(category=self.pk)).count()
        return count

    def get_unavailable_count(self):
        count = FoodItem.objects.filter(Q(is_available=False) & Q(category=self.pk)).count()
        return count

    def __str__(self):
        return self.category_name


# TODO Add weight field;
class FoodItem(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='fooditems')
    food_title = models.CharField(max_length=50, unique=True)
    slug = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=250, blank=True)
    # TODO add price switcher us dollar to uzs and back
    price = models.DecimalField(decimal_places=2, max_digits=9)
    image = models.ImageField(upload_to='food_images')
    is_available = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.food_title
