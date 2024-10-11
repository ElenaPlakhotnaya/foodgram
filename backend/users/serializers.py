from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import User, Subscription

class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'avatar', 'is_subscribed')
        read_only_fields = ('id',)
    
    def get_is_subscribed(self, obj):
        return Subscription.objects.filter(user=obj).exists()
    
class UserAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('avatar',)

class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username', read_only=True,
        default=serializers.CurrentUserDefault()
    )
    subscribing = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())

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

    def update(self, instance, validated_data):
        instance.subscribing = validated_data.get('subscribing', instance.subscribing)
        instance.save()
        return instance