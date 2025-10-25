from django import forms
from app.core.models import ValidacionProfesional

class ValidacionProfesionalForm(forms.ModelForm):
    """Formulario para la validación profesional"""
    
    class Meta:
        model = ValidacionProfesional
        fields = [
            'riesgo_confirmado',
            'indice_ajustado',
            'diagnostico_final',
            'notas_clinicas',
            'plan_tratamiento',
            'requiere_seguimiento',
        ]
        widgets = {
            'riesgo_confirmado': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-green-600',
            }),
            'indice_ajustado': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-purple-500',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'placeholder': 'Ej: 45.50'
            }),
            'diagnostico_final': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-purple-500',
                'rows': 3,
                'placeholder': 'Diagnóstico final del profesional'
            }),
            'notas_clinicas': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-purple-500',
                'rows': 2,
                'placeholder': 'Notas clínicas adicionales (opcional)'
            }),
            'plan_tratamiento': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-purple-500',
                'rows': 2,
                'placeholder': 'Plan de tratamiento sugerido (opcional)'
            }),
            'requiere_seguimiento': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-purple-600',
            }),
        }
        labels = {
            'riesgo_confirmado': '¿Confirma el riesgo detectado por IA?',
            'indice_ajustado': 'Índice Ajustado',
            'diagnostico_final': 'Diagnóstico Final',
            'notas_clinicas': 'Notas Clínicas',
            'plan_tratamiento': 'Plan de Tratamiento',
            'requiere_seguimiento': '¿Requiere Seguimiento?',
        }