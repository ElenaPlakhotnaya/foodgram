from django.urls import include, path
from rest_framework import routers
from users.views import UserViewSet, UserAvatarViewSet, SubscriptionViewSet, SubscribeViewSet


router = routers.DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('users/me/avatar', UserAvatarViewSet, basename='avatar')
router.register('users/subscriptions/', SubscriptionViewSet,
                basename='subscriptions')
router.register(r'users/(?P<user_id>\d+)/subscribe/',
                SubscribeViewSet, basename='subscribe')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
