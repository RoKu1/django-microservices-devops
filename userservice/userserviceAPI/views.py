import binascii
import os
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import MyTokenObtainPairSerializer, MyTokenRefreshSerializer, MyUserSerializer
from rest_framework.viewsets import ViewSet
from django.conf import settings
from django.utils.translation import gettext as _
from .models import SignupCode, send_multi_format_email
from .permissions import IsVerified
from django.db import connection
from django.http import JsonResponse, HttpResponse

User = get_user_model()
must_validate_email = getattr(settings, "AUTH_EMAIL_VERIFICATION", True)


def _generate_code():
    return binascii.hexlify(os.urandom(20)).decode('utf-8')


@api_view(['GET'])
@permission_classes([AllowAny])
def status(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({ "message": "OK"}, status=200)
    except Exception as ex:
        return JsonResponse({ "error": str(ex) }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = MyUserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = User.objects.get(email=request.data["email"])
        if must_validate_email:
            # Create and associate signup code
            ipaddr = request.META.get('REMOTE_ADDR', '0.0.0.0')
            signup_code = SignupCode.objects.create_signup_code(user, ipaddr)
            signup_code.send_signup_email()
        else:
            # set is_verified to true
            user.is_verified = True

        return Response(status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignupVerify(APIView):
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        code = request.GET.get('code', '')
        verified = SignupCode.objects.set_user_is_verified(code)

        if verified:
            try:
                signup_code = SignupCode.objects.get(code=code)
                signup_code.delete()
            except SignupCode.DoesNotExist:
                pass
            content = {'success': _('Email address verified.')}
            return Response(content, status=status.HTTP_200_OK)
        else:
            content = {'detail': _('Unable to verify user.')}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgotpassword(request):
    # serializer = MyUserSerializer(data=request.data)
    email = request.data["email"]
    try:
        user = User.objects.get(email=email)
        temp_pswd = _generate_code()
        user.set_password(temp_pswd)
        user.save()
        ctxt = {
            'email': email,
            'code': temp_pswd
        }
        send_multi_format_email("forgot_pswd", ctxt, email)
        return Response(status.HTTP_202_ACCEPTED)

    except User.DoesNotExist:
        return Response(status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsVerified])
def changepassword(request):
    old_pswd = request.data["old_password"]
    new_pswd = request.data["new_password"]
    user = request.user
    if user.check_password(old_pswd):
        user.set_password(new_pswd)
        user.save()
        return Response(status.HTTP_200_OK)
    else:
        return Response("Old Password Mismatch", status.HTTP_406_NOT_ACCEPTABLE)


class UserViewSet(ViewSet):
    permission_classes = [IsAuthenticated, IsVerified]

    def retrieve(self, request):
        try:
            user = request.user
            serializer = MyUserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request):
        if "password" in request.data:
            return Response("Cannot update pswd. Nice Try ;)", status=status.HTTP_403_FORBIDDEN)
        if "email" in request.data:
            return Response("Cannot update username/email. Nice Try ;)", status=status.HTTP_403_FORBIDDEN)

        user = request.user
        serializer = MyUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request):
        try:
            request.user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class MyObtainTokenPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = MyTokenObtainPairSerializer


class MyTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
    serializer_class = MyTokenRefreshSerializer
