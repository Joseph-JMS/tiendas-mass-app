import json
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, F
from django.db.models.functions import TruncDate, ExtractHour
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


@login_required
@requiere_rol(Usuario.Rol.ADMIN, Usuario.Rol.EMPLEADO)
def reportes_graficos(request):
    dias = int(request.GET.get('dias', 7))
    desde = timezone.now() - timedelta(days=dias)

    # 1. Ventas por día
    ventas_por_dia = (
        Venta.objects.filter(fecha_venta__gte=desde)
        .annotate(dia=TruncDate('fecha_venta'))
        .values('dia')
        .annotate(total=Sum('total_con_igv'), cantidad=Count('id'))
        .order_by('dia')
    )
    labels_dias = [v['dia'].strftime('%d/%m') for v in ventas_por_dia]
    datos_ingresos = [float(v['total']) for v in ventas_por_dia]
    datos_cantidad = [v['cantidad'] for v in ventas_por_dia]

    # 2. Top 5 productos más vendidos
    top_productos = (
        DetallePedido.objects
        .filter(pedido__fecha_creacion__gte=desde)
        .values('producto__nombre')
        .annotate(total_vendido=Sum('cantidad'))
        .order_by('-total_vendido')[:5]
    )
    labels_productos = [p['producto__nombre'] for p in top_productos]
    datos_productos = [p['total_vendido'] for p in top_productos]

    # 3. Ventas por horario (RF21)
    ventas_por_hora = (
        Venta.objects.filter(fecha_venta__gte=desde)
        .annotate(hora=ExtractHour('fecha_venta'))
        .values('hora')
        .annotate(cantidad=Count('id'))
        .order_by('hora')
    )
    horas_dict = {h: 0 for h in range(24)}
    for v in ventas_por_hora:
        horas_dict[v['hora']] = v['cantidad']
    labels_horas = [f"{h}:00" for h in range(24)]
    datos_horas = list(horas_dict.values())

    # 4. Distribución de pedidos por estado
    pedidos_por_estado = (
        Pedido.objects.filter(fecha_creacion__gte=desde)
        .values('estado')
        .annotate(cantidad=Count('id'))
    )
    estados_dict = dict(Pedido.Estado.choices)
    labels_estados = [estados_dict.get(p['estado'], p['estado']) for p in pedidos_por_estado]
    datos_estados = [p['cantidad'] for p in pedidos_por_estado]

    # 5. Desempeño de repartidores
    repartidores = PerfilRepartidor.objects.annotate(
        completadas=Count('entregas', filter=models.Q(entregas__estado=Entrega.Estado.ENTREGADO)),
        fallidas=Count('entregas', filter=models.Q(entregas__estado=Entrega.Estado.FALLIDA)),
    ).select_related('empleado__usuario')

    labels_repartidores = [r.empleado.usuario.username for r in repartidores]
    datos_completadas = [r.completadas for r in repartidores]
    datos_fallidas = [r.fallidas for r in repartidores]

    contexto = {
        'dias': dias,
        'labels_dias': json.dumps(labels_dias),
        'datos_ingresos': json.dumps(datos_ingresos),
        'datos_cantidad': json.dumps(datos_cantidad),
        'labels_productos': json.dumps(labels_productos),
        'datos_productos': json.dumps(datos_productos),
        'labels_horas': json.dumps(labels_horas),
        'datos_horas': json.dumps(datos_horas),
        'labels_estados': json.dumps(labels_estados),
        'datos_estados': json.dumps(datos_estados),
        'labels_repartidores': json.dumps(labels_repartidores),
        'datos_completadas': json.dumps(datos_completadas),
        'datos_fallidas': json.dumps(datos_fallidas),
    }
    return render(request, 'reportes/graficos.html', contexto)