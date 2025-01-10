from django.urls import path
from .views import create_event, create_category

urlpatterns = [
    path('create_event/', create_event),
    path('create_category/', create_category)
]
