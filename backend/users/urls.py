from django.urls import include, path
from rest_framework import routers
from users.views import UserViewSet, UserAvatarViewSet


router = routers.DefaultRouter()
router.register('users', UserViewSet, basename='users'),
router.register('users/me/avatar', UserAvatarViewSet, basename='avatar'),


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]