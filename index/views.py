from django.shortcuts import render, redirect, render, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from .decorators import no_autenticado, allowed_users
from django.db import IntegrityError
from publicaciones.models import Noticias
from usuarios.models import Usuarios
from .forms import UsuariosU
from .forms import UsuariosUP
from .forms import UsuariosUI

# =============== Vista de Cierre de Sesión ================ #
def logoutUser(request):
    logout(request)
    return redirect('index')

# =============== Vista de Acceso Denegado 403 ================ #
def loginf403(request):
    return render(request, "403.html")

# =============== Vista de Inicio de Sesión ================ #
@no_autenticado
def loginf(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('/')
        else:
            return render(request, "login_error.html")
    context = {}
    return render(request, "login.html", context)

# =============== Vista de Inicio ================ #
@login_required(login_url='login')
def inicio(request):
    es_administrador = False
    es_administrador_o_publicador = False

    if request.user.is_authenticated:
        es_administrador = request.user.is_member('administrador')

    if request.user.is_authenticated:
        es_administrador_o_publicador = (
            request.user.is_member('administrador') or 
            request.user.is_member('publicador')
        )
        
    noticias = Noticias.objects.order_by('-fecha_publicacion')[:10] 
    
    context = {
        'noticias': noticias,
        'es_administrador': es_administrador,
        'es_administrador_o_publicador': es_administrador_o_publicador
    }

    return render(request, "inicio.html", context)

# =============== Vista de Usuario ================ #
@login_required(login_url='login')
def user(request):
    context = {'form2': UsuariosU(), 'form3': UsuariosUP(), 'form4': UsuariosUI()}
    return render(request, 'user.html', context)

# =============== Vista de Editar Usuario ================ #
def user_u(request, id):
    queryset = get_object_or_404(Usuarios, id=id)
    if request.method == 'POST':
        form = UsuariosU(request.POST, instance=queryset)
        if form.is_valid():
            queryset.email = form.cleaned_data['email']
            queryset.telefono = form.cleaned_data['telefono']
            queryset.save()
            return redirect('/usuario#success')

# =============== Vista de Editar Password de Usuario ================ #
def user_up(request, id):
    queryset = get_object_or_404(Usuarios, id=id)
    if request.method == 'POST':
        form3 = UsuariosUP(request.POST, instance=queryset)
        if form3.is_valid():
            try:
                form3.save()
                return redirect(f"/usuario#success")
            except IntegrityError:
                return redirect(f"/usuario#passworderror")
        else:
            if 'password' in form3.errors or 'password_confirm' in form3.errors:
                return redirect(f"/usuario#passworderror") 
            else:
                return redirect(f"/usuario#passworderror") 
    else:
        return redirect('/usuario') 

# =============== Vista de Editar Imagen de Usuario ================ #
def user_ui(request, id):
    queryset = get_object_or_404(Usuarios, id=id)
    if request.method == 'POST':
        form4 = UsuariosUI(request.POST, request.FILES, instance=queryset)
        if form4.is_valid():
            queryset.foto = form4.cleaned_data['foto']
            queryset.save()
            return redirect('/usuario#success')