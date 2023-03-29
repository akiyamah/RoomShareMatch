from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('main_app/', include('main_app.urls')),  
    path('matching_app/', include('matching_app.urls')), 
    # path('app_name/', include('app_name.urls')),  フォーマット
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
