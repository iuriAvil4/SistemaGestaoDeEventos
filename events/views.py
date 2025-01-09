from django.shortcuts import render
from django.utils.text import slugify
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from core.permissions import IsAdminUser, IsOrganizerUser, IsParticipantUser
from .models import Event, Category
from .serializer import EventRegisterSerializer, EventSerializer, CategorySerializer


def generate_slug(name):
    return slugify(name)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_event(request):
    serializer = EventRegisterSerializer(data=request.data)
    if serializer.is_valid():
        validated_data = serializer.validated_data
        name = validated_data.get('name', '')
        slug = generate_slug(name)
        
        
        event = Event.objects.create(**validated_data, slug=slug)
        
        response_serializer = EventRegisterSerializer(event)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



