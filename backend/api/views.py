from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import AuthorOrReadOnly
from api.serializers import (FavouriteAndShoppingCrtSerializer,
                             FavouriteSerializer, IngredientSerializer,
                             RecipeReadSerializer, RecipeSerializer,
                             ShoppingCartSerializer, TagSerializer)
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.views import CustomPagination


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = [AuthorOrReadOnly, IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], url_path='favorite',
            permission_classes=[permissions.IsAuthenticated])
    def favorite_post(self, request, pk):
        return self.add_item_to_list(request.user, pk, 'favorite')

    @favorite_post.mapping.delete
    def favorite_delete(self, request, pk):
        return self.remove_item_from_list(request.user, pk, 'favorite')

    @action(detail=True, methods=['post'], url_path='shopping_cart',
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart_post(self, request, pk):
        return self.add_item_to_list(request.user, pk, 'shopping_cart')

    @shopping_cart_post.mapping.delete
    def shopping_cart_delete(self, request, pk):
        return self.remove_item_from_list(request.user, pk, 'shopping_cart')

    def add_item_to_list(self, user, pk, list_type):
        try:
            if list_type == 'favorite':
                serializer = FavouriteSerializer(
                    data={}, context={'request': self.request, 'id': pk})
                serializer.is_valid(raise_exception=True)
                favourite_item = serializer.create(serializer.validated_data)
                item_data = FavouriteAndShoppingCrtSerializer(
                    favourite_item).data
            elif list_type == 'shopping_cart':
                serializer = ShoppingCartSerializer(
                    data={}, context={'request': self.request, 'id': pk})
                serializer.is_valid(raise_exception=True)
                shopping_cart_item = serializer.create(
                    serializer.validated_data)
                item_data = FavouriteAndShoppingCrtSerializer(
                    shopping_cart_item).data
            return Response(item_data, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            return Response(
                {'errors': str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    def remove_item_from_list(self, user, pk, list_type):
        try:
            if list_type == 'favorite':
                serializer = FavouriteSerializer(
                    context={'request': self.request, 'id': pk})
                serializer.delete(user)
            elif list_type == 'shopping_cart':
                serializer = ShoppingCartSerializer(
                    context={'request': self.request, 'id': pk})
                serializer.delete(user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except serializers.ValidationError as e:
            return Response(
                {'errors': str(e)}, status=status.HTTP_400_BAD_REQUEST
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
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__shopping_carts__user=request.user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
        )

        if not ingredients.exists():
            return Response(
                {'errors': 'Корзина пуста.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        shopping_list_text = 'Список покупок:\n\n'
        for item in ingredients:
            shopping_list_text += (
                f'{item["ingredient__name"]}, '
                f'({item["ingredient__measurement_unit"]}) — '
                f'{item["total_amount"]}\n'
            )

        response = HttpResponse(shopping_list_text, content_type='text/plain')
        response[
            'Content-Disposition'] = 'attachment; filename="shopping_cart.txt"'

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


class RecipeRedirectView(APIView):
    def get(self, request, pk, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=pk)
        full_link = recipe.full_link
        return redirect(full_link)
