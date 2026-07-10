from decimal import Decimal

from catalogo.models import Producto


class Carrito:
    def __init__(self, request):
        self.session = request.session
        carrito = self.session.get('carrito')
        if not carrito:
            carrito = self.session['carrito'] = {}
        self.carrito = carrito

    def agregar(self, producto, cantidad=1):
        producto_id = str(producto.id)
        if producto_id not in self.carrito:
            self.carrito[producto_id] = {
                'cantidad': 0,
                'precio': str(producto.precio),
            }
        self.carrito[producto_id]['cantidad'] += cantidad
        self.guardar()

    def actualizar_cantidad(self, producto_id, cantidad):
        producto_id = str(producto_id)
        if producto_id in self.carrito:
            if cantidad <= 0:
                self.eliminar(producto_id)
            else:
                self.carrito[producto_id]['cantidad'] = cantidad
                self.guardar()

    def eliminar(self, producto_id):
        producto_id = str(producto_id)
        if producto_id in self.carrito:
            del self.carrito[producto_id]
            self.guardar()

    def guardar(self):
        self.session.modified = True

    def vaciar(self):
        self.session['carrito'] = {}
        self.guardar()

    def __iter__(self):
        producto_ids = self.carrito.keys()
        productos = Producto.objects.filter(id__in=producto_ids)
        productos_dict = {str(p.id): p for p in productos}

        for producto_id, datos in self.carrito.items():
            producto = productos_dict.get(producto_id)
            if not producto:
                continue
            precio = Decimal(datos['precio'])
            cantidad = datos['cantidad']
            yield {
                'producto': producto,
                'cantidad': cantidad,
                'precio': precio,
                'subtotal': precio * cantidad,
            }

    def __len__(self):
        return sum(item['cantidad'] for item in self.carrito.values())

    def total(self):
        return sum(
            Decimal(item['precio']) * item['cantidad']
            for item in self.carrito.values()
        )