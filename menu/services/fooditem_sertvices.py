import random

from menu.models import FoodItem


def get_random_fooditems_data() -> dict:
    '''Randomly choose 3 available fooditems as recommendation from and return data as dict'''

    all_fooditems = FoodItem.objects.filter(is_available=True)
    count_fooditems = all_fooditems.count()

    random_indexes = list(range(count_fooditems))
    random.shuffle(random_indexes)

    set_size = 2 if count_fooditems > 2 else count_fooditems
    fooditems_set = [all_fooditems[random_indexes[i]] for i in range(set_size)]

    fooditems = {}
    for food in fooditems_set:
        fooditems.update({
            food.food_title: {
                'image_url': food.image.url,
                'price': food.price,
                'vendor_slug': food.vendor.vendor_slug
            }
        })
    return fooditems
