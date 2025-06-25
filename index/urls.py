from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from index import views

# =============== URL's Iniciales ================ #
urlpatterns = [
    path('', views.inicio, name="inicio"),
    path('login/', views.loginf, name="login"),
    path('usuario/', views.user, name="user"),
    path('usuario/update/<int:id>', views.user_u, name="user_u"),
    path('usuario/updatep/<int:id>', views.user_up, name="user_up"),
    path('usuario/updatei/<int:id>', views.user_ui, name="user_ui"),
    path('j4ck3r4dm1n/', admin.site.urls),
    path('logout/', views.logoutUser, name='logout'),
    path('403', views.loginf403, name='403'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)