from django.urls import path

from logistica import views

app_name = 'logistica'

urlpatterns = [
    path('mis-entregas/', views.mis_entregas, name='mis_entregas'),
    path('entregas/<int:entrega_id>/actualizar/', views.actualizar_estado_entrega, name='actualizar_estado'),
]