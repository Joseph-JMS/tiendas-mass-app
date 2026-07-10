from django import forms

from catalogo.models import Producto


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'categoria', 'nombre', 'descripcion', 'precio',
            'stock', 'stock_minimo', 'fecha_vencimiento', 'imagen', 'activo'
        ]
        widgets = {
            'categoria': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'nombre': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'descripcion': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full'}),
            'precio': forms.NumberInput(attrs={'class': 'input input-bordered w-full'}),
            'stock': forms.NumberInput(attrs={'class': 'input input-bordered w-full'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'input input-bordered w-full'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'input input-bordered w-full', 'type': 'date'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
            'activo': forms.CheckboxInput(attrs={'class': 'checkbox'}),
        }