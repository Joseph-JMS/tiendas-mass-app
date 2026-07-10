from django.db import models

from ventas.models import Pedido


# Create your models here.
class Pago(models.Model):
    class Metodo(models.TextChoices):
        TARJETA = 'tarjeta', 'Tarjeta Visa/MasterCard'
        YAPE = 'yape', 'Yape'
        PLIN = 'plin', 'Plin'
        TRANSFERENCIA = 'transferencia', 'Transferencia bancaria'
        CONTRA_ENTREGA = 'contra_entrega', 'Pago contra entrega'

    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        CONFIRMADO = 'confirmado', 'Confirmado'
        RECHAZADO = 'rechazado', 'Rechazado'
        REEMBOLSADO = 'reembolsado', 'Reembolsado'

    pedido = models.OneToOneField(
        Pedido, on_delete=models.PROTECT, related_name='pago'
    )
    metodo = models.CharField(max_length=20, choices=Metodo.choices)
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.PENDIENTE
    )
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    referencia_transaccion = models.CharField(max_length=100, blank=True)
    fecha_pago = models.DateTimeField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pago {self.get_metodo_display()} - {self.pedido.numero_orden}"

    def confirmar(self, referencia=""):
        from django.utils import timezone
        self.estado = self.Estado.CONFIRMADO
        self.referencia_transaccion = referencia
        self.fecha_pago = timezone.now()
        self.save()


class Comprobante(models.Model):
    class Tipo(models.TextChoices):
        BOLETA = 'boleta', 'Boleta'
        FACTURA = 'factura', 'Factura'

    pago = models.OneToOneField(
        Pago, on_delete=models.PROTECT, related_name='comprobante'
    )
    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    serie = models.CharField(max_length=10)
    numero = models.CharField(max_length=20)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    igv = models.DecimalField(max_digits=8, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    archivo_pdf = models.FileField(upload_to='comprobantes/', null=True, blank=True)
    fecha_emision = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('serie', 'numero')

    def __str__(self):
        return f"{self.get_tipo_display()} {self.serie}-{self.numero}"

    @staticmethod
    def calcular_igv(subtotal):
        """IGV Perú = 18%"""
        from decimal import Decimal
        igv = subtotal * Decimal('0.18')
        return round(igv, 2)