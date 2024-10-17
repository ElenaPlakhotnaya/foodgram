from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.permissions import AuthorOrReadOnly
from api.serializers import (FavouriteAndShoppingCrtSerializer,
                             IngredientSerializer, RecipeSerializer,
                             TagSerializer)
from recipes.models import Favourite, Ingredient, Recipe, ShoppingCart, Tag


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = [AuthorOrReadOnly, IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True, methods=['post', 'delete'],
        url_path='favorite',
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            if Favourite.objects.filter(
                user=request.user, recipe=recipe
            ).exists():
                return Response(
                    {'errors': 'Рецепт уже был добавлен в избранное.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favourite.objects.create(user=request.user, recipe=recipe)
            serializer = FavouriteAndShoppingCrtSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            favourite = Favourite.objects.filter(
                user=request.user, recipe=recipe)
            if favourite.exists():
                favourite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Рецепт уже был удален из избранного.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=True, methods=['post', 'delete'],
        url_path='shopping_cart',
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            if ShoppingCart.objects.filter(
                user=request.user, recipe=recipe
            ).exists():
                return Response(
                    {'errors': 'Рецепт уже был добавлен в корзину.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            serializer = FavouriteAndShoppingCrtSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            shopping_cart_item = ShoppingCart.objects.filter(
                user=request.user, recipe=recipe)
            if shopping_cart_item.exists():
                shopping_cart_item.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Рецепт уже был удалён из корзины.'},
                status=status.HTTP_400_BAD_REQUEST
            )

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

        shopping_list_text = "Список покупок:\n\n"
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

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('name',)
    search_fields = ('name',)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
