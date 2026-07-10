from django.contrib import admin

from soporte.models import Ticket, LogError


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'categoria', 'estado', 'prioridad', 'fecha_creacion')
    list_filter = ('estado', 'categoria', 'prioridad')


@admin.register(LogError)
class LogErrorAdmin(admin.ModelAdmin):
    list_display = ('nivel', 'modulo', 'fecha')
    list_filter = ('nivel', 'modulo')
    readonly_fields = ('fecha',)