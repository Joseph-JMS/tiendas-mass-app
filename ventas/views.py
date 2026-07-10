from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST

from catalogo.models import Producto
from logistica.models import Zona
from ventas.carrito import Carrito
from ventas.models import Pedido, DetallePedido


@login_required
@require_POST
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, activo=True)
    cantidad = int(request.POST.get('cantidad', 1))

    if cantidad > producto.stock:
        messages.error(request, f"Solo hay {producto.stock} unidades disponibles.")
        return redirect('catalogo:lista_productos')

    carrito = Carrito(request)
    carrito.agregar(producto, cantidad)
    messages.success(request, f"{producto.nombre} agregado al carrito.")
    return redirect('ventas:ver_carrito')


@login_required
def ver_carrito(request):
    carrito = Carrito(request)
    return render(request, 'ventas/carrito.html', {'carrito': carrito})


@login_required
@require_POST
def actualizar_carrito(request, producto_id):
    cantidad = int(request.POST.get('cantidad', 1))
    carrito = Carrito(request)
    carrito.actualizar_cantidad(producto_id, cantidad)
    return redirect('ventas:ver_carrito')


@login_required
@require_POST
def eliminar_del_carrito(request, producto_id):
    carrito = Carrito(request)
    carrito.eliminar(producto_id)
    return redirect('ventas:ver_carrito')


@login_required
def checkout(request):
    carrito = Carrito(request)

    if len(carrito) == 0:
        messages.warning(request, "Tu carrito está vacío.")
        return redirect('catalogo:lista_productos')

    zonas = Zona.objects.all()

    if request.method == 'POST':
        zona_id = request.POST.get('zona')
        direccion = request.POST.get('direccion', '').strip()

        if not zona_id or not direccion:
            messages.error(request, "Debes seleccionar una zona e indicar tu dirección.")
            return render(request, 'ventas/checkout.html', {'carrito': carrito, 'zonas': zonas})

        zona = get_object_or_404(Zona, id=zona_id)

        with transaction.atomic():
            pedido = Pedido.objects.create(
                cliente=request.user,
                zona=zona,
                direccion_entrega=direccion,
            )

            for item in carrito:
                producto = item['producto']

                if item['cantidad'] > producto.stock:
                    messages.error(
                        request,
                        f"Stock insuficiente para {producto.nombre}. Pedido cancelado."
                    )
                    transaction.set_rollback(True)
                    return redirect('ventas:ver_carrito')

                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=item['cantidad'],
                    precio_unitario=item['precio'],
                )
                producto.stock -= item['cantidad']
                producto.save(update_fields=['stock'])

            pedido.calcular_total()
            carrito.vaciar()

        messages.success(request, f"Pedido {pedido.numero_orden} creado con éxito.")
        return redirect('pagos:procesar', pedido_id=pedido.id)

    return render(request, 'ventas/checkout.html', {'carrito': carrito, 'zonas': zonas})