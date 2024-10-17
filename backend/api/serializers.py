import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from rest_framework import serializers

from recipes.models import (Favourite, Ingredient, Recipe, RecipeIngredient,
                            RecipeTag, ShoppingCart, Tag)
from users.models import Subscription
from users.serializers import UserSerializer

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class FavouriteAndShoppingCrtSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class RecipeTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeTag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Параметр "amount" должен быть больше 1')
        return value


class RecipeSafeMethodsSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField(required=False, allow_null=True)
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'image', 'text', 'author', 'ingredients',
            'tags', 'cooking_time', 'is_in_shopping_cart', 'is_favorited'
        ]

    def get_is_favorited(self, obj):
        return Favourite.objects.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        return ShoppingCart.objects.filter(recipe=obj).exists()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['ingredients'] = [
            {
                'id': ingredient.ingredient.id,
                'name': ingredient.ingredient.name,
                'measurement_unit': ingredient.ingredient.measurement_unit,
                'amount': ingredient.amount
            }
            for ingredient in instance.recipe_ingredients.all()
        ]
        return representation


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredients', required=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), required=True)
    image = Base64ImageField(required=True, allow_null=True)
    author = UserSerializer(required=False)
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'image', 'text', 'author',
            'ingredients', 'tags', 'cooking_time',
            'is_in_shopping_cart', 'is_favorited'
        ]

    def get_is_favorited(self, obj):
        return Favourite.objects.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        return ShoppingCart.objects.filter(recipe=obj).exists()

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.pop('id')
            amount = ingredient_data.get('amount')
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError(
                    f'Ингредиент с ID {ingredient_id} не найден.')
            ingredient = Ingredient.objects.get(id=ingredient_id)
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=ingredient, amount=amount)
        recipe.tags.set(tags_data)
        print('tags data', tags_data)
        return recipe

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['tags'] = [
            {
                'id': tag.id,
                'name': tag.name,
                'slug': tag.slug,
            }
            for tag in instance.tags.all()
        ]
        representation['ingredients'] = [
            {
                'id': ingredient.ingredient.id,
                'name': ingredient.ingredient.name,
                'measurement_unit': ingredient.ingredient.measurement_unit,
                'amount': ingredient.amount
            }
            for ingredient in instance.recipe_ingredients.all()
        ]
        return representation

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Время приготовления должно превышать 1 минуту')
        return value

    def validate(self, value):
        tags = value.get('tags')
        ingredients = value.get('recipe_ingredients')

        if not tags:
            raise serializers.ValidationError('Необходимо выбрать тэги')
        if not ingredients:
            raise serializers.ValidationError('Необходимо выбрать ингридиенты')

        return value

    def validate_tags(self, value):

        if len(value) != len(set(value)):
            raise serializers.ValidationError('Теги должны быть уникальны')
        if len(value) < 1:
            raise serializers.ValidationError('Поле не может быть пустым.')
        return value

    def validate_ingredients(self, value):

        ingredient_list = []
        for item in value:
            if item in ingredient_list:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться.')
            ingredient_list.append(item)
        if len(ingredient_list) < 1:
            raise serializers.ValidationError('Поле не может быть пустым.')

        return value

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)

        tags_data = validated_data.pop('tags', None)
        if tags_data is not None:
            instance.tags.set(tags_data)

        ingredients_data = validated_data.pop('recipe_ingredients', [])
        instance.recipe_ingredients.all().delete()
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.pop('id')
            amount = ingredient_data.get('amount')
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError(
                    f'Ингредиент с ID {ingredient_id} не найден.')

            ingredient = Ingredient.objects.get(id=ingredient_id)
            RecipeIngredient.objects.create(
                recipe=instance, ingredient=ingredient, amount=amount)

        instance.save()
        return instance


class SubscribingSerializer(serializers.ModelSerializer):
    """сериализация подписчика"""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'avatar', 'is_subscribed', 'recipes', 'recipes_count')
        read_only_fields = ('id',)

    def get_is_subscribed(self, obj):
        return Subscription.objects.filter(user=obj).exists()

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj)
        return RecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def validate_subscribing(self, value):

        if value == self.context['request'].user:
            raise serializers.ValidationError(
                'Вы не можете подписаться на себя')
        return value


class SubscribeSerializer(serializers.ModelSerializer):
    """создание подписки"""
    subscribing = SubscribingSerializer(required=False)

    class Meta:
        model = Subscription
        fields = ('subscribing',)

    def create(self, validated_data):
        subscribing_data = validated_data.pop('subscribing')
        subscribing_user = User.objects.get(**subscribing_data)

        subscription = Subscription.objects.create(
            user=self.context['request'].user,
            subscribing=subscribing_user
        )
        return subscription

    def validate_subscribing(self, value):
        user = self.context['request'].user
        if Subscription.objects.filter(user=user, subscribing=value).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя.')
        if value == self.context['request'].user:
            raise serializers.ValidationError(
                'Вы не можете подписаться на себя')
        return value
