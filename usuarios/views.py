
from django.shortcuts import render, redirect, get_object_or_404, render
from django.contrib.auth.models import Group
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage 
from django.contrib.auth.decorators import login_required
from index.decorators import allowed_users
from .forms import UsuarioForm, UsuarioAForm, UsuarioAPForm, UsuariosAIForm, ComunidadForm, ComunidadAForm
from .models import Usuarios, Comunidad
from django.db import IntegrityError
import re

#################### VISTAS DE USUARIOS #####################

# =============== Vista de Usuario y Creación de Usuario ================ #
@login_required(login_url='login')
@allowed_users(allowed_roles=['administrador'])
def usuarios(request):
    usersl = Usuarios.objects.all()
    grupos = Group.objects.all()
    comunidades = Comunidad.objects.all()
    paginator = Paginator(usersl, 14)
    pagina = request.GET.get('page')

    try:
        pagina_actual = paginator.page(pagina)
    except PageNotAnInteger:
        pagina_actual = paginator.page(1)
    except EmptyPage:
        pagina_actual = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        form1 = UsuarioForm(request.POST, request.FILES)
        if form1.is_valid():
            try:
                usuario = form1.save()
                return redirect("/usuarios#success")
            except IntegrityError:
                return redirect("/usuarios#errorexist")
        else:
            if 'password' in form1.errors or 'password_confirm' in form1.errors:
                return redirect("/usuarios#passworderror") 

            if 'username' in form1.errors:
                return redirect("/usuarios#failusername")
            
            if 'email' in form1.errors:
                return redirect("/usuarios#failcorreo")
            
            if 'telefono' in form1.errors:
                return redirect("/usuarios#failtelefono")

            return redirect("/usuarios#error")
    
    else:
        form1 = UsuarioForm()
    
    context = {
        'form1': form1,
        'form2': UsuarioAForm(),
        'form3': UsuarioAPForm(),
        'form4': UsuariosAIForm(),
        'usersl': pagina_actual,
        'grupos': grupos,
        'comunidades': comunidades
    }
    return render(request, 'usuarios.html', context)

# =============== Consultar Usuarios ================ #
@login_required(login_url='login')
@allowed_users(allowed_roles=['administrador'])
def consultar_usuarios(request, accion):
    grupos = Group.objects.all()
    comunidades = Comunidad.objects.all()
    if accion == 'consultar':
        if 'nombre' in request.GET:
            username = request.GET['nombre']
            usuarios = Usuarios.objects.filter(username__contains=username).all().order_by("username")
            paginator = Paginator(usuarios, 14)
            pagina = request.GET.get('page')
            try:
                pagina_actual = paginator.page(pagina)
            except PageNotAnInteger:
                pagina_actual = paginator.page(1)
            except EmptyPage:
                pagina_actual = paginator.page(paginator.num_pages)
        context = {
            'form1': UsuarioForm,
            'form2': UsuarioAForm(),
            'form3': UsuarioAPForm(),
            'form4': UsuariosAIForm(),
            'usersl': pagina_actual,
            'grupos': grupos,
            'comunidades': comunidades
        }
        return render(request, 'usuarios.html', context)

# =============== Vista de Editar Usuario ================ #
@login_required(login_url='login')
@allowed_users(allowed_roles=['administrador'])
def update_usuarios(request, id):
    usuario = get_object_or_404(Usuarios, id=id)
    if request.method == 'POST':
        form = UsuarioAForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save() 
            return redirect('/usuarios#success')

# =============== Vista de Editar Password de Usuario ================ #
@login_required(login_url='login')
@allowed_users(allowed_roles=['administrador'])
def updatep_usuarios(request, id):
    usuario_a_editar = get_object_or_404(Usuarios, id=id)
    if request.method == 'POST':
        formp = UsuarioAPForm(request.POST, instance=usuario_a_editar)
        if formp.is_valid():
            try:
                formp.save()
                return redirect(f"/usuarios#success")
            except IntegrityError:
                return redirect(f"/usuarios#passworderror")
        else:
            if 'password' in formp.errors or 'password_confirm' in formp.errors:
                return redirect(f"/usuarios#passworderror") 
            else:
                return redirect(f"/usuarios#passworderror") 
    else:
        return redirect('/usuarios') 

# =============== Vista de Editar Imagen de Usuario ================ #
def updatei_usuarios(request, id):
    queryset = get_object_or_404(Usuarios, id=id)
    if request.method == 'POST':
        form4 = UsuariosAIForm(request.POST, request.FILES, instance=queryset)
        if form4.is_valid():
            queryset.foto = form4.cleaned_data['foto']
            queryset.save()
            return redirect('/usuarios#success')

# =============== Vista de Eliminar Usuario ================ #
@login_required(login_url='login')
@allowed_users(allowed_roles=['administrador'])
def delete_usuarios(request, id):
    queryset = get_object_or_404(Usuarios, id=id)
    if request.method == 'POST':
        queryset.delete()
        return redirect('/usuarios#success')

#################### VISTAS DE COMUNIDADES #####################

# =============== Vista de Comunidades y crear de Comunidad ================ #
@login_required(login_url='login')
@allowed_users(allowed_roles=['administrador'])
def comunidades(request):
    if request.method == 'POST':
        form1 = ComunidadForm(request.POST)
        if form1.is_valid():
            registro = Comunidad(
                comunidad=form1.cleaned_data['comunidad']
            )
            registro.save()
            return redirect('/usuarios/comunidad/#success')
        else:
            return redirect('/usuarios/comunidad/#error')
    comunidades = Comunidad.objects.all()
    context = {'form1': ComunidadForm(), 'form2': ComunidadAForm(), 'comunidades': comunidades}
    return render(request, 'comunidades.html', context)

# =============== Vista de Editar Comunidades ================ #
@login_required(login_url='login')
@allowed_users(allowed_roles=['administrador'])
def update_comunidades(request, id):
    queryset = get_object_or_404(Comunidad, id=id)
    if request.method == 'POST':
        form2 = ComunidadAForm(request.POST, instance=queryset)
        if form2.is_valid():
            queryset.comunidad = form2.cleaned_data['comunidad']
            queryset.save()
            return redirect('/usuarios/comunidad/#success')
        
# =============== Vista de Eliminar Comunidad ================ #
@login_required(login_url='login')
@allowed_users(allowed_roles=['administrador'])
def delete_comunidades(request, id):
    queryset = get_object_or_404(Comunidad, id=id)
    if request.method == 'POST':
        queryset.delete()
        return redirect('/usuarios/comunidad/#success')