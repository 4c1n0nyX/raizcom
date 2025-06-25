import json
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from .models import Contact
from django.contrib import messages
from django.db import IntegrityError
from .forms import AddContactForm
from django.contrib.auth import get_user_model
from usuarios.models import Usuarios
User = get_user_model()

# =============== Vista de Contactos y Agregar Contactos ================ #
@login_required(login_url='login')
def contactos(request):
    add_contact_form = AddContactForm()
    if request.method == 'POST':
        add_contact_form = AddContactForm(request.POST)
        if add_contact_form.is_valid():
            username_to_add = add_contact_form.cleaned_data['username']
            
            try:
                contact_to_add = Usuarios.objects.get(username=username_to_add)
            except Usuarios.DoesNotExist:
                messages.error(request, f"El usuario '{username_to_add}' no existe.")
                return redirect("/contactos#noexist")

            if request.user == contact_to_add:
                messages.error(request, "No puedes agregarte a ti mismo como contacto.")
                return redirect("/contactos#self")

            existing_relationship = Contact.objects.filter(
                (Q(user=request.user) & Q(contact_user=contact_to_add)) |
                (Q(user=contact_to_add) & Q(contact_user=request.user))
            ).first()

            if existing_relationship:
                if existing_relationship.status == 'accepted':
                    messages.info(request, f"{contact_to_add.username} ya es uno de tus contactos.")
                    return redirect("/contactos#already")
                elif existing_relationship.status == 'pending':
                    if existing_relationship.user == request.user:
                        messages.info(request, f"Ya enviaste una solicitud a {contact_to_add.username} que está pendiente.")
                        return redirect("/contactos#pendent")
                    else:
                        messages.info(request, f"{contact_to_add.username} ya te envió una solicitud. Revísala en 'Solicitudes Pendientes'.")
                        return redirect("/contactos#pendent_request")
                elif existing_relationship.status == 'rejected':
                    if existing_relationship.user == request.user:
                        messages.warning(request, f"Tu solicitud previa a {contact_to_add.username} fue rechazada. Puedes intentar enviar una nueva.")
                        return redirect("/contactos#rejected")
                    else:
                        messages.warning(request, f"Rechazaste una solicitud de {contact_to_add.username}. Si deseas agregarlo, envíale una nueva solicitud.")
                        return redirect("/contactos#rejected_recived")

            try:
                Contact.objects.create(
                    user=request.user,
                    contact_user=contact_to_add,
                    status='pending'
                )
                messages.success(request, f"¡Solicitud de contacto enviada a {contact_to_add.username} con éxito!")
                return redirect("/contactos#sent")
            except IntegrityError:
                messages.error(request, f"Ha ocurrido un error al enviar la solicitud a {contact_to_add.username}.")
                return redirect("/contactos#error")
        else:
            messages.error(request, "El nombre de usuario es inválido.")
            return redirect("/contactos#invalid")

    my_contacts_queryset = Contact.objects.filter(user=request.user, status='accepted').select_related('contact_user').order_by('contact_user__username')
    sent_requests_pending = Contact.objects.filter(user=request.user, status='pending').select_related('contact_user').order_by('contact_user__username')
    received_requests_pending = Contact.objects.filter(contact_user=request.user, status='pending').select_related('user').order_by('user__username')
    
    context = {
        'contactos': my_contacts_queryset,
        'add_contact_form': add_contact_form,
        'sent_requests_pending': sent_requests_pending,
        'received_requests_pending': received_requests_pending,
    }
    return render(request, 'agenda.html', context)

# =============== Vista de Aceptar Contactos ================ #
@login_required
def accept_contact_request(request, request_id):
    contact_entry = get_object_or_404(Contact, id=request_id)

    if request.user == contact_entry.contact_user and contact_entry.status == 'pending':
        if contact_entry.accept_request():
            messages.success(request, f"Has aceptado la solicitud de {contact_entry.user.username}. Ahora son contactos.")
        else:
            messages.warning(request, "La solicitud ya no está pendiente o ha ocurrido un error.")
    else:
        messages.error(request, "No tienes permiso para realizar esta acción o la solicitud no es válida.")
    
    return redirect("/contactos#acepted")

# =============== Vista de Rechazar Contactos ================ #
@login_required
def reject_contact_request(request, request_id):
    contact_entry = get_object_or_404(Contact, id=request_id)
    contact_entry.delete()
    return redirect("/contactos#rejectedr")

# =============== Vista de Solicitud Eliminada ================ #
@login_required
def cancel_contact_request(request, request_id):
    contact_entry = get_object_or_404(Contact, id=request_id)
    contact_entry.delete()
    return redirect("/contactos#requestdelete")

# =============== Vista de Eliminar Contacto ================ #
@login_required(login_url='login')
def delete_contacto(request, id):
    queryset = get_object_or_404(Contact, id=id)
    if request.method == 'POST':
        queryset.delete()
        return redirect('/contactos#success')
