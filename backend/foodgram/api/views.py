from djoser.views import UserViewSet
from rest_framework import filters, viewsets

from api.serializers import (CustomUserSerializer, IngredientSerializer,
                             RecipeReadSerializer,
                             RecipeCreateUpdateDestroySerializer,
                             TagSerializer)
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
