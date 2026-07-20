from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from catalogo.models import Producto
from logistica.models import Zona, Entrega
from pagos.models import Pago, Comprobante
from pagos.pdf_utils import generar_pdf_comprobante
from usuarios.models import PerfilRepartidor
from ventas.models import Pedido, Venta


# Create your views here.
@login_required
def procesar_pago(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)

    if hasattr(pedido, 'pago'):
        messages.warning(request, "Este pedido ya tiene un pago registrado.")
        return redirect('ventas:ver_carrito')

    if request.method == 'POST':
        metodo = request.POST.get('metodo')

        if metodo not in Pago.Metodo.values:
            messages.error(request, "Método de pago inválido.")
            return redirect('pagos:procesar', pedido_id=pedido.id)

        with transaction.atomic():
            detalles = pedido.detalles.select_related('producto')
            for detalle in detalles:
                producto = Producto.objects.select_for_update().get(id=detalle.producto_id)
                if detalle.cantidad > producto.stock:
                    transaction.set_rollback(True)
                    messages.error(
                        request,
                        f"Lo sentimos, '{producto.nombre}' ya no tiene stock suficiente. "
                        f"Tu pedido ha sido cancelado, no se realizó ningún cobro."
                    )
                    return redirect('ventas:cancelar_pedido', pedido_id=pedido.id)

            for detalle in detalles:
                producto = detalle.producto
                producto.stock -= detalle.cantidad
                producto.save(update_fields=['stock'])

            pago = Pago.objects.create(
                pedido=pedido,
                metodo=metodo,
                monto=pedido.total,
            )
            pago.confirmar(referencia=f"SIM-{pago.id:06d}")

            igv = Comprobante.calcular_igv(pedido.subtotal_productos)
            total_con_igv = pedido.subtotal_productos + igv + pedido.costo_envio

            comprobante = Comprobante.objects.create(
                pago=pago,
                tipo=Comprobante.Tipo.BOLETA,
                serie="B001",
                numero=f"{pago.id:06d}",
                subtotal=pedido.subtotal_productos,
                igv=igv,
                total=total_con_igv,
            )

            Venta.objects.create(
                pedido=pedido,
                empleado=None,
                igv=igv,
                total_con_igv=total_con_igv,
            )

            repartidor_disponible = PerfilRepartidor.objects.filter(
                zona=pedido.zona,
                estado=PerfilRepartidor.Estado.DISPONIBLE
            ).first()

            Entrega.objects.create(
                pedido=pedido,
                zona=pedido.zona,
                repartidor=repartidor_disponible,
                direccion_entrega=pedido.direccion_entrega,
            )

            pedido.estado = Pedido.Estado.CONFIRMADO
            pedido.save(update_fields=['estado'])

        if not repartidor_disponible:
            messages.warning(request, "Pago confirmado, pero no hay repartidores disponibles en tu zona por ahora.")
        else:
            messages.success(request, f"Pago confirmado. Comprobante {comprobante}.")

        return redirect('pagos:confirmacion', pedido_id=pedido.id)

    return render(request, 'pagos/procesar.html', {
        'pedido': pedido,
        'metodos': Pago.Metodo.choices,
    })


@login_required
def confirmacion_pago(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
    return render(request, 'pagos/confirmacion.html', {'pedido': pedido})


@login_required
def descargar_comprobante(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)

    if not hasattr(pedido, 'pago') or not hasattr(pedido.pago, 'comprobante'):
        messages.error(request, "Este pedido aún no tiene un comprobante generado.")
        return redirect('ventas:mis_pedidos')

    buffer = generar_pdf_comprobante(pedido)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="comprobante_{pedido.numero_orden}.pdf"'
    return response