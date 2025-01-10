
from django.urls import path
from .views import register_user, register_user_organizer, get_users, CustomRefreshTokenView, CustomTokenObtainPairView, logout, is_authenticated

urlpatterns = [
    path('register/', register_user),
    path('register_user_organizer/', register_user_organizer),
    path('logout/', logout),
    path('authenticated/', is_authenticated),
    path('', get_users),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomRefreshTokenView.as_view(), name='token_refresh'),
]