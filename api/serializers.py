from django.contrib.auth import authenticate
from django.template.defaultfilters import slugify

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts.models import User, UserProfile
from accounts.services import send_reset_password_email
from accounts.services.user_registration_service import register_new_customer, register_new_vendor
from marketplace.models import Cart
from menu.models import FoodItem
from vendors.models import Vendor


class CustomAuthTokenSerializer(serializers.Serializer):

    email = serializers.CharField(
        label="Email",
        style={'input_type': 'email'},
        write_only=True
    )
    password = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label="Token",
        read_only=True
    )

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "email" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        data['user'] = user
        return data


class UserCreateSerializer(serializers.Serializer):

    VENDOR = 1
    CUSTOMER = 2

    ROLE_CHOICE = (
        (VENDOR, 'Vendor'),
        (CUSTOMER, 'Customer'),
    )

    first_name = serializers.CharField(max_length=50, required=True)
    last_name = serializers.CharField(max_length=50, required=True)
    username = serializers.CharField(max_length=50, required=True)
    email = serializers.EmailField(max_length=100, required=True)
    role = serializers.ChoiceField(choices=ROLE_CHOICE, required=True)
    password = serializers.CharField(min_length=10, required=True)
    confirm_password = serializers.CharField(min_length=10, required=True)

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        if password != confirm_password:
            raise ValidationError("Two passwords don't match")
        return attrs

    def create(self, validated_data):
        user_id = register_new_customer(user_form_data=validated_data)
        return User.objects.get(pk=user_id)


class VendorCreateSerializer(serializers.Serializer):

    vendor_license = serializers.ImageField()
    vendor_name = serializers.CharField(max_length=50)

    def create(self, validated_data):
        user_data = validated_data
        user_data.update({'role': 1})
        vendor_data = dict()
        vendor_data.update({'vendor_name': user_data.pop('vendor_name')})
        vendor_data.update({'vendor_license': user_data.pop('vendor_license')})
        user_id = register_new_vendor(
            vendor_form_data=vendor_data,
            user_form_data=user_data
        )
        return User.objects.get(pk=user_id)


class ForgetPasswordFormSerializer(serializers.Serializer):

    email = serializers.EmailField()

    def validate(self, attrs):
        if not User.objects.filter(email=attrs['email']).exists():
            raise ValidationError('User with entered email does not exist')
        return attrs

    def save(self):
        email = self.validated_data['email']
        send_reset_password_email(email=email)


class RestaurantSerializer(serializers.ModelSerializer):

    restaurant_picture_url = serializers.SerializerMethodField(read_only=True)
    address = serializers.CharField(source='user_profile.address', read_only=True)
    state = serializers.CharField(source='user_profile.state', read_only=True)
    city = serializers.CharField(source='user_profile.city', read_only=True)
    pin_code = serializers.CharField(source='user_profile.pin_code', read_only=True)
    latitude = serializers.CharField(source='user_profile.latitude', read_only=True)
    longitude = serializers.CharField(source='user_profile.longitude', read_only=True)
    vendor_slug = serializers.CharField(read_only=True)

    class Meta:
        model = Vendor
        fields = ['vendor_name', 'latitude', 'longitude', 'pin_code', 'city', 'state',
                  'address', 'restaurant_picture_url', 'vendor_slug']

    def get_restaurant_picture_url(self, Vendor):
        request = self.context.get('request')
        image_url = Vendor.user_profile.profile_picture.url
        return request.build_absolute_uri(image_url)


class RestaurantFullInfoSerializer(serializers.ModelSerializer):

    restaurant_picture_url = serializers.SerializerMethodField(read_only=True)
    address = serializers.CharField(source='user_profile.address', read_only=True)
    state = serializers.CharField(source='user_profile.state', read_only=True)
    city = serializers.CharField(source='user_profile.city', read_only=True)
    pin_code = serializers.CharField(source='user_profile.pin_code', read_only=True)
    latitude = serializers.CharField(source='user_profile.latitude', read_only=True)
    longitude = serializers.CharField(source='user_profile.longitude', read_only=True)
    vendor_slug = serializers.CharField(read_only=True)
    categories = serializers.HyperlinkedRelatedField(read_only=True, view_name='categories-detail', many=True)

    class Meta:
        model = Vendor
        fields = ['vendor_name', 'latitude', 'longitude', 'pin_code', 'city', 'state',
                  'address', 'restaurant_picture_url', 'vendor_slug', 'categories']

    def get_restaurant_picture_url(self, Vendor):
        request = self.context.get('request')
        image_url = Vendor.user_profile.profile_picture.url
        return request.build_absolute_uri(image_url)


class FoodItemSerializer(serializers.ModelSerializer):

    fooditem_picture_url = serializers.SerializerMethodField(read_only=True)
    category = serializers.StringRelatedField()

    class Meta:
        model = FoodItem
        fields = ['category', 'food_title', 'description', 'price', 'fooditem_picture_url']

    def get_fooditem_picture_url(self, fooditem):
        request = self.context.get('request')
        image_url = fooditem.image.url
        return request.build_absolute_uri(image_url)


class ReadCartSerializer(serializers.ModelSerializer):

    quantity = serializers.IntegerField()
    fooditem = FoodItemSerializer(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'quantity', 'fooditem']
        read_only_fields = ['id', 'fooditem']


class CartCreateSerializer(serializers.ModelSerializer):

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    fooditem = serializers.PrimaryKeyRelatedField(
         required=True,
         queryset=FoodItem.objects.all(),
     )
    quantity = serializers.IntegerField(required=True)

    def update(self, instance, validated_data):
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.save()
        return instance

    def create(self, validated_data):
        try:
            instance = Cart.objects.get(user=validated_data['user'], fooditem=validated_data['fooditem'])
            instance.quantity = validated_data.get('quantity', instance.quantity)
            instance.save()
            return instance
        except Exception:
            instance = Cart.objects.get(**validated_data)
            return instance

    class Meta:
        model = Cart
        fields = ['id', 'quantity', 'fooditem', 'user']
        read_only_fields = ['id']


class ProfileSerializer(serializers.ModelSerializer):

    profile_picture = serializers.ImageField(write_only=True)
    profile_picture_url = serializers.SerializerMethodField(read_only=True)
    cover_photo = serializers.ImageField(write_only=True)
    cover_photo_url = serializers.SerializerMethodField(read_only=True)
    address = serializers.CharField(max_length=250, allow_blank=True, allow_null=True)
    country = serializers.CharField(max_length=15, allow_blank=True, allow_null=True)
    state = serializers.CharField(max_length=15, allow_blank=True, allow_null=True)
    city = serializers.CharField(max_length=15, allow_blank=True, allow_null=True)
    pin_code = serializers.CharField(max_length=6, allow_blank=True, allow_null=True)
    latitude = serializers.CharField(max_length=20, allow_blank=True, allow_null=True)
    longitude = serializers.CharField(max_length=20, allow_blank=True, allow_null=True)

    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'cover_photo', 'address', 'country', 'state',
                  'city', 'pin_code', 'latitude', 'longitude', 'profile_picture_url', 'cover_photo_url']

    def get_profile_picture_url(self, profile):
        request = self.context.get('request')
        image_url = profile.profile_picture.url
        return request.build_absolute_uri(image_url)

    def get_cover_photo_url(self, profile):
        request = self.context.get('request')
        image_url = profile.cover_photo.url
        return request.build_absolute_uri(image_url)


class VendorProfileSerializer(serializers.ModelSerializer):

    vendor_name = serializers.CharField(max_length=50)
    vendor_slug = serializers.CharField(max_length=50, read_only=True)
    vendor_license = serializers.ImageField(write_only=True)
    vendor_license_url = serializers.SerializerMethodField(read_only=True)
    is_approved = serializers.BooleanField(read_only=True)
    is_listed = serializers.BooleanField(read_only=True)
    profile_picture = serializers.ImageField(write_only=True, source='user_profile.profile_picture')
    profile_picture_url = serializers.SerializerMethodField(read_only=True)
    cover_photo = serializers.ImageField(write_only=True, source='user_profile.cover_photo')
    cover_photo_url = serializers.SerializerMethodField(read_only=True)
    address = serializers.CharField(max_length=250, allow_blank=True, allow_null=True, source='user_profile.address')
    country = serializers.CharField(max_length=15, allow_blank=True, allow_null=True, source='user_profile.country')
    state = serializers.CharField(max_length=15, allow_blank=True, allow_null=True, source='user_profile.state')
    city = serializers.CharField(max_length=15, allow_blank=True, allow_null=True, source='user_profile.city')
    pin_code = serializers.CharField(max_length=6, allow_blank=True, allow_null=True, source='user_profile.pin_code')
    latitude = serializers.CharField(max_length=20, allow_blank=True, allow_null=True, source='user_profile.latitude')
    longitude = serializers.CharField(max_length=20, allow_blank=True, allow_null=True, source='user_profile.longitude')

    class Meta:
        model = Vendor
        fields = ['vendor_name', 'vendor_slug', 'vendor_license', 'vendor_license_url', 'is_approved',
                  'is_listed', 'profile_picture', 'cover_photo', 'address', 'country', 'state', 'city',
                  'pin_code', 'latitude', 'longitude', 'profile_picture_url', 'cover_photo_url']

    def update(self, instance, validated_data):
        vendor_fields = ('vendor_name', 'vendor_license', )
        profile_fields = ('profile_picture', 'cover_photo', 'address', 'country', 'state', 'city',
                          'pin_code', 'latitude', 'longitude', )

        passed_vendor_name = validated_data.get('vendor_name')
        if passed_vendor_name and instance.vendor_name != validated_data:
            instance.vendor_slug = slugify(passed_vendor_name)

        for field in vendor_fields:
            instance.__setattr__(field, validated_data.get(field, instance.__getattribute__(field)))

        user_profile_data = validated_data.get('user_profile')
        if user_profile_data:
            for field in profile_fields:
                value = user_profile_data.get(field, instance.user_profile.__getattribute__(field))
                instance.user_profile.__setattr__(field, value)

        instance.save()
        return instance

    def get_vendor_license_url(self, vendor):
        request = self.context.get('request')
        image_url = vendor.vendor_license.url
        return request.build_absolute_uri(image_url)

    def get_profile_picture_url(self, vendor):
        request = self.context.get('request')
        image_url = vendor.user_profile.profile_picture.url
        return request.build_absolute_uri(image_url)

    def get_cover_photo_url(self, vendor):
        request = self.context.get('request')
        image_url = vendor.user_profile.cover_photo.url
        return request.build_absolute_uri(image_url)


class CustomerProfileSerializer(serializers.ModelSerializer):

    first_name = serializers.CharField(max_length=50, source='user.first_name')
    last_name = serializers.CharField(max_length=50, source='user.last_name')
    phone_number = serializers.CharField(max_length=12, source='user.phone_number')
    profile_picture = serializers.ImageField(write_only=True)
    profile_picture_url = serializers.SerializerMethodField(read_only=True)
    cover_photo = serializers.ImageField(write_only=True)
    cover_photo_url = serializers.SerializerMethodField(read_only=True)
    address = serializers.CharField(max_length=250, allow_blank=True, allow_null=True)
    country = serializers.CharField(max_length=15, allow_blank=True, allow_null=True)
    state = serializers.CharField(max_length=15, allow_blank=True, allow_null=True)
    city = serializers.CharField(max_length=15, allow_blank=True, allow_null=True)
    pin_code = serializers.CharField(max_length=6, allow_blank=True, allow_null=True)
    latitude = serializers.CharField(max_length=20, allow_blank=True, allow_null=True)
    longitude = serializers.CharField(max_length=20, allow_blank=True, allow_null=True)

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'phone_number', 'profile_picture',
                  'cover_photo', 'address', 'country', 'state', 'city', 'pin_code',
                  'latitude', 'longitude', 'profile_picture_url', 'cover_photo_url']

    def get_profile_picture_url(self, profile):
        request = self.context.get('request')
        image_url = profile.profile_picture.url
        return request.build_absolute_uri(image_url)

    def get_cover_photo_url(self, profile):
        request = self.context.get('request')
        image_url = profile.cover_photo.url
        return request.build_absolute_uri(image_url)

    def update(self, instance, validated_data):
        user_fields = ('first_name', 'last_name', 'phone_number', )
        profile_fields = ('profile_picture', 'cover_photo', 'address', 'country',
                          'state', 'city', 'pin_code', 'latitude', 'longitude', )

        for field in profile_fields:
            instance.__setattr__(field, validated_data.get(field, instance.__getattribute__(field)))

        user_profile_data = validated_data.get('user')
        if user_profile_data:
            for field in user_fields:
                value = user_profile_data.get(field, instance.user.__getattribute__(field))
                instance.user.__setattr__(field, value)

        instance.save()
        return instance
