from django.contrib import admin

from .models import Ingredient, IngredientRecipe, Recipe, Tag, TagRecipe


class IngredientInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1


class TagInline(admin.TabularInline):
    model = TagRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ('name', 'author', 'tags')
    inlines = (IngredientInline, TagInline,)
    readonly_fields = ('number_of_liked_users',)

    def number_of_liked_users(self, obj):
        return obj.liked_users.count()

    number_of_liked_users.short_description = (
        'число добавлений этого рецепта в избранное'
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
