from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from api.serializers import SubscribeSerializer, SubscribingSerializer
from users.models import Subscription, User
from users.serializers import UserAvatarSerializer, UserSerializer


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = []
    pagination_class = LimitOffsetPagination

    @action(
        detail=False, methods=['get'],
        url_path='me',
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        user = request.user
        user_me = User.objects.get(id=user.id)
        serializer = UserSerializer(user_me)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True, methods=['post', 'delete'],
        url_path='subscribe',
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscribe(self, request, *args, **kwargs):
        subscribing = self.get_object()
        if request.method == 'POST':
            if request.user == subscribing:
                return Response(
                    {'errors': 'Вы не можете подписаться сами на себя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Subscription.objects.filter(
                user=request.user, subscribing=subscribing
            ).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscription.objects.create(
                user=request.user, subscribing=subscribing)
            serializer = SubscribingSerializer(subscribing)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = Subscription.objects.filter(
                user=request.user, subscribing=subscribing)
            if subscription:
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False, methods=['get'],
        url_path='subscriptions',
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscriptions(self, request):
        user_subscriptions = Subscription.objects.filter(
            subscribing=request.user)
        paginator = self.paginator
        paginated_subscriptions = paginator.paginate_queryset(
            user_subscriptions, request)
        serializer = SubscribeSerializer(paginated_subscriptions, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(
        detail=False, methods=['put', 'delete'],
        url_path='me/avatar',
        permission_classes=[permissions.IsAuthenticated]
    )
    def avatar(self, request):
        user = request.user

        if request.method == 'PUT':
            serializer = UserAvatarSerializer(user, data=request.data)
            if serializer.is_valid():

                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete(save=False)
                user.avatar = None
                user.save()
                return Response(
                    {'status': 'Аватар удален.'},
                    status=status.HTTP_204_NO_CONTENT
                )
            return Response(
                {'errors': 'Объект не существует.'},
                status=status.HTTP_404_NOT_FOUND
            )
