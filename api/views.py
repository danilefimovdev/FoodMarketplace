import rest_framework.status
from django.contrib import auth
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, GenericViewSet
from rest_framework import status, mixins

from accounts.models import UserProfile
from api.filters import filter_fooditems
from api.permissions import IsOwner, IsCustomerAccountOwner, IsCustomer, IsVendor, IsVendorAccountOwner
from api.serializers import CustomAuthTokenSerializer, VendorCreateSerializer, UserCreateSerializer, \
    ForgetPasswordFormSerializer, RestaurantSerializer, FoodItemSerializer, ReadCartSerializer, CartCreateSerializer, \
    CustomerProfileSerializer, VendorProfileSerializer, CustomerOrderShortInfoSerializer, \
    CustomerOrderFullInfoSerializer, \
    VendorOrderFullInfoSerializer, VendorOrderShortInfoSerializer
from marketplace.models import Cart
from marketplace.services.cart_manipulation_services import get_cart_amounts
from menu.models import FoodItem
from orders.models import Order
from vendors.models import Vendor


class TokenAuthenticationViewSet(ViewSet):

    @action(methods=['POST'], detail=False, url_path='login')
    def login(self, request):
        serializer = CustomAuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
        })

    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated, ], url_path='logout')
    def logout(self, request):
        Token.objects.get(key=request.auth).delete()
        auth.logout(request)
        return Response(1)


class UsersViewSet(ViewSet):

    @action(methods=['POST'], detail=False, url_path='customer')
    def register_customer(self, request):
        data = dict(request.data)
        data.update({'role': 2})
        serializer = UserCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        message = 'Verification email was sent to your email address.'
        return Response(status=rest_framework.status.HTTP_201_CREATED,
                        data={'email': data['email'], 'message': message})

    @action(methods=['POST'], detail=False, url_path='vendor', parser_classes=[MultiPartParser])
    def register_vendor(self, request):
        data = request.data.dict()
        data.update({'role': 1})
        serializer = VendorCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        message = 'Verification email was sent to your email address.'
        return Response(status=status.HTTP_201_CREATED,
                        data={'email': data['email'], 'message': message})

    @action(methods=['POST'], detail=False, url_path='forget-password')
    def reset_password(self, request):
        serializer = ForgetPasswordFormSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        message = 'Reset password link was was sent to your email address.'
        return Response(status=status.HTTP_200_OK, data={'email': request.data['email'], 'message': message})


class RestaurantsViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):

    lookup_field = 'vendor_slug'

    @action(methods=['GET'], detail=True, url_path='fooditems')
    def show_fooditems(self, request, **kwargs):
        vendor = self.get_queryset()
        fooditems = vendor.fooditems.filter(is_available=True)
        fooditems = filter_fooditems(queryset=fooditems, filter_params=self.request.query_params.dict())
        serializer = self.get_serializer_class()(data=fooditems, many=True, context={'request': request})
        serializer.is_valid()
        return Response({'fooditems': serializer.data})

    def get_queryset(self, vendor_pk=None):
        vendor_slug = self.kwargs.get('vendor_slug')
        if vendor_slug:
            return Vendor.objects.get(vendor_slug=vendor_slug)
        return Vendor.objects.valid_vendors()

    def get_serializer_class(self):
        if self.action == 'fooditems':
            return FoodItemSerializer
        else:
            return RestaurantSerializer


class FoodItemsViewSet(mixins.RetrieveModelMixin, GenericViewSet):

    serializer_class = FoodItemSerializer

    def get_queryset(self):
        queryset = FoodItem.objects.filter(is_available=True)
        return queryset


class CartViewSet(mixins.DestroyModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                  mixins.RetrieveModelMixin, GenericViewSet):

    permission_classes = [IsAuthenticated, IsCustomer, IsCustomerAccountOwner, IsOwner]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer_class()(data=queryset, many=True, context={'request': request})
        serializer.is_valid()
        amounts = get_cart_amounts(user_id=request.user.pk)
        return Response(data={'carts': serializer.data, 'cart_amounts': amounts})

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReadCartSerializer
        else:
            return CartCreateSerializer

    def get_queryset(self):
        if self.action == 'list':
            return Cart.objects.filter(user=self.request.user)
        else:
            return Cart.objects.all()


class ProfileViewSet(GenericViewSet, mixins.RetrieveModelMixin):

    VENDOR = 1
    CUSTOMER = 2

    @action(methods=['GET', 'PUT', 'PATCH'], detail=False, url_path='profile')
    def profile(self, request, *args, **kwargs):

        if self.request.method == 'GET':
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        else:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(data=serializer.data)

    def get_serializer_class(self):

        if self.request.user.role == self.VENDOR:
            return VendorProfileSerializer
        else:
            return CustomerProfileSerializer

    def get_queryset(self):

        if self.request.user.role == self.VENDOR:
            return Vendor.objects.select_related('user_profile').all()
        else:
            return UserProfile.objects.select_related('user').all()

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), user=self.request.user)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.user.role == self.VENDOR:
            permission_classes.append(IsVendorAccountOwner)
        else:
            permission_classes.append(IsCustomerAccountOwner)
        return permission_classes


class CustomerOrdersViewSet(GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):

    VENDOR = 1
    CUSTOMER = 2

    lookup_field = 'order_number'
    permission_classes = [IsAuthenticated, IsCustomer, IsCustomerAccountOwner]

    def get_serializer_class(self):

        if self.kwargs.get('order_number'):
            return CustomerOrderFullInfoSerializer
        else:
            return CustomerOrderShortInfoSerializer

    def get_queryset(self):

        return Order.objects.filter(user=self.request.user)

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), order_number=self.kwargs.get('order_number')).order_by('-created_at')
        self.check_object_permissions(self.request, obj)
        return obj


class VendorOrdersViewSet(GenericViewSet, mixins.ListModelMixin):

    lookup_field = 'order_number'
    permission_classes = [IsAuthenticated, IsVendor, IsVendorAccountOwner]

    def list(self, request, *args, **kwargs):
        vendor = Vendor.objects.get(vendor_slug=self.kwargs['vendor_slug'])
        queryset = self.get_queryset()
        serializer = self.get_serializer_class()(queryset, many=True, context={'vendor_pk': vendor.pk})
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        vendor = Vendor.objects.get(vendor_slug=self.kwargs['vendor_slug'])
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'vendor_pk': vendor.pk})
        return Response(serializer.data)

    def get_queryset(self):

        return Order.objects.filter(vendor__vendor_slug__in=[self.kwargs['vendor_slug']]).order_by('-created_at')

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), order_number=self.kwargs.get('order_number'))
        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_class(self):

        if self.kwargs.get('order_number'):
            return VendorOrderFullInfoSerializer
        else:
            return VendorOrderShortInfoSerializer
