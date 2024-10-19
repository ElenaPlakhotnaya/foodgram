from django.contrib import admin
from django.core.exceptions import ValidationError

from recipes.models import (Favourite, Ingredient, Recipe, RecipeIngredient,
                            RecipeTag, ShoppingCart, Tag)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'get_ingredients', 'get_tags')
    search_fields = ('author', 'name',)
    list_filter = ('tags',)
    empty_value_display = '---'

    def get_ingredients(self, obj):
        return ', '.join(
            [ingredient.name for ingredient in obj.ingredients.all()]
        )
    get_ingredients.short_description = 'Ингредиенты'

    def get_tags(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])
    get_tags.short_description = 'Теги'

    def save_model(self, request, obj, change):
        if not obj.ingredients.exists():
            raise ValidationError(
                'Рецепт должен содержать хотя бы один ингредиент.')
        super().save_model(request, obj, change)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    empty_value_display = '---'


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    search_fields = ('name',)
    empty_value_display = '---'


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount',)
    search_fields = ('recipe__name', 'ingredient__name',)
    empty_value_display = '---'


class RecipeTagAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'tag',)
    search_fields = ('recipe__name', 'tag__name',)
    empty_value_display = '---'


class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    search_fields = ('user__username', 'recipe__name',)
    empty_value_display = '---'


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    search_fields = ('user__username', 'recipe__name',)
    empty_value_display = '---'


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(RecipeTag, RecipeTagAdmin)
admin.site.register(Favourite, FavouriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
