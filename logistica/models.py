from django.db import models

from usuarios.models import PerfilRepartidor
from ventas.models import Pedido


class Zona(models.Model):
    nombre = models.CharField(max_length=50)  # Cercado, Norte, Sur, Este
    tarifa_envio = models.DecimalField(max_digits=6, decimal_places=2)
    tiempo_estimado_min = models.PositiveIntegerField(help_text="Tiempo estimado en minutos")

    def __str__(self):
        return self.nombre

class Entrega(models.Model):
    class Estado(models.TextChoices):
        ASIGNADA = 'asignada', 'Asignada'
        PREPARADO = 'preparado', 'Preparado'
        EN_CAMINO = 'en_camino', 'En camino'
        ENTREGADO = 'entregado', 'Entregado'
        FALLIDA = 'fallida', 'Entrega fallida'

    class MotivoFallo(models.TextChoices):
        CLIENTE_AUSENTE = 'cliente_ausente', 'Cliente ausente'
        DIRECCION_INCORRECTA = 'direccion_incorrecta', 'Dirección incorrecta'
        OTRO = 'otro', 'Otro motivo'

    pedido = models.OneToOneField(
        Pedido, on_delete=models.PROTECT, related_name='entrega'
    )
    repartidor = models.ForeignKey(
        PerfilRepartidor, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='entregas'
    )
    zona = models.ForeignKey(Zona, on_delete=models.PROTECT, related_name='entregas')
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.ASIGNADA
    )
    direccion_entrega = models.CharField(max_length=255)
    motivo_fallo = models.CharField(
        max_length=30, choices=MotivoFallo.choices, blank=True
    )
    fecha_estimada = models.DateTimeField(null=True, blank=True)
    fecha_entrega_real = models.DateTimeField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Entrega de {self.pedido.numero_orden}"

    def marcar_entregado(self):
        from django.utils import timezone
        self.estado = self.Estado.ENTREGADO
        self.fecha_entrega_real = timezone.now()
        self.save()

    def reprogramar(self, motivo):
        self.estado = self.Estado.FALLIDA
        self.motivo_fallo = motivo
        self.save()