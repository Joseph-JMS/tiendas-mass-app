from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    class Rol(models.TextChoices):
        CLIENTE = 'cliente', 'Cliente'
        EMPLEADO = 'empleado', 'Empleado'
        REPARTIDOR = 'repartidor', 'Repartidor'
        SOPORTE = 'soporte', 'Soporte Técnico'
        ADMIN = 'admin', 'Administrador'

    rol = models.CharField(max_length=20, choices=Rol.choices)
    telefono = models.CharField(max_length=15, blank=True)
    dni = models.CharField(max_length=8, blank=True, unique=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"

class PerfilCliente(models.Model):
    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, related_name='perfil_cliente'
    )
    direccion_principal = models.CharField(max_length=255, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cliente: {self.usuario.username}"

class PerfilEmpleado(models.Model):
    class Cargo(models.TextChoices):
        ADMIN_MINIMARKET = 'admin_minimarket', 'Administrador del Minimarket'
        SUPERVISOR_VENTAS = 'supervisor_ventas', 'Supervisor de Ventas'
        ENCARGADO_ALMACEN = 'encargado_almacen', 'Encargado de Almacén'
        COORDINADOR_ENTREGAS = 'coordinador_entregas', 'Coordinador de Entregas'
        CAJERO = 'cajero', 'Cajero/Atención al Cliente'

    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, related_name='perfil_empleado'
    )
    cargo = models.CharField(max_length=30, choices=Cargo.choices)
    fecha_ingreso = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.get_cargo_display()}"

class PerfilRepartidor(models.Model):
    class Estado(models.TextChoices):
        DISPONIBLE = 'disponible', 'Disponible'
        EN_RUTA = 'en_ruta', 'En ruta'
        DESCONECTADO = 'desconectado', 'Desconectado'

    empleado = models.OneToOneField(
        PerfilEmpleado, on_delete=models.CASCADE, related_name='perfil_repartidor'
    )
    zona = models.ForeignKey(
        'logistica.Zona', on_delete=models.SET_NULL, null=True, blank=True
    )
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.DESCONECTADO
    )

    def __str__(self):
        return f"Repartidor: {self.empleado.usuario.username}"


class Notificacion(models.Model):
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name='notificaciones'
    )
    mensaje = models.CharField(max_length=255)
    url = models.CharField(max_length=255, blank=True)
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.usuario.username}: {self.mensaje[:40]}"

def notificar(usuario, mensaje, url=""):
    Notificacion.objects.create(usuario=usuario, mensaje=mensaje, url=url)