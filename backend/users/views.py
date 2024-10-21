from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import SubscribeSerializer
from users.models import Subscription, User
from users.paginators import CustomPagination
from users.serializers import UserAvatarSerializer, UserSerializer


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = []
    pagination_class = CustomPagination

    @action(
        detail=False, methods=['get'],
        url_path='me',
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        user = request.user
        user_me = get_object_or_404(User, id=user.id)
        serializer = UserSerializer(user_me)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True, methods=['post'],
        url_path='subscribe',
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscribe_post(self, request, **kwargs):
        user = request.user
        subscribing = get_object_or_404(User, pk=self.kwargs.get('id'))
        serializer = SubscribeSerializer(
            data={
                'user': user.id,
                'subscribing': subscribing.id,
            },
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe_post.mapping.delete
    def subscribe_delete(self, request, *args, **kwargs):
        subscribing = get_object_or_404(User, pk=self.kwargs.get('id'))
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
            user=self.request.user)
        paginator = self.paginate_queryset(user_subscriptions)
        serializer = SubscribeSerializer(paginator,
                                         context={'request': request},
                                         many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False, methods=['put'],
        url_path='me/avatar',
        permission_classes=[permissions.IsAuthenticated]
    )
    def avatar_put(self, request):
        user = request.user

        serializer = UserAvatarSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @avatar_put.mapping.delete
    def avatar_delete(self, request):
        user = request.user
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
