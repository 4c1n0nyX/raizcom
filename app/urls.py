from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', include('index.urls')),
    path('contactos/', include('agenda.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('servicios/', include('servicios.urls')),
    path('publicaciones/', include('publicaciones.urls')),
    path('chat/', include('chat.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
