from rest_framework import serializers

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
    class Meta:
        model = Subscription
        fields = '__all__'