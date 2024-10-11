from djoser.views import UserViewSet
from users.models import User, Subscription
from users.serializers import UserSerializer, UserAvatarSerializer, SubscriptionSerializer
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import viewsets, permissions
from rest_framework.response import Response

class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination
    

class UserAvatarViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserAvatarSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    def get_queryset(self):
        return self.request.user.subscribing.all()

class SubscribeViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        return self.request.user.subscribing.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)