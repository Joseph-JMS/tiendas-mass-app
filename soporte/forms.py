from django import forms

from soporte.models import Ticket


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['categoria', 'asunto', 'descripcion']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'select select-bordered bg-base-200 w-full'}),
            'asunto': forms.TextInput(attrs={'class': 'input input-bordered bg-base-200 w-full'}),
            'descripcion': forms.Textarea(attrs={'class': 'textarea textarea-bordered bg-base-200 w-full', 'rows': 4}),
        }