from django.urls import path
from servicios import views

urlpatterns = [
    path('', views.mapa_servicios, name="mapa_servicios"),
    path('api/', views.api_servicios, name="api_servicios"),
]
