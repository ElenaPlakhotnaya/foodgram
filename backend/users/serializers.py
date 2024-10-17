import base64

from django.core.files.base import ContentFile

from rest_framework import serializers

from users.models import Subscription, User


class Base64ImageFieldAvatar(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(default=False)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'avatar', 'is_subscribed')
        read_only_fields = ('id',)

    def get_is_subscribed(self, obj):
        return Subscription.objects.filter(user=obj).exists()


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageFieldAvatar(required=True)

    class Meta:
        model = User
        fields = ('avatar',)
