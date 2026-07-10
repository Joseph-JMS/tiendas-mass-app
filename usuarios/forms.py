from django.contrib.auth.forms import UserCreationForm
from django import forms

from usuarios.models import Usuario


class RegistroClienteForm(UserCreationForm):
    email = forms.EmailField(required=True)
    dni = forms.CharField(max_length=8, min_length=8, required=True)
    telefono = forms.CharField(max_length=15, required=True)

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'dni', 'telefono', 'password1', 'password2']

    def clean_dni(self):
        dni = self.cleaned_data['dni']
        if not dni.isdigit():
            raise forms.ValidationError("El DNI debe contener solo números.")
        if Usuario.objects.filter(dni=dni).exists():
            raise forms.ValidationError("Este DNI ya está registrado.")
        return dni

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.rol = Usuario.Rol.CLIENTE
        usuario.dni = self.cleaned_data['dni']
        usuario.telefono = self.cleaned_data['telefono']
        if commit:
            usuario.save()
        return usuario