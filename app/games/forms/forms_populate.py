from django import forms

class PopulateSessionsForm(forms.Form):
    RIESGO_CHOICES = [
        ('alto', 'Alto'),
        ('medio', 'Medio'),
        ('bajo', 'Bajo'),
    ]
    riesgo = forms.ChoiceField(
        choices=RIESGO_CHOICES,
        label='Nivel de riesgo',
        initial='medio',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all',
        })
    )