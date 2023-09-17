import rest_framework.status
from django.contrib import auth
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework import status

from api.serializers import CustomAuthTokenSerializer, VendorCreateSerializer, UserCreateSerializer, \
    ForgetPasswordFormSerializer


class TokenAuthenticationViewSet(ViewSet):

    @action(methods=['POST'], detail=False)
    def login(self, request):
        serializer = CustomAuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
        })

    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated, ])
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

        _MESSAGE = 'Verification email was sent to your email address.'
        return Response(status=status.HTTP_201_CREATED,
                        data={'email': data['email'], 'message': _MESSAGE})

    @action(methods=['POST'], detail=False, url_path='forget-password')
    def reset_password(self, request):
        serializer = ForgetPasswordFormSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        _MESSAGE = 'Reset password link was was sent to your email address.'
        return Response(status=status.HTTP_200_OK, data={'email': request.data['email'], 'message': _MESSAGE})