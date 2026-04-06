from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from api.recipes.views import redirect_to_recipe_url

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('s/<str:short_link>', redirect_to_recipe_url, name='redierct')
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
