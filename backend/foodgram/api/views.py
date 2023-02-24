import csv

from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from api.serializers import (CustomUserSerializer, ShortRecipeReadSerializer,
                             IngredientSerializer,
                             RecipeReadSerializer,
                             RecipeCreateUpdateDestroySerializer,
                             TagSerializer)
from interactions_with_recipes.models import Favorites, ShoppingList
from recipes.models import Ingredient, Recipe, Tag
from users.models import User


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action in {'list', 'retrieve'}:
            return RecipeReadSerializer
        return RecipeCreateUpdateDestroySerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        favorites_obj_with_current_recipe = request.user.favorite_list.filter(
            recipe=recipe
        )
        if request.method == 'POST':
            if favorites_obj_with_current_recipe.exists():
                return Response(
                    {'errors': 'Favorites with the following fields recipe '
                               'and user already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            Favorites.objects.create(
                user=request.user,
                recipe=recipe
            )
            return Response(
                ShortRecipeReadSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )

        elif favorites_obj_with_current_recipe.exists():
            favorites_obj_with_current_recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'errors': 'Favorites with the following fields recipe '
                       'and user not exists'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        shopping_obj_with_current_recipe = request.user.shopping_list.filter(
            recipe=recipe
        )
        if request.method == 'POST':
            if shopping_obj_with_current_recipe.exists():
                return Response(
                    {'errors': 'Shoppinglist with the following fields recipe '
                               'and user already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            ShoppingList.objects.create(
                user=request.user,
                recipe=recipe
            )
            return Response(
                ShortRecipeReadSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )

        elif shopping_obj_with_current_recipe.exists():
            shopping_obj_with_current_recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'errors': 'Shoppinglist with the following fields recipe '
                       'and user not exists'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False)
    def download_shopping_cart(self, request):
        response = Response(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; '
                                            'filename="somefilename.csv"'},
        )
        writer = csv.writer(response)
        pass
