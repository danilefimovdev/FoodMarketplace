from django import forms

from accounts.models import User, UserProfile
from accounts.validators import allow_only_images_validator, allow_only_square_images_validator


class UserForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'role']

    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError("Two passwords don't match")
        return cleaned_data


class UserProfileForm(forms.ModelForm):

    profile_picture = forms.FileField(widget=forms.FileInput({'class': 'btn btn-info'}),
                                      validators=[allow_only_images_validator, allow_only_square_images_validator])
    cover_photo = forms.FileField(widget=forms.FileInput({'class': 'btn btn-info'}),
                                  validators=[allow_only_images_validator])
    # uncomment if google services work
    # latitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    # longitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    # address = forms.CharField(widget=forms.TextInput(attrs={
    #     'placeholder': 'Start typing....', 'required': 'required',
    # }))
    address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Start typing....',
    }))

    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'cover_photo', 'address',
                  'country', 'state', 'city', 'pin_code', 'latitude', 'longitude']

        def __init__(self, *args, **kwargs):
            super(UserProfileForm, self).__init__(*args, **kwargs)
            for field in self.fields:
                if field == 'latitude' or field == 'longitude':
                    self.fields[field].widget.attrs['readonly'] = 'readonly'


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number']

