from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from soporte.forms import TicketForm
from soporte.models import Ticket, LogError
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


@login_required
@requiere_rol(Usuario.Rol.SOPORTE, Usuario.Rol.ADMIN)
def panel_mantenimiento(request):
    nivel_filtro = request.GET.get('nivel', '')
    modulo_filtro = request.GET.get('modulo', '')

    logs = LogError.objects.all()

    if nivel_filtro:
        logs = logs.filter(nivel=nivel_filtro)
    if modulo_filtro:
        logs = logs.filter(modulo=modulo_filtro)

    logs = logs[:100]  # límite razonable para no sobrecargar la vista

    # Resumen rápido de salud del sistema (últimas 24h)
    hace_24h = timezone.now() - timedelta(hours=24)
    resumen = LogError.objects.filter(fecha__gte=hace_24h).aggregate(
        total=Count('id'),
    )
    criticos_24h = LogError.objects.filter(
        fecha__gte=hace_24h, nivel=LogError.Nivel.CRITICAL
    ).count()
    errores_24h = LogError.objects.filter(
        fecha__gte=hace_24h, nivel=LogError.Nivel.ERROR
    ).count()

    modulos_disponibles = (
        LogError.objects.values_list('modulo', flat=True).distinct()
    )

    return render(request, 'soporte/panel_mantenimiento.html', {
        'logs': logs,
        'niveles': LogError.Nivel.choices,
        'nivel_filtro': nivel_filtro,
        'modulo_filtro': modulo_filtro,
        'modulos_disponibles': modulos_disponibles,
        'total_24h': resumen['total'] or 0,
        'criticos_24h': criticos_24h,
        'errores_24h': errores_24h,
    })


@login_required
@requiere_rol(Usuario.Rol.SOPORTE, Usuario.Rol.ADMIN)
def registrar_log_prueba(request):
    """Utilidad de diagnóstico: permite generar un log de prueba para verificar
    que el sistema de registro de errores funciona correctamente."""
    if request.method == 'POST':
        LogError.objects.create(
            nivel=LogError.Nivel.INFO,
            modulo='soporte',
            mensaje=f"Log de prueba generado manualmente por {request.user.username}",
        )
        messages.success(request, "Log de prueba registrado correctamente.")
    return redirect('soporte:panel_mantenimiento')