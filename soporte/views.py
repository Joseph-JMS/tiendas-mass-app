from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from soporte.forms import TicketForm
from soporte.models import Ticket
from usuarios.decorators import requiere_rol
from usuarios.models import Usuario


@login_required
def crear_ticket(request):
    """Cualquier usuario autenticado puede abrir un ticket."""
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.cliente = request.user
            ticket.save()
            messages.success(request, f"Ticket #{ticket.id} creado. Te contactaremos pronto.")
            return redirect('soporte:mis_tickets')
    else:
        form = TicketForm()
    return render(request, 'soporte/form_ticket.html', {'form': form})


@login_required
def mis_tickets(request):
    """Tickets creados por el usuario actual (cualquier rol)."""
    tickets = Ticket.objects.filter(cliente=request.user).order_by('-fecha_creacion')
    return render(request, 'soporte/mis_tickets.html', {'tickets': tickets})


@login_required
@requiere_rol(Usuario.Rol.SOPORTE, Usuario.Rol.ADMIN)
def lista_tickets(request):
    """Panel de soporte técnico: todos los tickets del sistema."""
    estado_filtro = request.GET.get('estado', '')
    tickets = Ticket.objects.select_related('cliente', 'asignado_a').order_by('-fecha_creacion')

    if estado_filtro:
        tickets = tickets.filter(estado=estado_filtro)

    return render(request, 'soporte/lista_tickets.html', {
        'tickets': tickets,
        'estados': Ticket.Estado.choices,
        'estado_filtro': estado_filtro,
    })


@login_required
@requiere_rol(Usuario.Rol.SOPORTE, Usuario.Rol.ADMIN)
def atender_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in Ticket.Estado.values:
            ticket.estado = nuevo_estado
            if nuevo_estado == Ticket.Estado.RESUELTO:
                ticket.fecha_resolucion = timezone.now()
            ticket.asignado_a = request.user
            ticket.save()
            messages.success(request, "Ticket actualizado.")

    return redirect('soporte:lista_tickets')