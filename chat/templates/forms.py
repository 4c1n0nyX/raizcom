from django import forms
from publicaciones.models import Recursos_Pagos

# =============== Formulario de Reporar Pago ================ #
class RecursosR(forms.ModelForm):
    class Meta:
        model = Recursos_Pagos
        fields = ('comprbante',)

