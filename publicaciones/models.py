from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
import datetime

# =============== Módelo de Publicación de Noticias  ================ #
class Noticias(models.Model):
    titulo = models.CharField(max_length=200, verbose_name='Titulo', default='', unique=True)
    contenido = models.CharField(max_length=5000, verbose_name='Descripción', default='', blank=True)
    imagen = models.FileField(upload_to='fotos/', verbose_name='Imagen', default='', blank=True, null=True)
    fecha_publicacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Publicación')

    class Meta:
        verbose_name = "Publicación"
        verbose_name_plural = "Publicaciones"
        ordering = ['-fecha_publicacion']

    def __str__(self):
        return self.titulo

# =============== Módelo de Publicación de Recursos  ================ #
class Recursos(models.Model):
    tipo_recurso = models.CharField(max_length=200, verbose_name='Recurso', default='')
    fecha = models.DateTimeField(verbose_name='Fecha Pago', default=datetime.date.today)
    lugar = models.CharField(max_length=200, verbose_name='Lugar', default='')
    pago = models.BooleanField(default=False, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estatus = models.CharField(max_length=200, verbose_name='Estatus', default='ACTIVO')

# =============== Módelo de Pago de Recursos  ================ #
class Recursos_Pagos(models.Model):
    recurso = models.ForeignKey(Recursos, on_delete=models.CASCADE, related_name='recursos')
    usuario = models.CharField(max_length=200, verbose_name='Usuario', default='', blank=True, null=True)
    cedula = models.CharField(max_length=50, verbose_name='Cédula', default='', blank=True, null=True)
    fechap = models.DateTimeField(verbose_name='Fecha Pago', default=datetime.date.today)
    comunidad = models.CharField(max_length=200, verbose_name='Comunidad', default='', blank=True, null=True)
    comprobante = models.FileField(upload_to='comprobantes/', verbose_name='Comprobante de Pago', default='')

# =============== Módelo de Publicación de Servicios  ================ #
class Servicios(models.Model):
    nombre = models.CharField(max_length=200, verbose_name='Nombre', default='')
    servicio = models.CharField(max_length=200, verbose_name='Servicio', default='')
    latitud = models.CharField(max_length=200, verbose_name='Latitud', default='')
    longitud = models.CharField(max_length=5000, verbose_name='Longitud', default='')
    