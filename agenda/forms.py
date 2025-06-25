from django import forms
from django.contrib.auth import get_user_model
User = get_user_model() 

# =============== Formulario de Agregar Contactos ================ #
class AddContactForm(forms.Form):
    username = forms.CharField(
        label="Nombre de usuario del contacto",
        help_text="Introduce el nombre de usuario del contacto que quieres agregar."
    )

    def clean_username(self):
        username_input = self.cleaned_data['username']
        try:
            user_to_add = User.objects.get(username__iexact=username_input)
        except User.DoesNotExist:
            raise forms.ValidationError("El nombre de usuario no existe.")
        
        return user_to_add