from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.users.views import MyUserViewSet
from api.ingredients.views import IngredientViewSet
from api.recipes.views import TagtViewSet, RecipeViewSet

app_name = 'api'

router = DefaultRouter()
router.register(r'users', MyUserViewSet, basename='users')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagtViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
