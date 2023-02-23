from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, Tag, IngredientRecipe, TagRecipe
from users.models import User


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed',
        )

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError('Недоступное имя пользователя')
        return value

    def get_is_subscribed(self, obj):
        current_user = self.context['request'].user
        return (not current_user.is_anonymous
                and current_user.subscriptions.filter(following=obj).exists())


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

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        )


class RecipeCreateUpdateDestroySerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = IngredientRecipeSerializer(
        many=True, source='ingredientrecipe_set',
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time'
        )

    def create(self, validated_data):
        ingredientrecipe_set = validated_data.pop('ingredientrecipe_set')
        tags = validated_data.pop('tags')
        recipe = Recipe(
            author=self.context.get('request').user,
            **validated_data
        )

        ingredient_recipe_objs = (
            IngredientRecipe(
                ingredient=Ingredient.objects.get(
                    pk=ingredient_recipe['ingredient']['id'].id,
                ),
                recipe=recipe,
                amount=ingredient_recipe['amount'],
            ) for ingredient_recipe in ingredientrecipe_set
        )
        tag_recipe_objs = (
            TagRecipe(
                tag=Tag.objects.get(pk=tag.id),
                recipe=recipe,
            ) for tag in tags
        )

        recipe.save()
        IngredientRecipe.objects.bulk_create(
            ingredient_recipe_objs
        )
        TagRecipe.objects.bulk_create(
            tag_recipe_objs
        )
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )

        instance.tagrecipe_set.all().delete()
        instance.ingredientrecipe_set.all().delete()

        ingredientrecipe_set = validated_data.pop('ingredientrecipe_set')
        tags = validated_data.pop('tags')

        ingredient_recipe_objs = (
            IngredientRecipe(
                ingredient=Ingredient.objects.get(
                    pk=ingredient_recipe['ingredient']['id'].id,
                ),
                recipe=instance,
                amount=ingredient_recipe['amount'],
            ) for ingredient_recipe in ingredientrecipe_set
        )
        tag_recipe_objs = (
            TagRecipe(
                tag=Tag.objects.get(pk=tag.id),
                recipe=instance,
            ) for tag in tags
        )

        instance.save()
        IngredientRecipe.objects.bulk_create(ingredient_recipe_objs)
        TagRecipe.objects.bulk_create(tag_recipe_objs)

        return instance
