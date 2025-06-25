from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from agenda.models import Contact
from .models import ChatRoom, Message
from publicaciones.models import Recursos, Recursos_Pagos
from django.contrib.auth import get_user_model
from .forms import RecursosR
from django.utils import timezone
from django.db.models import Prefetch
User = get_user_model()

# =============== VISTA DE CHAT GENERAL ============== #
@login_required(login_url='login')
def chat_general(request):
    general_room = ChatRoom.get_general_chat_room()
    
    if request.user not in general_room.participants.all():
        general_room.participants.add(request.user)
    
    messages_history = Message.objects.filter(
        chatroom=general_room
    ).order_by('timestamp')

    my_contacts_queryset = Contact.objects.filter(user=request.user).select_related('contact_user').order_by('contact_user__username')
    
    context = {
        'chat_room_id': general_room.id,
        'messages': messages_history,
        'room_name': general_room.name,
        'contactos': my_contacts_queryset,
    }
    return render(request, "chat_general.html", context)

# =============== VISTA DE CHAT POR PERSONA ============== #
@login_required(login_url='login')
def chat_view(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    if request.user.id == other_user.id:
        messages.warning(request, "No puedes iniciar un chat contigo mismo.")
        return redirect('contacts_list')

    chat_room = ChatRoom.get_or_create_private_room(request.user, other_user)
    messages_history = Message.objects.filter(
        chatroom=chat_room
    ).order_by('timestamp')

    my_contacts_queryset = Contact.objects.filter(user=request.user).select_related('contact_user').order_by('contact_user__username')

    context = {
        'other_user': other_user,
        'chat_room_id': chat_room.id,
        'messages': messages_history,
        'contactos': my_contacts_queryset,
    }
    return render(request, 'chat.html', context)

# =============== VISTA DE RECURSOS DISPONIBLES ============== #
@login_required(login_url='login')
def recursos_view(request):
    general_room = ChatRoom.get_general_chat_room()
    
    if request.user not in general_room.participants.all():
        general_room.participants.add(request.user)
    
    messages_history = Message.objects.filter(
        chatroom=general_room
    ).order_by('timestamp')

    my_contacts_queryset = Contact.objects.filter(user=request.user).select_related('contact_user').order_by('contact_user__username')
    pagos_del_usuario = Recursos_Pagos.objects.filter(cedula=request.user.username)
    publicacionesa = Recursos.objects.filter(estatus='ACTIVO').prefetch_related(Prefetch('recursos', queryset=pagos_del_usuario, to_attr='pagos_del_usuario_actual')).order_by('-fecha')

    context = {
        'chat_room_id': general_room.id,
        'messages': messages_history,
        'room_name': general_room.name,
        'contactos': my_contacts_queryset,
        'publicacionesa': publicacionesa,
        'form1': RecursosR(),
    }
    return render(request, "grecursos.html", context)

@login_required(login_url='login')
def recursos_report(request, id):
    data = get_object_or_404(Recursos, id=id)
    if request.method == 'POST':
        form1 = RecursosR(request.POST, request.FILES)
        if form1.is_valid():
            comprobante = form1.cleaned_data['comprobante']
            nombre = request.user.first_name
            apellido = request.user.last_name
            usuario = f"{nombre} {apellido}"
            cedula = request.user.username
            comunidad = request.user.comunidad
            hoy = timezone.now()

            Recursos_Pagos.objects.update_or_create(
                recurso = data,
                cedula = cedula,
                defaults={
                    'usuario': usuario,
                    'comunidad': comunidad,
                    'comprobante': comprobante,
                    'fechap': hoy,
                }
            )
            return redirect("/chat/grecursos/#success")

# =============== VISTA DE ALERTAS DE EMERGENCIAS ============== #
@login_required(login_url='login')
def alertas(request):
    try:
        bot_user = User.objects.get(username='alertas_bot')
    except User.DoesNotExist:
        messages.error(request, "Error: El usuario del bot de alertas ('alertas_bot') no se encontró en la base de datos.")
        return render(request, 'alertas.html', {'alerts': []})

    alertas_room = ChatRoom.get_alertas_chat_room()

    sismo_alerts = Message.objects.filter(chatroom=alertas_room, sender=bot_user).order_by('-timestamp')[:20]

    my_contacts_queryset = Contact.objects.filter(user=request.user).select_related('contact_user').order_by('contact_user__username')

    context = {
        'alerts': sismo_alerts,
        'contactos': my_contacts_queryset,
    }
    return render(request, 'alertas.html', context)
