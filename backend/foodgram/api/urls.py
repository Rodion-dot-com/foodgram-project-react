from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (CustomUserViewSet, IngredientViewSet, RecipeViewSet,
                       TagViewSet)

router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', CustomUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
