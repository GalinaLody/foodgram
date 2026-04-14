from django.urls import path

from .views import redirect_to_recipe_url

app_name = 'recipes'

urlpatterns = [
    path('<int:recipe_id>/', redirect_to_recipe_url, name='redirect')
]
