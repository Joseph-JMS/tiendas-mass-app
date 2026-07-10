from django.contrib import admin

from ventas.models import Venta, DetallePedido, Pedido


# Register your models here.
class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('numero_orden', 'cliente', 'estado', 'total', 'fecha_creacion')
    list_filter = ('estado',)
    inlines = [DetallePedidoInline]


admin.site.register(Venta)