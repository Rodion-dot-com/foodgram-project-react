from django.db import models
from django.core.validators import MinValueValidator
from users.models import User


class Tag(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, null=True)

    def __str__(self):
        return f'{self.name} - {self.slug}'


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    unit_of_measurement = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.name} {self.unit_of_measurement}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField(
        max_length=200,
        blank=False,
        null=False
    )
    text = models.TextField(
        blank=False,
        null=False,
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(1),)
    )
    image = models.ImageField(
        upload_to='recipes/'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe'
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe'
    )

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    count = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(1),)
    )

    def __str__(self):
        return (
            f'В рецепте {self.recipe.name}: {self.ingredient.name} - '
            f'{self.count} {self.ingredient.unit_of_measurement}'
        )


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.recipe.name} [{self.tag.name}]'
