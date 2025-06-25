from django import forms
import re
from usuarios.models import Usuarios
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

#################### FORMULARIOS DE USUARIO #####################

# =============== Formulario de Actualizar Usuario ================ #
class UsuariosU(forms.ModelForm):
    class Meta:
        model = Usuarios
        fields = ['email', 'telefono',]

# =============== Formulario de Actualizar Foto de Usuario ================ #
class UsuariosUI(forms.ModelForm):
    class Meta:
        model = Usuarios
        fields = ('foto',)

# =============== Formulario de Actualizar Password de Usuario ================ #
class UsuariosUP(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Nueva Contraseña")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirmar Nueva Contraseña")

    class Meta:
        model = Usuarios
        fields = ('password',)
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise ValidationError("La contraseña no puede estar vacía.")
        if len(password) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if not any(char.isupper() for char in password):
            raise ValidationError("La contraseña debe contener al menos una letra mayúscula.")
        if not any(char.islower() for char in password):
            raise ValidationError("La contraseña debe contener al menos una letra minúscula.")
        if not any(char.isdigit() for char in password):
            raise ValidationError("La contraseña debe contener al menos un número.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("La contraseña debe contener al menos un carácter especial.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Las contraseñas no coinciden.")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False) 
        user.set_password(self.cleaned_data["password"])
        
        if commit:
            user.save()
            
        return user
