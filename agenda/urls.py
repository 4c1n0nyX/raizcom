from django.urls import path
from agenda import views

# =============== URL's de Agenda del Contactos ================ #
urlpatterns = [
    path('', views.contactos, name='contactos'),
    path('aceptar-solicitud/<int:request_id>/', views.accept_contact_request, name='accept_contact_request'),
    path('rechazar-solicitud/<int:request_id>/', views.reject_contact_request, name='reject_contact_request'),
    path('cancelar-solicitud/<int:request_id>/', views.cancel_contact_request, name='cancel_contact_request'),
    path('delete/<int:id>', views.delete_contacto, name="delete_contacto"),
]
