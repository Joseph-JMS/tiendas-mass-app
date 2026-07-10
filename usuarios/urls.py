from django.urls import path
from django.contrib.auth import views as auth_views

from usuarios import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='usuarios/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registro/', views.RegistroClienteView.as_view(), name='registro'),
    path('redirigir/', views.redirigir_por_rol, name='redirigir'),
]