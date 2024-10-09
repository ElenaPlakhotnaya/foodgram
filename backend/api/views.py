from rest_framework import filters, mixins, viewsets
from rest_framework.response import Response
from api.serializers import (RecipeSerializer, TagSerializer, 
                             IngredientSerializer, FavouriteSerializer,
                             ShoppingCartSerializer, RecipeSafeMethodsSerializer)
from recipes.models import Recipe, Tag, Ingredient, Favourite, ShoppingCart
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Exists, OuterRef, Case, When, IntegerField
from django.shortcuts import get_object_or_404
from api.permissions import AuthorOrReadOnly
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('author', 'tags',) 
    permission_classes = [AuthorOrReadOnly, IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    """
    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSafeMethodsSerializer
        return RecipeSerializer
    """

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

class DownloadViewSet(viewsets.ModelViewSet):
    pass

class LinkViewSet(viewsets.ModelViewSet):
    pass

class CartViewSet(viewsets.ModelViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer

class FavouriteViewSet(viewsets.ModelViewSet):
    queryset = Favourite.objects.all()
    serializer_class = FavouriteSerializer