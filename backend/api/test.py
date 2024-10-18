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
                'Время приготовления должно превышать 1 минуту.')
        return value

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

            ingredient = Ingredient.objects.get(id=ingredient_id)
            RecipeIngredient.objects.create(
                recipe=instance, ingredient=ingredient, amount=amount)

        instance.save()
        return instance