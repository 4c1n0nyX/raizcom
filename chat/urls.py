from django.urls import path
from . import views

# =============== URL's de Chat ================ #
urlpatterns = [
    path('', views.chat_general, name='chat_general'),
    path('<int:user_id>/', views.chat_view, name='start_chat'),
    path('grecursos/', views.recursos_view, name='recursos_view'),
    path('grecursos/reportar/<int:id>', views.recursos_report, name='recursos_report'),
    path('alertas/', views.alertas, name='alertas'),
]