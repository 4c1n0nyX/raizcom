from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from usuarios import views

urlpatterns = [
    # =============== URL's del Módulo de Usuarios ================ #
    path('', views.usuarios, name='usuarios'),
    path('update/<int:id>', views.update_usuarios, name='update_usuarios'),
    path('updatep/<int:id>', views.updatep_usuarios, name='updatep_usuarios'),
    path('updatei/<int:id>', views.updatei_usuarios, name='updatei_usuarios'),
    path('delete/<int:id>', views.delete_usuarios, name="delete_usuarios"),
    path('<str:accion>', views.consultar_usuarios, name='consultar_usuarios'),
    # =============== URL's del Módulo de Comunidades ================ #
    path('comunidad/', views.comunidades, name='comunidades'),
    path('comunidad/update/<int:id>', views.update_comunidades, name='update_comunidades'),
    path('comunidad/delete/<int:id>', views.delete_comunidades, name="delete_comunidades"),
]