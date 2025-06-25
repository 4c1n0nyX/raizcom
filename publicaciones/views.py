
from django.shortcuts import render, redirect, get_object_or_404, render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage 
from django.contrib.auth.decorators import login_required
from .forms import NoticiasForm, NoticiasAForm, NoticiasAIForm, RecursosForm, RecursosAForm, ServiciosForm, ServiciosAForm
from .models import Noticias, Recursos, Servicios
from index.decorators import allowed_users
from django.utils import timezone
from django.db.models import Prefetch
from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse

#################### VISTAS DE NOTICIAS #####################

# =============== Vista de Noticias y creador de Noticias ================ #
@login_required(login_url='login')
@allowed_users(allowed_roles=['administrador', 'publicador'])
def noticias(request):
    if request.method == 'POST':
        form1 = NoticiasForm(request.POST, request.FILES)
        if form1.is_valid():
            registro = Noticias(
                titulo=form1.cleaned_data['titulo'],
                contenido=form1.cleaned_data['contenido'],
                imagen=form1.cleaned_data['imagen'],
            )
            registro.save()
            return redirect("/publicaciones/noticias#success")
        else:
            return redirect("/publicaciones/noticias#error")
    
    publicaciones = Noticias.objects.all()
    paginator = Paginator(publicaciones, 15)
    pagina = request.GET.get('page')

    try:
        pagina_actual = paginator.page(pagina)
    except PageNotAnInteger:
        pagina_actual = paginator.page(1)
    except EmptyPage:
        pagina_actual = paginator.page(paginator.num_pages)

    context = {'form1': NoticiasForm(), 'form2': NoticiasAForm(), 'form3':NoticiasAIForm, 'publicaciones': pagina_actual}
    return render(request, 'noticias.html', context)

# =============== Consultar Noticias ================ #
@login_required(login_url='login')
@allowed_users(allowed_roles=['administrador'])
def consultar_noticias(request, accion):
    if accion == 'consultar':
        if 'nombre' in request.GET:
            noticia = request.GET['nombre']
            noiticias = Noticias.objects.filter(titulo__contains=noticia).all().order_by("titulo")
            paginator = Paginator(noiticias, 15)
            pagina = request.GET.get('page')
            try:
                pagina_actual = paginator.page(pagina)
            except PageNotAnInteger:
                pagina_actual = paginator.page(1)
            except EmptyPage:
                pagina_actual = paginator.page(paginator.num_pages)
        context = {'form1': NoticiasForm(), 'form2': NoticiasAForm(), 'form3':NoticiasAIForm, 'publicaciones': pagina_actual}
        return render(request, 'noticias.html', context)

# =============== Vista de Editar Noticias ================ #
@login_required(login_url='login')
@allowed_users(allowed_roles=['administrador', 'publicador'])
def update_noticias(request, id):
    queryset = get_object_or_404(Noticias, id=id)
    if request.method == 'POST':
        form2 = NoticiasAForm(request.POST, instance=queryset)
        if form2.is_valid():
            queryset.titulo = form2.cleaned_data['titulo']
            queryset.contenido = form2.cleaned_data['contenido']
            queryset.save()
            return redirect('/publicaciones/noticias#success')

# =============== Vista de Editar Imagen de Noticias ================ #
@login_required(login_url='login')
@allowed_users(allowed_roles=['administrador', 'publicador'])
def updatei_noticias(request, id):
    queryset = get_object_or_404(Noticias, id=id)
    if request.method == 'POST':
        form3 = NoticiasAIForm(request.POST, request.FILES, instance=queryset)
        if form3.is_valid():
            queryset.imagen = form3.cleaned_data['imagen']
            queryset.save()
            return redirect('/publicaciones/noticias#success')

# =============== Vista de Eliminar Noticias ================ #
@login_required(login_url='login')
@allowed_users(allowed_roles=['administrador', 'publicador'])
def delete_noticias(request, id):
    queryset = get_object_or_404(Noticias, id=id)
    if request.method == 'POST':
        queryset.delete()
        return redirect('/publicaciones/noticias#success')

#################### VISTAS DE RECURSOS #####################

# =============== Vista de Recursos y creador de Recursos ================ #
@login_required(login_url='login')
@allowed_users(allowed_roles=['administrador', 'publicador'])
def recursos(request):
    if request.method == 'GET':
        hoy = timezone.localdate() 
        recursos_a_finalizar = Recursos.objects.filter(fecha__lt=hoy)
        recursos_a_finalizar.update(estatus='FINALIZADO')

    if request.method == 'POST':
        form1 = RecursosForm(request.POST)
        if form1.is_valid():
            if form1.cleaned_data['tipo_recurso'] == 'Gas (Pago)' or form1.cleaned_data['tipo_recurso'] == 'Bolsas de Comida (Pago)':
                registro = Recursos(
                    tipo_recurso=form1.cleaned_data['tipo_recurso'],
                    fecha=form1.cleaned_data['fecha'],
                    lugar='N/A',
                    precio=form1.cleaned_data['precio'],
                    pago=True,
                    estatus='ACTIVO'
                )
                registro.save()
                return redirect("/publicaciones/recursos#success")
            else:
                registro = Recursos(
                    tipo_recurso=form1.cleaned_data['tipo_recurso'],
                    fecha=form1.cleaned_data['fecha'],
                    lugar=form1.cleaned_data['lugar'],
                    pago=False,
                    estatus='ACTIVO'
                )
                registro.save()
                return redirect("/publicaciones/recursos#success")
        else:
            return redirect("/publicaciones/recursos#error")
        
        
    
    publicacionesa = Recursos.objects.filter(estatus='ACTIVO').prefetch_related(Prefetch('recursos', to_attr='recursos_pagos_relacionados')).order_by('recursos__comunidad')[:30]
    publicacionesf = Recursos.objects.filter(estatus='FINALIZADO').prefetch_related(Prefetch('recursos', to_attr='recursos_pagos_relacionados')).order_by('recursos__comunidad')[:30]

    context = {'form1': RecursosForm(), 'form2': RecursosAForm(), 'publicacionesa': publicacionesa, 'publicacionesf': publicacionesf}
    return render(request, 'recursos.html', context)

# =============== Vista de Editar Recursos ================ #
@login_required(login_url='login')
@allowed_users(allowed_roles=['administrador', 'publicador'])
def update_recursos(request, id):
    queryset = get_object_or_404(Recursos, id=id)
    if request.method == 'POST':
        form2 = RecursosAForm(request.POST, instance=queryset)
        if form2.is_valid():
            if queryset.tipo_recurso == 'Gas (Pago)' or queryset.tipo_recurso == 'Bolsas de Comida (Pago)':
                queryset.fecha = form2.cleaned_data['fecha']
                queryset.precio = form2.cleaned_data['precio']
                queryset.save()
                return redirect('/publicaciones/recursos#success')
            else:
                queryset.lugar = form2.cleaned_data['lugar']
                queryset.fecha = form2.cleaned_data['fecha']
                queryset.save()
                return redirect('/publicaciones/recursos#success')
        
# =============== Vista de Finalizar Recursos ================ #
@login_required(login_url='login')
@allowed_users(allowed_roles=['administrador', 'publicador'])
def finalizar_recursos(request, id):
    queryset = get_object_or_404(Recursos, id=id)
    if request.method == 'POST':
        queryset.estatus = 'FINALIZADO'
        queryset.save()
        return redirect('/publicaciones/recursos#success')

# =============== Vista de Imprimir Lista de Recursos ================ #
@login_required(login_url='login')
@allowed_users(allowed_roles=['administrador', 'publicador'])
def print_recursos(request):
    queryset = Recursos.objects.all().prefetch_related(Prefetch('recursos', to_attr='recursos_pagos_relacionados')).order_by('fecha')
    base_url = request.build_absolute_uri('/')
    html_string = render_to_string('print.html', {'resultados': queryset})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="reporte.pdf"'
    HTML(string=html_string, base_url=base_url).write_pdf(response)
    return response

# =============== Vista de Eliminar Recursos ================ #
@login_required(login_url='login')
@allowed_users(allowed_roles=['administrador', 'publicador'])
def delete_recursos(request, id):
    queryset = get_object_or_404(Recursos, id=id)
    if request.method == 'POST':
        queryset.delete()
        return redirect('/publicaciones/recursos#success')

#################### VISTAS DE SERVICIOS #####################

# =============== Vista de Servicios y creador de Servicios ================ #
@login_required(login_url='login')
@allowed_users(allowed_roles=['administrador', 'publicador'])
def servicios(request):
    if request.method == 'POST':
        form1 = ServiciosForm(request.POST)
        if form1.is_valid():
            registro = Servicios(
                nombre=form1.cleaned_data['nombre'],
                servicio=form1.cleaned_data['servicio'],
                latitud=form1.cleaned_data['latitud'],
                longitud=form1.cleaned_data['longitud'],
            )
            registro.save()
            return redirect("/publicaciones/pservicios#success")

        else:
            return redirect("/publicaciones/pservicios#error")
        
    servicios = Servicios.objects.all()

    context = {'form1': ServiciosForm(), 'form2': ServiciosAForm(), 'servicios': servicios}
    return render(request, 'pservicios.html', context)

# =============== Vista de Editor de Servicios ================ #
@login_required(login_url='login')
@allowed_users(allowed_roles=['administrador', 'publicador'])
def update_servicios(request, id):
    queryset = get_object_or_404(Servicios, id=id)
    if request.method == 'POST':
        form2 = ServiciosAForm(request.POST, instance=queryset)
        if form2.is_valid():
            queryset.nombre = form2.cleaned_data['nombre']
            queryset.servicio = form2.cleaned_data['servicio']
            queryset.latitud = form2.cleaned_data['latitud']
            queryset.longitud = form2.cleaned_data['longitud']
            queryset.save()
            return redirect('/publicaciones/pservicios#success')

# =============== Vista de Eliminar Servicios ================ #
@login_required(login_url='login')
@allowed_users(allowed_roles=['administrador', 'publicador'])
def delete_servicios(request, id):
    queryset = get_object_or_404(Servicios, id=id)
    if request.method == 'POST':
        queryset.delete()
        return redirect('/publicaciones/pservicios#success')
        