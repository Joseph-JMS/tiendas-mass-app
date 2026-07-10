from django.contrib import admin

from pagos.models import Pago, Comprobante


# Register your models here.
@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'metodo', 'estado', 'monto', 'fecha_pago')
    list_filter = ('metodo', 'estado')


admin.site.register(Comprobante)