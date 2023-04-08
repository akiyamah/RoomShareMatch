from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main_app.urls')),
    path('matching_app/', include('matching_app.urls')), 
    path('messages/', include('messages_app.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

