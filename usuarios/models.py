from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin

# =============== Módelo de Usuarios ================ #
class Usuarios(AbstractUser, PermissionsMixin):
    username = models.CharField(max_length=200, verbose_name='Cédula', default='', unique=True)
    comunidad = models.CharField(max_length=200, verbose_name='Comunidad', default='')
    password = models.CharField(max_length=200, verbose_name='Contraseña', default='')
    telefono = models.CharField(max_length=200, verbose_name='Teléfono', default='')
    foto = models.FileField(upload_to='fotos/', verbose_name='Imagen', blank=True, null=True)
    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'username'

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def is_member(self, group_name):
        return self.groups.filter(name=group_name).exists()
    
    def __str__(self):
        return self.username

# =============== Módelo de Comunidad ================ #
class Comunidad(models.Model):
    comunidad = models.CharField(max_length=200, verbose_name='comunidad', default='', unique=True)