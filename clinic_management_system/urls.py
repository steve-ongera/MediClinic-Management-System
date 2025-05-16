from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include  # include if you have other apps

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapplication.urls')),  # Replace 'myapplication' with your app name
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
