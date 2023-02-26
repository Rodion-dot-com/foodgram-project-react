from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag, TagRecipe
from users.models import User


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        current_user = self.context['request'].user
        return (not current_user.is_anonymous
                and current_user.subscriptions.filter(following=obj).exists())


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name', 'last_name', 'password'
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id', queryset=Ingredient.objects.all()
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True, source='ingredientrecipe_set', read_only=True,
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time',
            'is_favorited', 'is_in_shopping_cart',
        )

    def get_is_favorited(self, obj):
        current_user = self.context['request'].user
        return (not current_user.is_anonymous
                and current_user.favorite_list.filter(recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        current_user = self.context['request'].user
        return (not current_user.is_anonymous
                and current_user.shopping_list.filter(recipe=obj).exists())


class RecipeCreateUpdateDestroySerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = IngredientRecipeSerializer(
        many=True, source='ingredientrecipe_set',
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time'
        )

    @staticmethod
    def create_ingredient_recipe_objs(ingredientrecipe_set, recipe):
        IngredientRecipe.objects.bulk_create(
            IngredientRecipe(
                ingredient=Ingredient.objects.get(
                    pk=ingredient_recipe['ingredient']['id'].id,
                ),
                recipe=recipe,
                amount=ingredient_recipe['amount'],
            ) for ingredient_recipe in ingredientrecipe_set
        )

    @staticmethod
    def create_tag_recipe_objs(tags, recipe):
        TagRecipe.objects.bulk_create(
            TagRecipe(
                tag=Tag.objects.get(pk=tag.id),
                recipe=recipe,
            ) for tag in tags
        )

    def create(self, validated_data):
        ingredientrecipe_set = validated_data.pop('ingredientrecipe_set')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        self.create_ingredient_recipe_objs(
            ingredientrecipe_set,
            recipe,
        )
        self.create_tag_recipe_objs(tags, recipe)

        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )

        if 'ingredients' in self.initial_data:
            instance.ingredientrecipe_set.all().delete()
            ingredientrecipe_set = validated_data.pop('ingredientrecipe_set')
            self.create_ingredient_recipe_objs(ingredientrecipe_set, instance)

        if 'tags' in self.initial_data:
            instance.tagrecipe_set.all().delete()
            tags = validated_data.pop('tags')
            self.create_tag_recipe_objs(tags, instance)

        instance.save()
        return instance

    def validate_ingredients(self, ingredientrecipe_set):
        unique_ingredients = set()
        for ingredientrecipe in ingredientrecipe_set:
            current_id = ingredientrecipe['ingredient']['id'].id
            if current_id in unique_ingredients:
                raise ValidationError(
                    f'Ингредиент с id {current_id} уже добавлен',
                )
            unique_ingredients.add(current_id)
        return ingredientrecipe_set

    def validate_tags(self, tags):
        unique_tags = set()
        for tag in tags:
            if tag.id in unique_tags:
                raise ValidationError(
                    f'Ингредиент с id {tag.id} уже добавлен',
                )
            unique_tags.add(tag.id)
        return tags


class ShortRecipeReadSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class UserRecipesSerializer(CustomUserSerializer):
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed',
            'recipes_count', 'recipes',
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        query_params = self.context['request'].query_params
        if 'recipes_limit' in query_params:
            recipes = recipes[:int(query_params['recipes_limit'])]
        return ShortRecipeReadSerializer(instance=recipes, many=True).data
