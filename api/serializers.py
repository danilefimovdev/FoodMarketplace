from django.contrib.auth import authenticate

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts.models import User
from accounts.services import send_reset_password_email
from accounts.services.user_registration_service import register_new_customer, register_new_vendor
from marketplace.models import Cart
from menu.models import Category, FoodItem


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


class VendorCreateSerializer(UserCreateSerializer):

    vendor_name = serializers.CharField(max_length=50)
    vendor_license = serializers.ImageField()

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


class FoodItemSerializer(serializers.ModelSerializer):

    url = serializers.HyperlinkedRelatedField(read_only=True, view_name='fooditems-detail')

    class Meta:
        model = FoodItem
        fields = ['food_title', 'description', 'price', 'image', 'url']


class CategorySerializer(serializers.ModelSerializer):

    fooditems = serializers.HyperlinkedRelatedField(read_only=True, view_name='fooditems-detail', many=True)

    class Meta:
        model = Category
        fields = ['category_name', 'description', 'fooditems']


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
            instance = Cart.objects.create(**validated_data)
            return instance

    class Meta:
        model = Cart
        fields = ['id', 'quantity', 'fooditem', 'user']
        read_only_fields = ['id']
