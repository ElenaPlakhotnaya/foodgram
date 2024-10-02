from rest_framework import serializers
from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient
from django.core.files.base import ContentFile
import base64

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class IngredientSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Ingredient
        fields = '__all__'

class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient.id')

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']

class RecipeSerializer(serializers.ModelSerializer):
    ingredient = RecipeIngredientSerializer(many=True, read_only=True)
    tag = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    image = Base64ImageField(required=False, allow_null=True)
    class Meta:
        model = Recipe
        fields = '__all__'