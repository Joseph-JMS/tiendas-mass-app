from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, F
from django.shortcuts import render
from django.utils import timezone
from django.db import models

from usuarios.decorators import requiere_rol
from usuarios.models import Usuario, PerfilRepartidor
from catalogo.models import Producto
from ventas.models import Pedido, Venta, DetallePedido
from logistica.models import Entrega



# Create your views here.
@login_required
@requiere_rol(Usuario.Rol.ADMIN, Usuario.Rol.EMPLEADO)
def dashboard(request):
    hoy = timezone.now().date()

    # KPIs del día (RF22)
    ventas_hoy = Venta.objects.filter(fecha_venta__date=hoy)
    ingresos_hoy = ventas_hoy.aggregate(total=Sum('total_con_igv'))['total'] or 0
    cantidad_ventas_hoy = ventas_hoy.count()

    pedidos_pendientes = Pedido.objects.filter(
        estado__in=[Pedido.Estado.PENDIENTE, Pedido.Estado.CONFIRMADO, Pedido.Estado.EN_PREPARACION]
    ).count()

    stock_critico = Producto.objects.filter(stock__lte=F('stock_minimo'), activo=True)

    repartidores_activos = PerfilRepartidor.objects.filter(
        estado=PerfilRepartidor.Estado.EN_RUTA
    ).count()

    # Productos más vendidos (RF21)
    productos_top = (
        DetallePedido.objects
        .values('producto__nombre')
        .annotate(total_vendido=Sum('cantidad'))
        .order_by('-total_vendido')[:5]
    )

    return render(request, 'reportes/dashboard.html', {
        'ingresos_hoy': ingresos_hoy,
        'cantidad_ventas_hoy': cantidad_ventas_hoy,
        'pedidos_pendientes': pedidos_pendientes,
        'stock_critico': stock_critico,
        'repartidores_activos': repartidores_activos,
        'productos_top': productos_top,
    })


@login_required
@requiere_rol(Usuario.Rol.ADMIN, Usuario.Rol.EMPLEADO)
def reporte_repartidores(request):
    # RF23: desempeño de repartidores
    repartidores = PerfilRepartidor.objects.annotate(
        entregas_completadas=Count(
            'entregas', filter=models.Q(entregas__estado=Entrega.Estado.ENTREGADO)
        ),
        entregas_fallidas=Count(
            'entregas', filter=models.Q(entregas__estado=Entrega.Estado.FALLIDA)
        ),
    ).select_related('empleado__usuario')

    return render(request, 'reportes/repartidores.html', {'repartidores': repartidores})