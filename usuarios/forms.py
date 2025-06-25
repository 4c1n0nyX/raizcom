from django import forms
import re
from .models import Usuarios, Comunidad
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.shortcuts import redirect

#################### FORMULARIOS DE USUARIOS #####################

# =============== Formulario de Crear Usuarios ================ #
class UsuarioForm(forms.ModelForm):
    tipo = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        empty_label="Selecciona un grupo",
        to_field_name="name",
        required=True,
        label="Grupo de Usuario"
    )

    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirmar Contraseña")

    class Meta:
        model = Usuarios
        fields = ['username', 'first_name', 'last_name', 'email', 'telefono', 'comunidad', 'foto', 'tipo', 'password']

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
            nombre_grupo = self.cleaned_data.get('tipo')
            if nombre_grupo:
                try:
                    grupo = Group.objects.get(name=nombre_grupo)
                    user.groups.add(grupo)
                except Group.DoesNotExist:
                    pass
        return user

# =============== Formulario de Actualizar Usuario ================ #
class UsuarioAForm(forms.ModelForm):
    tipo = forms.ChoiceField(label="Tipo de Usuario", required=True)

    class Meta:
        model = Usuarios
        fields = ['username', 'first_name', 'last_name', 'email', 'telefono', 'comunidad', 'tipo',]

    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)

        grupos_existentes = Group.objects.all()
        self.fields['tipo'].choices = [(g.name, g.name) for g in grupos_existentes]

        if self.user_instance and self.user_instance.groups.exists():
            current_group_name = self.user_instance.groups.first().name
            self.fields['tipo'].initial = current_group_name

        if self.user_instance and self.user_instance.id == 1:
            self.fields['tipo'].disabled = True
            self.fields['tipo'].required = False

    def clean_tipo(self):
        nuevo_tipo_nombre = self.cleaned_data['tipo']
        if self.user_instance and self.user_instance.id == 1:
            grupo_actual_nombre = None
            if self.user_instance.groups.exists():
                grupo_actual_nombre = self.user_instance.groups.first().name
            if nuevo_tipo_nombre != grupo_actual_nombre:
                raise forms.ValidationError(
                    "No se puede cambiar el tipo de usuario para el ID 1."
                )
        return nuevo_tipo_nombre

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if self.user_instance:
            if username != self.user_instance.username:
                if Usuarios.objects.filter(username=username).exists():
                    raise forms.ValidationError("Este nombre de usuario ya está en uso por otro usuario.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)

        if commit:
            user.save()

            nuevo_tipo_nombre = self.cleaned_data.get('tipo')
            if nuevo_tipo_nombre:
                try:
                    user.groups.clear()
                    grupo = Group.objects.get(name=nuevo_tipo_nombre)
                    user.groups.add(grupo)
                except Group.DoesNotExist:
                    pass
        return user

# =============== Formulario de Actualizar Foto de Usuario ================ #
class UsuariosAIForm(forms.ModelForm):
    class Meta:
        model = Usuarios
        fields = ('foto',)

# =============== Formulario de Actualizar Password de Usuario ================ #
class UsuarioAPForm(forms.ModelForm):
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

#################### FORMULARIOS DE COMUNIDADES #####################

# =============== Formulario de Crear Comunidad ================ #
class ComunidadForm(forms.ModelForm):
    class Meta:
        model = Comunidad
        fields = ('comunidad',)

# =============== Formulario de Actualizar Noticias ================ #
class ComunidadAForm(forms.ModelForm):
    class Meta:
        model = Comunidad
        fields = ('comunidad',)