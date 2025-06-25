from django.shortcuts import render
from django.http import JsonResponse
from publicaciones.models import Servicios

def mapa_servicios(request):
    servicios = Servicios.objects.all()
    
    servicios_data = []
    for servicio in servicios:
        servicios_data.append({
            'nombre': servicio.nombre,
            'servicio': servicio.servicio,
            'latitud': servicio.latitud,
            'longitud': servicio.longitud,
        })
    
    context = {
        'servicios_json': servicios_data
    }
    return render(request, 'servicios.html', context)

def api_servicios(request):
    servicios = Servicios.objects.all()
    servicios_data = []
    for servicio in servicios:
        servicios_data.append({
            'nombre': servicio.nombre,
            'servicio': servicio.servicio,
            'latitud': servicio.latitud,
            'longitud': servicio.longitud,
        })
    return JsonResponse({'servicios': servicios_data})