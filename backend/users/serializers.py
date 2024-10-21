

from rest_framework import serializers

from api.fields import Base64ImageField
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализация пользователя."""
    is_subscribed = serializers.SerializerMethodField(default=False)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'avatar', 'is_subscribed')
        read_only_fields = ('id',)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.subscribing.filter(user=request.user).exists()
        return False


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализация аватара пользователя."""
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)
