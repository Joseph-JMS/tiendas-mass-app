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
            'categoria': forms.Select(attrs={'class': 'select select-bordered bg-base-200 w-full'}),
            'nombre': forms.TextInput(attrs={'class': 'input input-bordered bg-base-200 w-full'}),
            'descripcion': forms.Textarea(attrs={'class': 'textarea textarea-bordered bg-base-200 w-full', 'rows': 3}),
            'precio': forms.NumberInput(attrs={'class': 'input input-bordered bg-base-200 w-full'}),
            'stock': forms.NumberInput(attrs={'class': 'input input-bordered bg-base-200 w-full'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'input input-bordered bg-base-200 w-full'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'input input-bordered bg-base-200 w-full', 'type': 'date'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'file-input file-input-bordered bg-base-200 w-full'}),
            'activo': forms.CheckboxInput(attrs={'class': 'checkbox checkbox-primary'}),
        }