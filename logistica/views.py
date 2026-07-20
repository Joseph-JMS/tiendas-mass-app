import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from logistica.models import Entrega
from usuarios.decorators import requiere_rol
from usuarios.models import Usuario, notificar

logger = logging.getLogger(__name__)

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

        mensajes_estado = {
            Entrega.Estado.PREPARADO: "Tu pedido está siendo preparado.",
            Entrega.Estado.EN_CAMINO: "¡Tu pedido va en camino!",
            Entrega.Estado.ENTREGADO: "Tu pedido ha sido entregado. ¡Gracias por tu compra!",
            Entrega.Estado.FALLIDA: "Hubo un problema con la entrega de tu pedido.",
        }

        if nuevo_estado == Entrega.Estado.ENTREGADO:
            entrega.marcar_entregado()
            messages.success(request, "Entrega marcada como completada.")
        elif nuevo_estado == Entrega.Estado.FALLIDA:
            motivo = request.POST.get('motivo', Entrega.MotivoFallo.OTRO)
            entrega.reprogramar(motivo)
            logger.warning(
                f"Entrega fallida: pedido {entrega.pedido.numero_orden}, "
                f"motivo: {motivo}, repartidor: {request.user.username}"
            )
            messages.warning(request, "Entrega marcada como fallida.")
        elif nuevo_estado in Entrega.Estado.values:
            entrega.estado = nuevo_estado
            entrega.save(update_fields=['estado'])
            messages.success(request, "Estado actualizado.")

        if nuevo_estado in mensajes_estado:
            notificar(
                entrega.pedido.cliente,
                f"Pedido {entrega.pedido.numero_orden}: {mensajes_estado[nuevo_estado]}",
                url=f"/ventas/mis-pedidos/{entrega.pedido.id}/"
            )

    return redirect('logistica:mis_entregas')