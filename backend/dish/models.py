from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from colorfield.fields import ColorField


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=200,
        unique=True,
        blank=False
    )
    color = ColorField(
        'Цвет',
        format='hex',
        unique=True,
        blank=False
    )
    slug = models.SlugField(
        'Идентификатор',
        max_length=200,
        unique=True,
        blank=False
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=200,
        blank=False
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200,
        blank=False
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
    )
    name = models.CharField(
        'Название',
        max_length=200,
        blank=False
    )
    image = models.ImageField(
        'Картинка',
        blank=False
    )
    text = models.TextField(
        'Текстовое описание',
        blank=False
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        through='RecipeTag'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=(MinValueValidator(1),),
        blank=False
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент')
    amount = models.IntegerField(
        'Количество',
        validators=(MinValueValidator(1),),
        blank=False
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        default_related_name = 'recipeingredients'


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, verbose_name='Тэг')

    class Meta:
        verbose_name = 'Тэг рецепта'
        verbose_name_plural = 'Тэги рецепта'
        default_related_name = 'recipetags'


# class FavoriteAndShopingCartBaseModel(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
#     recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')

    class Meta():
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        default_related_name = 'favorites'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_recipe'
            )
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')

    class Meta():
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shoppingcart'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_cart'
            )
        ]
