from django.shortcuts import render
from .models import User
from .serializer import UserRegisterSerializer, UserSerializer, UserOrganizerRegisterSerializer
from core.permissions import IsAdminUser, IsOrganizerUser, IsParticipantUser

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
#CLASSES JWT
class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            tokens = response.data

            access_token = tokens['access']
            refresh_token = tokens['refresh']
        

            res = Response()

            res.data = {'success': True}

            res.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=True,
                samesite=None,
                path='/'
            )

            res.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=True,
                samesite=None,
                path='/'
            )

            return res
        
        except Exception as e:
            print(e)
            return Response({'success':False})

class CustomRefreshTokenView(TokenRefreshView):

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.COOKIES.get('refresh_token')

            request.data['refresh'] = refresh_token

            response = super().post(request, *args, **kwargs)

            tokens = response.data

            access_token = tokens['access']

            res = Response()

            res.data = {'refreshed': True}

            res.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=True,
                samesite='None',
                path='/'
            )

            return res
        
        except:
            return Response({'refreshed': False})



@api_view(['POST'])
@permission_classes([IsAdminUser])
def register_user(request):
    """
    Register a new user. Admin-only access.
    """
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user_organizer(request):
    """
    Register a new organizer user. Accessible to any user.
    """
    serializer = UserOrganizerRegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def logout(request):
    """
    Log out the user by clearing the authentication cookies.
    """
    try:
        res = Response()
        res.data = {'success': True}
        res.delete_cookie('access_token')
        res.delete_cookie('refresh_token')
        return res
    except:
        return Response({'refreshed': False})
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def is_authenticated(request):
    """
    Check if the current user is authenticated.
    """
    return Response({'authenticated': True})


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_users(request):
    """
    Retrieve a list of all active users. Admin-only access.
    """
    users = User.objects.filter(is_active=True)
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)