from django.core.validators import MinValueValidator
from django.db import models

from recipes.validators import color_hex_validator
from users.models import User

DEFAULT_FIELD_MAX_LENGTH = 200
MAX_COLOR_FIELD_LENGTH = 7


class Tag(models.Model):
    name = models.CharField(
        max_length=DEFAULT_FIELD_MAX_LENGTH,
        unique=True,
        verbose_name='название',
    )
    slug = models.SlugField(
        max_length=DEFAULT_FIELD_MAX_LENGTH,
        unique=True,
        verbose_name='уникальный адрес группы',
    )
    color = models.CharField(
        max_length=MAX_COLOR_FIELD_LENGTH,
        unique=True,
        validators=(color_hex_validator,),
        verbose_name='цветовой HEX-код',
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=DEFAULT_FIELD_MAX_LENGTH,
        db_index=True,
        verbose_name='название',
    )
    measurement_unit = models.CharField(
        max_length=DEFAULT_FIELD_MAX_LENGTH,
        verbose_name='единицы измерения',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='name_measurement_unit_unique',
            ),
        )
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='автор публикации',
    )
    name = models.CharField(
        max_length=DEFAULT_FIELD_MAX_LENGTH,
        verbose_name='название',
    )
    text = models.TextField(
        verbose_name='текстовое описание',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(1),),
        verbose_name='время приготовления в минутах',
    )
    image = models.ImageField(
        upload_to='recipes/',
        null=True,
        verbose_name='картинка',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата публикации',
        db_index=True
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт',
    )
    quantity = models.FloatField(
        validators=(MinValueValidator(0),),
        verbose_name='количество',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='ingredient_recipe_unique',
            ),
        )
        verbose_name = 'входящий ингредиент'
        verbose_name_plural = 'входящие ингредиенты'

    def __str__(self):
        return (
            f'{self.ingredient.name} - {self.quantity} '
            f'{self.ingredient.measurement_unit}'
        )


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='тег',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('tag', 'recipe'),
                name='tag_recipe_unique',
            ),
        )
        verbose_name = 'указанный тег'
        verbose_name_plural = 'указанные теги'

    def __str__(self):
        return f'{self.recipe}- {self.tag}'
