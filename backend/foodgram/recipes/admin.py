from django.contrib import admin

from .models import (Recipe, Ingredient, Tag, IngredientRecipe, TagRecipe,
                     Favorites)


class IngredientInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1


class TagInline(admin.TabularInline):
    model = TagRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author',)
    list_filter = ('name', 'author', 'tags')
    inlines = (IngredientInline, TagInline,)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit_of_measurement',)
    list_filter = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    list_filter = ('user', 'recipe',)
