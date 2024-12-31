
from django.urls import path
from .views import register_user, get_users, CustomRefreshTokenView, CustomTokenObtainPairView, logout, is_authenticated

urlpatterns = [
    path('register/', register_user),
    path('logout/', logout),
    path('authenticated/', is_authenticated),
    path('', get_users),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomRefreshTokenView.as_view(), name='token_refresh'),
]