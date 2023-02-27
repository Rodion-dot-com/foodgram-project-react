import csv

from api.filtersets import RecipeFilter
from api.pagination import CustomPageNumberPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (CustomUserSerializer, IngredientSerializer,
                             RecipeCreateUpdateDestroySerializer,
                             RecipeReadSerializer, ShortRecipeReadSerializer,
                             TagSerializer, UserRecipesSerializer)
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from interactions_with_recipes.models import Favorites, ShoppingList
from recipes.models import Ingredient, Recipe, Tag
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Follow, User


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
    pagination_class = CustomPageNumberPagination

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, id=None):
        following_user = get_object_or_404(User, pk=id)
        is_already_subscribed = request.user.subscriptions.filter(
            following=following_user
        )
        if request.method == 'POST':
            if following_user == request.user:
                return Response(
                    {'errors': 'You can not subscribe to yourself'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if is_already_subscribed.exists():
                return Response(
                    {'errors': 'A subscription with such fields '
                               '"user" "following" already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            Follow.objects.create(user=request.user, following=following_user)
            return Response(
                UserRecipesSerializer(
                    following_user,
                    context={'request': request},
                ).data,
                status=status.HTTP_201_CREATED,
            )

        if is_already_subscribed.exists():
            is_already_subscribed.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'errors': 'A subscription with such fields '
                       '"user" "following" not exists'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        pages = self.paginate_queryset(
            User.objects.filter(subscribers__user=request.user)
        )

        return self.get_paginated_response(
            UserRecipesSerializer(
                pages,
                context={'request': request},
                many=True,
            ).data
        )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in {'list', 'retrieve'}:
            return RecipeReadSerializer
        return RecipeCreateUpdateDestroySerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        if self.action == 'update':
            raise MethodNotAllowed('PUT')
        return super().update(request, *args, **kwargs)

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

        if favorites_obj_with_current_recipe.exists():
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

        if shopping_obj_with_current_recipe.exists():
            shopping_obj_with_current_recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'errors': 'Shoppinglist with the following fields recipe '
                       'and user not exists'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename=shoppinglist.csv'
        )
        writer = csv.writer(response)
        for shopping_entry in request.user.shopping_list.values(
                'recipe__ingredients__name',
                'recipe__ingredients__measurement_unit'
        ).annotate(amount=Sum('recipe__ingredientrecipe__amount')):
            writer.writerow(shopping_entry.values())
        return response
