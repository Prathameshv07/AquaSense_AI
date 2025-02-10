from django import forms
from .models import IoTInput

class IoTInputForm(forms.ModelForm):
    class Meta:
        model = IoTInput
        fields = ['temperature', 'pH', 'conductivity', 'dissolved_oxygen']
        widgets = {
            'temperature': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Temperature'}),
            'pH': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter pH'}),
            'conductivity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Conductivity'}),
            'dissolved_oxygen': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Dissolved Oxygen'}),
        }
