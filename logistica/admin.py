from django.contrib import admin

from logistica.models import Zona, Entrega


@admin.register(Entrega)
class EntregaAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'repartidor', 'zona', 'estado', 'fecha_estimada')
    list_filter = ('estado', 'zona')

admin.site.register(Zona)