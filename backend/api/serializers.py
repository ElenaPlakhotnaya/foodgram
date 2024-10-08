from rest_framework import serializers
from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient, RecipeTag, Favourite, ShoppingCart
from django.core.files.base import ContentFile
import base64
from users.serializers import UserSerializer

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)
    
class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favourite
        fields = '__all__'


class FavouriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favourite
        fields = '__all__'


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

class RecipeSafeMethodsSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField(required=False, allow_null=True)
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )
    is_in_shopping_cart = serializers.IntegerField(max_value=1, min_value=0)
    is_favorited = serializers.IntegerField(max_value=1, min_value=0)

    class Meta:
        model = Recipe
        fields = '__all__'

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
    ingredients = RecipeIngredientSerializer(many=True, source='recipe_ingredients')
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    image = Base64ImageField(required=False, allow_null=True)
    author = UserSerializer(required=False)
    class Meta:
        model = Recipe
        fields = '__all__'

    def create(self, validated_data):
        print(validated_data)
        ingredients_data = validated_data.pop('recipe_ingredients')
        print("Ingredients data:", ingredients_data)
        tags_data = validated_data.pop('tags')
        print("Tags data:", tags_data)
        recipe = Recipe.objects.create(**validated_data)
        print(recipe)
        
        for ingredient_data in ingredients_data:            
            print("Ingredient data:", ingredient_data)
            ingredient_id = ingredient_data.pop('id')
            amount = ingredient_data.get('amount')
            ingredient = Ingredient.objects.get(id=ingredient_id)
            RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient, amount=amount)
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
    
    