from api.ingredients.views import IngredientViewSet
from api.recipes.views import RecipeViewSet, TagtViewSet
from api.users.views import MyUserViewSet
from django.urls import include, path
from rest_framework.routers import DefaultRouter

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
