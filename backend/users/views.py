from djoser.views import UserViewSet
from users.models import User, Subscription
from users.serializers import UserSerializer, UserAvatarSerializer, SubscriptionSerializer
from api.serializers import SubscribeSerializer
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination

    @action(detail=True, methods=['post', 'delete'], url_path='subscriber', permission_classes=[permissions.IsAuthenticated])
    def subscriber(self, request, pk):
        subscribing = get_object_or_404(User, id=pk)

        if request.method == 'POST':
            if Subscription.objects.filter(user=request.user, subscribing=subscribing).exists():
                return Response({'errors': 'подписка существует'}, status=status.HTTP_400_BAD_REQUEST)
            Subscription.objects.create(user=request.user, subscribing=subscribing)
            serializer = SubscribeSerializer(subscribing)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            favourite = Subscription.objects.filter(user=request.user, subscribing=subscribing)
            if favourite.exists():
                favourite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'вы уже отписались'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='subscriptions', permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        user_subscriptions = Subscription.objects.filter(user=request.user).select_related('subscribing')
        serializer = SubscribeSerializer(user_subscriptions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)       


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
    serializer_class = SubscribeSerializer
    pagination_class = LimitOffsetPagination
    def get_user(self):
        return get_object_or_404(User, id=self.kwargs.get('user_id'))

    def get_queryset(self):
        return self.get_user().subscribing.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, subscribing=self.get_user())
