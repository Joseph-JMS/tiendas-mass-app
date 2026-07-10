from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from usuarios.models import Usuario, PerfilCliente, PerfilEmpleado, PerfilRepartidor


# Register your models here.
@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Datos Tienda Mass', {'fields': ('rol', 'telefono', 'dni')}),
    )
    list_display = ('username', 'email', 'rol', 'is_staff')

admin.site.register(PerfilCliente)
admin.site.register(PerfilEmpleado)
admin.site.register(PerfilRepartidor)