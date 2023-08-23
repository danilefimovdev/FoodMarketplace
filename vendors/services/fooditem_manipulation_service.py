from menu.models import FoodItem
from vendors.models import Vendor
from pytils.translit import slugify


def create_or_update_fooditem(vendor_id: int, form_data: dict, slug: str = None) -> str:

    vendor = Vendor.objects.get(id=vendor_id)

    if not slug:
        fooditem = FoodItem()
    else:
        fooditem = FoodItem.objects.get(slug=slug)

    fooditem.category = form_data['category']
    fooditem.food_title = form_data['food_title']
    fooditem.description = form_data['description']
    fooditem.price = form_data['price']
    fooditem.image = form_data['image']
    fooditem.vendor = vendor
    fooditem.is_available = form_data['is_available']
    print(fooditem.is_available, 'fooditem.is_available')
    fooditem.slug = slugify(form_data['food_title']) + '-' + str(vendor_id)
    fooditem.save()

    category_slug = fooditem.category.slug
    return category_slug
