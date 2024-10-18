from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User
from recipes.constants import (TAG_LENGTH, INGR_NAME_LENGTH, 
                               INGR_UNIT_LENGTH, RECIPE_NAME_LENGTH, 
                               SHORT_LINK_LENGTH, MIN, MAX)
from django.db.models import UniqueConstraint

class Tag(models.Model):
    name = models.CharField('Название', max_length=TAG_LENGTH, unique=True)
    slug = models.SlugField(
        'Уникальный слаг', max_length=TAG_LENGTH, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=INGR_NAME_LENGTH)
    measurement_unit = models.CharField('Единица измерения', max_length=INGR_UNIT_LENGTH)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            UniqueConstraint(fields=['name', 'measurement_unit'], name='unique_name_measurement')
        ]



class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество в рецепте',
    )
    class Meta:
        verbose_name = 'Рецепт-ингредиент'
        verbose_name_plural = 'Рецепты-ингредиенты'


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name='recipe_tags'
    )
    tag = models.ForeignKey(
        Tag,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name='recipe_tags'
    )
    class Meta:
        
        verbose_name = 'Рецепт-тег'
        verbose_name_plural = 'Рецепты-теги'
        constraints = [
            UniqueConstraint(fields=['recipe', 'tag'], name='unique_recipe_tag')
        ]


class Recipe(models.Model):
    name = models.CharField('Название', max_length=RECIPE_NAME_LENGTH)
    image = models.ImageField(
        'Изображениe',
        upload_to='recipes/images/',
        null=True,
        default=None
    )
    text = models.TextField('Описание')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through=RecipeIngredient,
        blank=False,
        verbose_name='Список ингридиентов',
        related_name='recipes',
        validators=[
            MinValueValidator(MIN),
            MaxValueValidator(MAX)
        ]
    )
    tags = models.ManyToManyField(
        Tag,
        through=RecipeTag,
        blank=False,
        verbose_name='Список тэгов',
        related_name='recipes',
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(MIN),
            MaxValueValidator(MAX)
        ]
    )
    short_link = models.URLField(
        max_length=SHORT_LINK_LENGTH, unique=True, blank=True, null=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.short_link:
            self.short_link = str(self.pk)
            self.save(update_fields=['short_link'])

    def __str__(self):
        return self.name


class Favourite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='favorites',
    )
    
    class Meta:
        
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            UniqueConstraint(fields=['user', 'recipe'], name='unique_fav_user_recipe')
        ]

class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_carts',
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shopping_carts',
    )

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'
        constraints = [
            UniqueConstraint(fields=['user', 'recipe'], name='unique_shop_user_recipe')
        ]
