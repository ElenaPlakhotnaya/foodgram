from django.contrib.auth import get_user_model

from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipe, Tag

User = get_user_model()


class RecipeFilter(FilterSet):

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value:
                return queryset.filter(favorites__user=user)
            else:
                return queryset.exclude(favorites__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value:
                return queryset.filter(shopping_carts__user=user)
            else:
                return queryset.exclude(shopping_carts__user=user)
        return queryset
