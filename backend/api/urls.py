from django.urls import include, path
from rest_framework import routers
from api.views import (RecipeViewSet, TagViewSet, IngredientViewSet, 
                       DownloadViewSet, LinkViewSet)

router = routers.DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('recipes/download_shopping_cart', DownloadViewSet, basename='download')
router.register(r'recipes/(?P<recipe_id>\d+)/get_link', LinkViewSet, basename='get_link')


urlpatterns = [
    path('', include(router.urls)),
]