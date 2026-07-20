from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from usuarios.forms import RegistroClienteForm
from usuarios.models import PerfilCliente, Usuario, Notificacion


# Create your views here.
class RegistroClienteView(CreateView):
    form_class = RegistroClienteForm
    template_name = 'usuarios/registro.html'
    success_url = reverse_lazy('usuarios:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        PerfilCliente.objects.create(usuario=self.object)
        return response

@login_required
def redirigir_por_rol(request):
    """Vista intermedia: decide a dónde va cada usuario tras el login."""
    rol = request.user.rol
    rutas = {
        Usuario.Rol.CLIENTE: 'catalogo:lista_productos',
        Usuario.Rol.ADMIN: 'reportes:dashboard',
        Usuario.Rol.EMPLEADO: 'reportes:dashboard',
        Usuario.Rol.REPARTIDOR: 'logistica:mis_entregas',
        Usuario.Rol.SOPORTE: 'soporte:lista_tickets',
    }
    return redirect(rutas.get(rol, 'catalogo:lista_productos'))


@login_required
def ver_notificaciones(request):
    notificaciones = Notificacion.objects.filter(usuario=request.user)[:20]
    Notificacion.objects.filter(usuario=request.user, leida=False).update(leida=True)
    return render(request, 'usuarios/notificaciones.html', {'notificaciones': notificaciones})