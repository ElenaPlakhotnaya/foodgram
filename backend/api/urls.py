from django.urls import include, path
from rest_framework import routers
from api.views import (RecipeViewSet, TagViewSet, IngredientViewSet, 
                       DownloadViewSet, LinkViewSet, CartViewSet,
                       FavouriteViewSet)

router = routers.DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('recipes/download_shopping_cart', DownloadViewSet, basename='download')
router.register(r'recipes/(?P<recipe_id>\d+)/get_link', LinkViewSet, basename='get_link')
router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart', CartViewSet, basename='shopping_cart')
router.register(r'recipes/(?P<recipe_id>\d+)/favourite', FavouriteViewSet, basename='favourite')


urlpatterns = [
    path('', include(router.urls)),
]