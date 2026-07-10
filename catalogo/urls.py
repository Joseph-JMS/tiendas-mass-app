from django.urls import path

from catalogo import views

app_name = 'catalogo'

urlpatterns = [
    path('', views.lista_productos, name='lista_productos'),
    path('admin/productos/', views.panel_productos, name='panel_productos'),
    path('admin/productos/crear/', views.crear_producto, name='crear_producto'),
    path('admin/productos/editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('admin/productos/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
]