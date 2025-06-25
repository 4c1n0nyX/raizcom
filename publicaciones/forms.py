from django import forms
from .models import Noticias, Recursos, Servicios

#################### FORMULARIOS DE NOTICIAS #####################

# =============== Formulario de Crear Noticias ================ #
class NoticiasForm(forms.ModelForm):
    class Meta:
        model = Noticias
        fields = ('titulo', 'contenido', 'imagen')

# =============== Formulario de Actualizar Noticias ================ #
class NoticiasAForm(forms.ModelForm):
    class Meta:
        model = Noticias
        fields = ('titulo', 'contenido',)

# =============== Formulario de Actualizar Imagen de Noticias ================ #
class NoticiasAIForm(forms.ModelForm):
    class Meta:
        model = Noticias
        fields = ('imagen',)

#################### FORMULARIOS DE RECURSOS #####################

# =============== Formulario de Crear Recurso ================ #
class RecursosForm(forms.ModelForm):
    class Meta:
        model = Recursos
        fields = ('tipo_recurso', 'fecha', 'lugar', 'precio',)

# =============== Formulario de Actualizar Recurso ================ #
class RecursosAForm(forms.ModelForm):
    class Meta:
        model = Recursos
        fields = ('fecha', 'lugar', 'precio',)

#################### FORMULARIOS DE SERVICIOS #####################

# =============== Formulario de Crear Recurso ================ #
class ServiciosForm(forms.ModelForm):
    class Meta:
        model = Servicios
        fields = ('nombre', 'servicio', 'latitud', 'longitud',)

# =============== Formulario de Actualizar Recurso ================ #
class ServiciosAForm(forms.ModelForm):
    class Meta:
        model = Servicios
        fields = ('nombre', 'servicio', 'latitud', 'longitud',)
