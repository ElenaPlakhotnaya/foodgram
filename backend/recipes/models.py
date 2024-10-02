from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField('Название', max_length=32, unique=True)
    slug = models.SlugField(
        'Уникальный слаг', max_length=32, unique=True)
    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
    
    def __str__(self):
        return self.name

    

class Ingredient(models.Model):
    name = models.CharField('Название', max_length=128)
    measurement_unit = models.CharField('Единица измерения', max_length=64)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
    
    def __str__(self):
        return self.name
    

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    amount = models.IntegerField('Количество в рецепте',)
    
    def __str__(self):
        return f'{self.ingredient} {self.amount}'
    
class RecipeTag(models.Model):
    recipe_id = models.ForeignKey(
        'Recipe',
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    tag_id = models.ForeignKey(
        Tag,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )

class Recipe(models.Model):    
    name = models.CharField('Название', max_length=256)
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
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through=RecipeIngredient,
        blank=False,
        verbose_name='Список ингридиентов',
    )
    tags = models.ManyToManyField(
        Tag,
        through=RecipeTag,
        blank=False,
        verbose_name='Список тэгов',
    )
    cooking_time = models.IntegerField('Время приготовления',)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name
