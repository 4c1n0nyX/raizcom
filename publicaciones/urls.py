from django.urls import path
from publicaciones import views

urlpatterns = [
    # =============== URL's del Módulo de Noticias ================ #
    path('noticias/', views.noticias, name='noticias'),
    path('noticias/update/<int:id>', views.update_noticias, name='update_noticias'),
    path('noticias/updatei/<int:id>', views.updatei_noticias, name='updatei_noticias'),
    path('noticias/delete/<int:id>', views.delete_noticias, name="delete_noticias"),
    path('noticias/<str:accion>', views.consultar_noticias, name='consultar_noticias'),
    # =============== URL's del Módulo de Recursos ================ #
    path('recursos/', views.recursos, name='recursos'),
    path('recursos/update/<int:id>', views.update_recursos, name='update_recursos'),
    path('recursos/delete/<int:id>', views.delete_recursos, name="delete_recursos"),
    path('recursos/finalizar/<int:id>', views.finalizar_recursos, name="finalizar_recursos"),
    path('recursos/print/', views.print_recursos, name="print_recursos"),
    # =============== URL's del Módulo de Recursos ================ #
    path('pservicios/', views.servicios, name='recursos'),
    path('pservicios/update/<int:id>', views.update_servicios, name='update_servicios'),
    path('pservicios/delete/<int:id>', views.delete_servicios, name="delete_servicios"),
]
