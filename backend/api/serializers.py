from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.fields import Base64ImageField
from recipes.models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag
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
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:

        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class CreateIngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализация создания ингредиента в рецепте."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
        error_messages={
            'does_not_exist': 'Ингредиент с указанным ID не существует.'
        }
    )

    class Meta:

        model = RecipeIngredient
        fields = (
            'id',
            'amount',
        )

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Количество должно быть больше 0.")
        return value


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализация ингредиентов."""
    amount = RecipeIngredientSerializer(read_only=True)

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализация рецептов для чтения."""
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients',
        many=True,
        read_only=True,
    )
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(required=False)
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'text', 'author',
            'ingredients', 'tags', 'cooking_time',
            'is_in_shopping_cart', 'is_favorited'
        )

    def get_user(self):
        request = self.context.get('request')
        return request.user if request else None

    def get_is_favorited(self, obj):
        user = self.get_user()
        if user and not user.is_anonymous:
            return obj.favorites.filter(user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.get_user()
        if user and not user.is_anonymous:
            return obj.shopping_carts.filter(user=user).exists()
        return False

    def add_to_favorites(self, user, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if recipe.favorites.filter(user=user).exists():
            raise serializers.ValidationError(
                'Рецепт уже был добавлен в избранное.')
        user.favorites.create(recipe=recipe)
        return FavouriteAndShoppingCrtSerializer(recipe).data

    def remove_from_favorites(self, user, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        favourite = user.favorites.filter(recipe=recipe).first()
        if not favourite:
            raise serializers.ValidationError(
                'Рецепт уже был удален из избранного.')
        favourite.delete()

    def add_to_shopping_cart(self, user, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if recipe.shopping_carts.filter(user=user).exists():
            raise serializers.ValidationError(
                'Рецепт уже был добавлен в корзину.')
        user.shopping_carts.create(recipe=recipe)
        return FavouriteAndShoppingCrtSerializer(recipe).data

    def remove_from_shopping_cart(self, user, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        shopping_cart_item = user.shopping_carts.filter(recipe=recipe).first()
        if not shopping_cart_item:
            raise serializers.ValidationError(
                'Рецепт уже был удален из корзины.')
        shopping_cart_item.delete()


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализация рецептов для записи."""
    ingredients = CreateIngredientInRecipeSerializer(
        many=True, source='recipe_ingredients', required=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), required=True)
    image = Base64ImageField(required=True, allow_null=True)
    author = UserSerializer(required=False)

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'text', 'author',
            'ingredients', 'tags', 'cooking_time',
        )

    @staticmethod
    def _set_ingredients_and_tags(validated_data, recipe):
        ingredients = validated_data.pop('recipe_ingredients', [])
        tags = validated_data.pop('tags', [])
        recipe.tags.set(tags)
        ingredients_in_recipe = []
        for ingredient in ingredients:
            ingredients_in_recipe.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient.get('ingredient'),
                    amount=ingredient.get('amount'),
                )
            )
        RecipeIngredient.objects.bulk_create(ingredients_in_recipe)

    def create(self, validated_data):
        print(validated_data)
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            image=validated_data.pop('image'),
            name=validated_data.pop('name'),
            text=validated_data.pop('text'),
            cooking_time=validated_data.pop('cooking_time'), )
        self._set_ingredients_and_tags(
            validated_data,
            recipe
        )
        return recipe

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()
        self._set_ingredients_and_tags(
            validated_data,
            instance,
        )
        return super().update(instance, validated_data)

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
