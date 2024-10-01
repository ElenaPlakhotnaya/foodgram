from rest_framework import filters, mixins, viewsets
from rest_framework.response import Response
from api.serializers import RecipeSerializer, TagSerializer, IngredientSerializer
from recipes.models import Recipe, Tag, Ingredient
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('author', 'tags',) 

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
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class DownloadViewSet(viewsets.ModelViewSet):
    pass

class LinkViewSet(viewsets.ModelViewSet):
    pass

class CartViewSet(viewsets.ModelViewSet):
    pass

class FavouriteViewSet(viewsets.ModelViewSet):
    pass