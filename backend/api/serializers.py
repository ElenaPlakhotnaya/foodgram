from django.contrib.auth import get_user_model
from django.db.models import F

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.fields import Base64ImageField
from recipes.models import (Favourite, Ingredient, Recipe, RecipeIngredient,
                            RecipeTag, ShoppingCart, Tag)
from users.models import Subscription
from users.serializers import UserSerializer

User = get_user_model()


class FavouriteAndShoppingCrtSerializer(serializers.ModelSerializer):
    """Сериализация избранного и корзины покупок."""
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
    """Сериализация тегов."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug',)


class RecipeTagSerializer(serializers.ModelSerializer):
    """Сериализация тегов в рецептах."""
    class Meta:
        model = RecipeTag
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализация ингредиентов в рецептах."""
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализация ингредиентов."""
    amount = RecipeIngredientSerializer(read_only=True)

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализация рецептов для чтения."""
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
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

    def get_ingredients(self, obj):
        recipe = obj
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('recipe_ingredients__amount')
        )

        return ingredients


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализация рецептов для записи."""
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredients', required=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), required=True)
    image = Base64ImageField(required=True, allow_null=True)
    author = UserSerializer(required=False)

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'image', 'text', 'author',
            'ingredients', 'tags', 'cooking_time',
        ]

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)

        recipe_ingredients = []
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.pop('id')
            amount = ingredient_data.get('amount')
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError(
                    f'Ингредиент с ID {ingredient_id} не найден.')

            if amount < 1:
                raise serializers.ValidationError(
                    f'{amount} не может быть меньше 1.'
                )

            ingredient = Ingredient.objects.get(id=ingredient_id)

            recipe_ingredients.append(RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            ))

        RecipeIngredient.objects.bulk_create(recipe_ingredients)

        return recipe

    def to_representation(self, instance):
        return RecipeReadSerializer(instance).data

    def validate(self, value):
        tags = value.get('tags')
        ingredients = value.get('recipe_ingredients')

        if not tags:
            raise serializers.ValidationError('Необходимо выбрать тэги.')
        if not ingredients:
            raise serializers.ValidationError(
                'Необходимо выбрать ингридиенты.')

        return value

    def validate_tags(self, value):

        if len(value) != len(set(value)):
            raise serializers.ValidationError('Теги не должны повторяться.')
        if len(value) < 1:
            raise serializers.ValidationError('Добавьте теги.')
        return value

    def validate_ingredients(self, value):
        ingredient_list = []
        for item in value:
            if item in ingredient_list:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться.')
            ingredient_list.append(item)

        if len(ingredient_list) < 1:

            raise serializers.ValidationError('Добавьте ингридиенты.')

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
            if amount < 1:
                raise serializers.ValidationError(
                    f'{amount} не может быть меньше 1.'
                )

            ingredient = Ingredient.objects.get(id=ingredient_id)
            RecipeIngredient.objects.create(
                recipe=instance, ingredient=ingredient, amount=amount)

        instance.save()
        return instance


class SubscribingSerializer(serializers.ModelSerializer):
    """Сериализация подписчика."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'avatar', 'is_subscribed', 'recipes', 'recipes_count')
        read_only_fields = ('id',)

    def get_is_subscribed(self, obj):
        return Subscription.objects.filter(
            user=self.context['request'].user,
            subscribing=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        queryset = obj.recipes.all()
        limit = request.query_params.get('recipes_limit')
        if limit:
            try:
                queryset = queryset[:int(limit)]
            except (TypeError, ValueError):
                pass
        return FavouriteAndShoppingCrtSerializer(
            queryset,
            many=True,
            context={'request': request},
        ).data


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализация подписок."""

    class Meta:
        model = Subscription
        fields = ('user', 'subscribing',)
        validators = [
            UniqueTogetherValidator(
                fields=('user', 'subscribing'),
                queryset=model.objects.all(),
                message='Вы уже подписаны на этого пользователя.',
            )
        ]

    def validate_subscribing(self, data):

        if self.context.get('request').user == data:
            raise serializers.ValidationError(
                'Вы не можете подписаться сами на себя.'
            )
        return data

    def to_representation(self, instance):
        return SubscribingSerializer(
            instance.subscribing,
            context=self.context,
        ).data
