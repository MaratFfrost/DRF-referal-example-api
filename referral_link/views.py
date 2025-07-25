from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.hashers import make_password
from django.contrib.auth import login as django_login, logout as django_logout
from django.utils.crypto import get_random_string
from django.core.cache import cache

from .models import ReferralLinkUser
from .utils import send_code
from .serializer import ReferralLinkUserSerializer

from random import randint
import re

CODE_TIMEOUT = 300
PHONE_REGEX = r'^(\+7|8)[0-9]{10}$'


def normalize_number(phone_number):
    if not re.match(PHONE_REGEX, phone_number):
        return None
    return '+7' + phone_number[-10:]


def auth_test(request):
    return render(request, 'test.html')


@api_view(['POST'])
def get_code(request):
    if request.user.is_authenticated:
        return Response({'error': 'You are already logged in.'},
                        status=status.HTTP_400_BAD_REQUEST)

    phone_number = request.data.get('phone_number')

    if not phone_number:
        return Response(
            {'error': 'Phone number is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    normalized_phone = normalize_number(phone_number)

    if not normalized_phone:
        return Response(
            {'error': '''Invalid phone number format.
             Use +7XXXXXXXXXX or 8XXXXXXXXXX'''},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        with cache.lock(f'phone_lock:{normalized_phone}', timeout=5):
            if cache.get(f'code:{normalized_phone}'):
                return Response(
                    {'error': 'Code already sent. Please wait.'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

            code = randint(1000, 9999)
            cache.set(f'code:{normalized_phone}', code, CODE_TIMEOUT)

            # тут лучше сделать отправку через celery или на сторонний сервес
            send_code()

    except Exception:
        return Response(
            {'error': 'Service temporarily unavailable. Please try again.'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    return Response(
        {
            "code": code,
            'status': 'success',
            'code_valid_for': f"{CODE_TIMEOUT // 60} minutes",
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
def login(request):

    if request.user.is_authenticated:
        return Response({'error': 'You are already logged in.'},
                        status=status.HTTP_400_BAD_REQUEST)

    phone_number = request.data.get('phone_number')
    code = request.data.get('code')

    if not phone_number or not code:
        return Response(
            {'error': 'Phone number and code are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    normalized_phone = normalize_number(phone_number)

    if not normalized_phone:
        return Response(
            {'error': '''Invalid phone number format.
             Use +7XXXXXXXXXX or 8XXXXXXXXXX'''},
            status=status.HTTP_400_BAD_REQUEST
        )

    cached_code = cache.get(f'code:{normalized_phone}')

    if not cached_code or str(cached_code) != str(code):
        return Response(
            {'error': 'Invalid code.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    else:
        try:
            random_password = get_random_string(length=10)
            user, _ = ReferralLinkUser.objects.get_or_create(
                phone_number=normalized_phone,
                defaults={
                  'username': normalized_phone,
                  'password': make_password(random_password)}
                )

            django_login(request, user)

            cache.delete(f'code:{normalized_phone}')

            return Response({
                'detail': 'Login successful.',
                'user': user.username,
                'unique_code': user.referral_code
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Service temporarily unavailable. Try again. {e}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        django_logout(request)
        return Response(
            {'detail': 'Successfully logged out'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user

    invited_users = ReferralLinkUser.objects.filter(
        invited_by=user
    )

    return Response({
        'phone_number': getattr(user, 'phone_number', None),
        'referral_code': getattr(user, 'referral_code', None),
        'invited_users': ReferralLinkUserSerializer(
            invited_users,
            many=True).data
    }, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def enter_code(request):
    user = request.user
    code = request.data.get('code')

    if user.invited_by:
        return Response(
            {'error': 'You have already been invited.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not code:
        return Response(
            {'error': 'Code is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        invited_user = ReferralLinkUser.objects.get(referral_code=code)

        user.invited_by = invited_user
        user.save()

        return Response(
            {'detail': 'Code entered successfully.'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
