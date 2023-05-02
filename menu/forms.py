from django import forms
from django.core.exceptions import ValidationError

from accounts.validators import allow_only_images_validator
from menu.models import Category, FoodItem
from vendors.utils import get_vendor


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ['category_name', 'description']

    def clean_category_name(self):
        category_name = self.cleaned_data['category_name'].lower().capitalize()
        return category_name


class FoodItemForm(forms.ModelForm):
    image = forms.FileField(widget=forms.FileInput({'class': 'btn btn-info w-100'}),
                                     validators=[allow_only_images_validator])

    class Meta:
        model = FoodItem
        fields = ['category', 'food_title', 'description', 'price', 'image', 'is_available']


