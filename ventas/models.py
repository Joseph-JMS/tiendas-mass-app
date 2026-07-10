from django.conf import settings
from django.db import models

from catalogo.models import Producto


# Create your models here.
class Pedido(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        CONFIRMADO = 'confirmado', 'Confirmado'
        EN_PREPARACION = 'en_preparacion', 'En preparación'
        EN_CAMINO = 'en_camino', 'En camino'
        ENTREGADO = 'entregado', 'Entregado'
        CANCELADO = 'cancelado', 'Cancelado'

    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='pedidos'
    )
    numero_orden = models.CharField(max_length=20, unique=True, editable=False)
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.PENDIENTE
    )
    zona = models.ForeignKey(
        'logistica.Zona', on_delete=models.PROTECT, null=True, related_name='pedidos'
    )
    direccion_entrega = models.CharField(max_length=255, blank=True)
    subtotal_productos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    costo_envio = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pedido {self.numero_orden} - {self.cliente}"

    def save(self, *args, **kwargs):
        if not self.numero_orden:
            import uuid
            self.numero_orden = f"TM-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def calcular_total(self):
        subtotal = sum(d.subtotal for d in self.detalles.all())
        envio = self.zona.tarifa_envio if self.zona else 0
        self.subtotal_productos = subtotal
        self.costo_envio = envio
        self.total = subtotal + envio
        self.save(update_fields=['subtotal_productos', 'costo_envio', 'total'])
        return self.total


class DetallePedido(models.Model):
    pedido = models.ForeignKey(
        Pedido, on_delete=models.CASCADE, related_name='detalles'
    )
    producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT, related_name='detalles_pedido'
    )
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        unique_together = ('pedido', 'producto')

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario


class Venta(models.Model):
    pedido = models.OneToOneField(
        Pedido, on_delete=models.PROTECT, related_name='venta'
    )
    empleado = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='ventas_registradas'
    )
    igv = models.DecimalField(max_digits=8, decimal_places=2)
    total_con_igv = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_venta = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Venta de {self.pedido.numero_orden}"