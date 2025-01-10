from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from core.permissions import IsAdminUser, IsOrganizerUser, IsParticipantUser
from .models import Event, Category
from .serializer import EventRegisterSerializer, EventSerializer, CategorySerializer


@api_view(['POST'])
@permission_classes([IsOrganizerUser, IsAuthenticated])
def create_event(request):
    user = request.user
    data = request.data.copy()
    serializer = EventRegisterSerializer(data=data, context={'request': request})
    if serializer.is_valid():
        event = serializer.save(organizer=user) 
        response_serializer = EventRegisterSerializer(event)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_category(request):
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
