from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

from core.permissions import IsAdminUser, IsOrganizerUser, IsParticipantUser
from .models import Event, Category
from .serializer import EventRegisterSerializer, EventSerializer, CategorySerializer


@api_view(['GET'])
@permission_classes([IsAdminUser | IsOrganizerUser | IsParticipantUser])
def list_events(request):
    events = Event.objects.all().order_by("title")
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdminUser | IsOrganizerUser])
def create_event(request):
    user = request.user
    data = request.data.copy()
    serializer = EventRegisterSerializer(data=data, context={'request': request})
    if serializer.is_valid():
        event = serializer.save(organizer=user) 
        response_serializer = EventRegisterSerializer(event)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminUser | IsOrganizerUser])
def list_organizer_events(request):
    user = request.user
    events = Event.objects.filter(organizer=user) 
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
    

@api_view(['PUT'])
@permission_classes([IsAdminUser | IsOrganizerUser])
def update_event(request, id):
    try:
        event = Event.objects.get(pk=id)
    except Event.DoesNotExist:
        return Response(
            {"error": f"Event with id {id} does not exist."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = EventRegisterSerializer(event, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAdminUser | IsOrganizerUser])
def delete_event(request, id):
    try:
        event = Event.objects.get(pk=id)
        event.delete()
        return Response({"message": f"Event with id {id} deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    except Event.DoesNotExist:
        return Response(
            {"error": f"Event with id {id} does not exist."},
            status=status.HTTP_404_NOT_FOUND
        )

#---------------------------------------------------------------------------------------

@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_category(request):
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_categories(request):
    categories = Category.objects.all().order_by("name")
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
    

@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_category(request, id):
    try:
        category = Category.objects.get(pk=id)
    except Category.DoesNotExist:
        return Response(
            {"error": f"Category with id {id} does not exist."},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = CategorySerializer(category, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_category(request, id):
        try:
            category = Category.objects.filter(pk=id)
            category.delete()
            return Response({"message": f"Category with id {id} deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Event.DoesNotExist:
            return Response(
                {"error": f"Event with id {id} does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )
       
