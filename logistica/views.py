from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from logistica.models import Entrega
from usuarios.decorators import requiere_rol
from usuarios.models import Usuario


@login_required
@requiere_rol(Usuario.Rol.REPARTIDOR)
def mis_entregas(request):
    perfil_repartidor = request.user.perfil_empleado.perfil_repartidor
    entregas = Entrega.objects.filter(
        repartidor=perfil_repartidor
    ).exclude(estado=Entrega.Estado.ENTREGADO).select_related('pedido', 'zona')

    return render(request, 'logistica/mis_entregas.html', {'entregas': entregas})


@login_required
@requiere_rol(Usuario.Rol.REPARTIDOR)
def actualizar_estado_entrega(request, entrega_id):
    perfil_repartidor = request.user.perfil_empleado.perfil_repartidor
    entrega = get_object_or_404(Entrega, id=entrega_id, repartidor=perfil_repartidor)

    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')

        if nuevo_estado == Entrega.Estado.ENTREGADO:
            entrega.marcar_entregado()
            messages.success(request, "Entrega marcada como completada.")
        elif nuevo_estado == Entrega.Estado.FALLIDA:
            motivo = request.POST.get('motivo', Entrega.MotivoFallo.OTRO)
            entrega.reprogramar(motivo)
            messages.warning(request, "Entrega marcada como fallida.")
        elif nuevo_estado in Entrega.Estado.values:
            entrega.estado = nuevo_estado
            entrega.save(update_fields=['estado'])
            messages.success(request, "Estado actualizado.")

    return redirect('logistica:mis_entregas')