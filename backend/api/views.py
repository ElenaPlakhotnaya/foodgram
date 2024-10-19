from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import AuthorOrReadOnly
from api.serializers import (FavouriteAndShoppingCrtSerializer,
                             IngredientSerializer, RecipeReadSerializer,
                             RecipeSerializer, TagSerializer)
from recipes.models import Favourite, Ingredient, Recipe, ShoppingCart, Tag


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    # serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = [AuthorOrReadOnly, IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def add_in_bd(self, model, user, pk):
        if model.objects.filter(user=user, recipe_id=pk).exists():
            return Response(
                {'errors': 'Рецепт уже был добавлен.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = FavouriteAndShoppingCrtSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from_bd(self, model, user, pk):
        if not Recipe.objects.filter(id=pk).exists():
            return Response(
                {'errors': 'Рецепт не существует.'},
                status=status.HTTP_404_NOT_FOUND
            )
        obj = model.objects.filter(user=user, recipe__id=pk)

        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Рецепт уже был удален.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True, methods=['post'],
        url_path='favorite',
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite_post(self, request, pk):

        return self.add_in_bd(Favourite, request.user, pk)

    @favorite_post.mapping.delete
    def favorite_delete(self, request, pk):

        return self.delete_from_bd(Favourite, request.user, pk)

    @action(
        detail=True, methods=['post'],
        url_path='shopping_cart',
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart_post(self, request, pk):

        return self.add_in_bd(ShoppingCart, request.user, pk)

    @shopping_cart_post.mapping.delete
    def shopping_cart_delete(self, request, pk):
        return self.delete_from_bd(ShoppingCart, request.user, pk)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, *args, **kwargs):
        recipe = self.get_object()
        short_link = recipe.short_link
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)

    @action(
        detail=False, methods=['get'],
        url_path='download_shopping_cart',
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):

        shopping_cart_items = ShoppingCart.objects.filter(user=request.user)
        recipes = [item.recipe for item in shopping_cart_items]

        if not recipes:
            return Response(
                {'errors': 'Корзина пуста.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ingredients = {}

        for recipe in recipes:
            for recipe_ingredient in recipe.recipe_ingredients.all():
                name = recipe_ingredient.ingredient.name
                measurement_unit = (
                    recipe_ingredient.ingredient.measurement_unit
                )
                amount = recipe_ingredient.amount

                key = f"{name} ({measurement_unit})"

                if key in ingredients:
                    ingredients[key] += amount
                else:
                    ingredients[key] = amount

        shopping_list_text = 'Список покупок:\n\n'
        for item, total_amount in ingredients.items():
            shopping_list_text += f"{item} — {total_amount}\n"

        response = HttpResponse(shopping_list_text, content_type='text/plain')
        response[
            'Content-Disposition'
        ] = 'attachment; filename="shopping_cart.txt"'

        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None
