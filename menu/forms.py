from django import forms
from django.core.exceptions import ValidationError

from menu.models import Category


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ['category_name', 'description']

    def clean_category_name(self):
        category_name = self.cleaned_data['category_name'].lower().capitalize()
        return category_name

