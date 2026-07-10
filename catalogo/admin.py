from django.contrib import admin

from catalogo.models import Producto, Categoria


# Register your models here.
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'stock', 'stock_bajo', 'activo')
    list_filter = ('categoria', 'activo')
    search_fields = ('nombre',)

admin.site.register(Categoria)