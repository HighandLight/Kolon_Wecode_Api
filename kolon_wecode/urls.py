from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('dealers', include('dealers.urls')),
    path('cars', include('cars.urls')),
    path('estimates', include('estimates.urls')),
    path('notifications', include('notifications.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)