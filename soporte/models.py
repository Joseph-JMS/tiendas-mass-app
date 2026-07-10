from django.conf import settings
from django.db import models

class Ticket(models.Model):
    class Categoria(models.TextChoices):
        PEDIDO = 'pedido', 'Problema con pedido'
        PAGO = 'pago', 'Problema con pago'
        ENTREGA = 'entrega', 'Problema con entrega'
        CUENTA = 'cuenta', 'Problema con cuenta'
        OTRO = 'otro', 'Otro'

    class Estado(models.TextChoices):
        ABIERTO = 'abierto', 'Abierto'
        EN_PROCESO = 'en_proceso', 'En proceso'
        RESUELTO = 'resuelto', 'Resuelto'
        CERRADO = 'cerrado', 'Cerrado'

    class Prioridad(models.TextChoices):
        BAJA = 'baja', 'Baja'
        MEDIA = 'media', 'Media'
        ALTA = 'alta', 'Alta'

    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets_creados'
    )
    asignado_a = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='tickets_asignados'
    )
    categoria = models.CharField(max_length=20, choices=Categoria.choices)
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.ABIERTO
    )
    prioridad = models.CharField(
        max_length=10, choices=Prioridad.choices, default=Prioridad.MEDIA
    )
    asunto = models.CharField(max_length=150)
    descripcion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Ticket #{self.id} - {self.asunto}"


class LogError(models.Model):
    class Nivel(models.TextChoices):
        INFO = 'info', 'Información'
        WARNING = 'warning', 'Advertencia'
        ERROR = 'error', 'Error'
        CRITICAL = 'critical', 'Crítico'

    nivel = models.CharField(max_length=10, choices=Nivel.choices)
    modulo = models.CharField(max_length=50, help_text="App donde ocurrió (ventas, pagos, etc.)")
    mensaje = models.TextField()
    traceback = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"[{self.nivel.upper()}] {self.modulo} - {self.fecha}"