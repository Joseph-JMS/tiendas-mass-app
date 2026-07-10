from django.urls import path

from pagos import views

app_name = 'pagos'

urlpatterns = [
    path('procesar/<int:pedido_id>/', views.procesar_pago, name='procesar'),
    path('confirmacion/<int:pedido_id>/', views.confirmacion_pago, name='confirmacion'),
]