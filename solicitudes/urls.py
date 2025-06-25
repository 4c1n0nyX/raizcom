from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from index import views

urlpatterns = [
    path('', views.inicio, name="index"),
    path('login/', views.loginf, name="login"),
    path('j4ck3r4dm1n/', admin.site.urls),
    path('inicio/', views.inicio, name='inicio'),
    path('logout/', views.logoutUser, name='logout'),
    path('403', views.loginf403, name='403'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)