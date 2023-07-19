from django import forms

from accounts.validators import allow_only_images_validator
from menu.models import Category, FoodItem


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ['category_name', 'description']

    def clean_category_name(self):
        category_name = self.cleaned_data['category_name'].lower().capitalize()
        return category_name


class FoodItemForm(forms.ModelForm):

    image = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info w-100'}),
                            validators=[allow_only_images_validator])

    class Meta:
        model = FoodItem
        fields = ['category', 'food_title', 'description', 'price', 'image', 'is_available']

    def clean_food_title(self):
        food_title = self.cleaned_data['food_title'].lower().capitalize()
        return food_title


