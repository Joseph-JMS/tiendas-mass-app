import logging
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from catalogo.forms import ProductoForm
from catalogo.models import Producto, Categoria
from usuarios.decorators import requiere_rol
from usuarios.models import Usuario

logger = logging.getLogger(__name__)

def lista_productos(request):
    categoria_id = request.GET.get('categoria')
    busqueda = request.GET.get('q', '')
    orden = request.GET.get('orden', 'nombre')

    productos = Producto.objects.filter(activo=True)

    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    if busqueda:
        productos = productos.filter(nombre__icontains=busqueda)

    if orden in ['nombre', '-nombre', 'precio', '-precio']:
        productos = productos.order_by(orden)

    categorias = Categoria.objects.all()

    return render(request, 'catalogo/lista_productos.html', {
        'productos': productos,
        'categorias': categorias,
        'busqueda': busqueda,
        'categoria_id': categoria_id,
        'orden': orden,
    })


@login_required
@requiere_rol(Usuario.Rol.ADMIN, Usuario.Rol.EMPLEADO)
def panel_productos(request):
    productos = Producto.objects.select_related('categoria').all()

    stock_bajo = productos.filter(stock__lte=5)  # ajustamos con F() más abajo
    proximos_vencer = productos.filter(
        fecha_vencimiento__isnull=False,
        fecha_vencimiento__lte=timezone.now().date() + timedelta(days=7)
    )

    if stock_bajo.exists():
        logger.warning(
            f"Panel de productos: {stock_bajo.count()} producto(s) con stock bajo "
            f"(revisado por {request.user.username})"
        )

    return render(request, 'catalogo/panel_productos.html', {
        'productos': productos,
        'stock_bajo': stock_bajo,
        'proximos_vencer': proximos_vencer,
    })


@login_required
@requiere_rol(Usuario.Rol.ADMIN, Usuario.Rol.EMPLEADO)
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save()
            logger.info(
                f"Producto creado: '{producto.nombre}' (id={producto.id}) "
                f"por {request.user.username}"
            )
            messages.success(request, "Producto creado con éxito.")
            return redirect('catalogo:panel_productos')
    else:
        form = ProductoForm()
    return render(request, 'catalogo/form_producto.html', {'form': form, 'accion': 'Crear'})


@login_required
@requiere_rol(Usuario.Rol.ADMIN, Usuario.Rol.EMPLEADO)
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            logger.info(
                f"Producto editado: '{producto.nombre}' (id={producto.id}) "
                f"por {request.user.username}"
            )
            messages.success(request, "Producto actualizado.")
            return redirect('catalogo:panel_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'catalogo/form_producto.html', {'form': form, 'accion': 'Editar'})


@login_required
@requiere_rol(Usuario.Rol.ADMIN, Usuario.Rol.EMPLEADO)
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        producto.activo = False  # borrado lógico, no físico
        producto.save(update_fields=['activo'])
        logger.warning(
            f"Producto desactivado: '{producto.nombre}' (id={producto.id}) "
            f"por {request.user.username}"
        )
        messages.success(request, "Producto desactivado.")
    return redirect('catalogo:panel_productos')