from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import User, Subscription
from django.core.files.base import ContentFile
import base64
#from api.serializers import RecipeSerializer
from recipes.models import Recipe

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
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'avatar', 'is_subscribed')
        read_only_fields = ('id',)
    
    def get_is_subscribed(self, obj):
        return Subscription.objects.filter(user=obj).exists()
    """
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['is_subscribed'] = self.get_is_subscribed(instance)

        if representation['avatar']:
            representation['avatar'] = self.context['request'].build_absolute_uri(instance.avatar.url)
        else:
            representation['avatar'] = None

        return representation
    """
class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageFieldAvatar(required=True)

    class Meta:
        model = User
        fields = ('avatar',)

class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=['user', 'subscribing']
            )
        ]
    def validate_subscribing(self, value):
        if value == self.context['request'].user:
            raise serializers.ValidationError(
                "Вы не можете подписаться сами на себя")
        return value
    
    def create(self, validated_data):
        subscription = Subscription.objects.create(**validated_data)
        return subscription

"""
class SubscribingSerializer(serializers.ModelSerializer):
    
    is_subscribed = serializers.SerializerMethodField()
    #recipes = RecipeSerializer()
    recipes_count = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'avatar', 'is_subscribed', 'recipes', 'recipes_count')
        read_only_fields = ('id',)
    def get_is_subscribed(self, obj):
        return Subscription.objects.filter(user=obj).exists()
    def get_recipes_count(self, request, *args, **kwargs):
        user = request.user
        recipe_count = Recipe.objects.filter(author=user).count()
        return recipe_count
    


class SubscribeSerializer(serializers.ModelSerializer):
   
    subscribing = SubscribingSerializer(required=False)
    class Meta:
        model = Subscription
        fields = ('subscribing',)

    def validate(self, value):
        user = value.get('user')
        subscribing = value.get('subscribing')

        if Subscription.objects.filter(user=user, subscribing=subscribing).exists():
            raise serializers.ValidationError("Вы уже подписаны на этого пользователя.")
        
        return value    
    
"""