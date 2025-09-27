from django import forms
from .models import Previoustests


class PrevioustestsForm(forms.ModelForm):
    class Meta:
        model = Previoustests
        fields = [
            'english_degree', 'it_degree', 'information_degree', 
            'nafsy_degree', 'security_degree'
        ]
        widgets = {
            'english_degree': forms.NumberInput(attrs={'class': 'form-control'}),
            'it_degree': forms.NumberInput(attrs={'class': 'form-control'}),
            'information_degree': forms.NumberInput(attrs={'class': 'form-control'}),
            'nafsy_degree': forms.NumberInput(attrs={'class': 'form-control'}),
            'security_degree': forms.NumberInput(attrs={'class': 'form-control'}),
        }