from django.urls import path

from reportes import views

app_name = 'reportes'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('repartidores/', views.reporte_repartidores, name='reporte_repartidores'),
    path('graficos/', views.reportes_graficos, name='graficos'),
]