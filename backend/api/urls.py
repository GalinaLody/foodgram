from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .ingredients.views import IngredientViewSet
from .recipes.views import (
    RecipeViewSet,
    TagViewSet,
)
from .users.views import FoodgramUserViewSet

app_name = 'api'

router = DefaultRouter()
router.register(r'users', FoodgramUserViewSet, basename='users')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
