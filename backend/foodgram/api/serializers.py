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

        instance.tagrecipe_set.all().delete()
        instance.ingredientrecipe_set.all().delete()
        instance.save()

        ingredientrecipe_set = validated_data.pop('ingredientrecipe_set')
        tags = validated_data.pop('tags')
        self.create_ingredient_recipe_objs(ingredientrecipe_set, instance)
        self.create_tag_recipe_objs(tags, instance)

        return instance


class ShortRecipeReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time')
        read_only_fields = ('id', 'name', 'cooking_time')
