from django import forms
from app.core.models import Profesional, Nino

class ProfesionalUpdateForm(forms.ModelForm):
    """Formulario para actualizar el perfil de profesionales"""
    
    class Meta:
        model = Profesional
        fields = ['nombres', 'apellidos', 'email', 'especialidad', 'numero_licencia', 'imagen']
        widgets = {
            'nombres': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-700 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-200',
                'placeholder': 'Tus nombres'
            }),
            'apellidos': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-700 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-200',
                'placeholder': 'Tus apellidos'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-700 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-200',
                'placeholder': 'correo@ejemplo.com'
            }),
            'especialidad': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-700 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-200',
                'placeholder': 'Ej: Neuropsicólogo, Psicólogo Educativo'
            }),
            'numero_licencia': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-700 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-200',
                'placeholder': 'Número de licencia profesional (opcional)'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*',
                'id': 'imagen-input-edit'
            })
        }
        labels = {
            'nombres': 'Nombres',
            'apellidos': 'Apellidos',
            'email': 'Correo electrónico',
            'especialidad': 'Especialidad',
            'numero_licencia': 'Número de licencia',
            'imagen': 'Imagen de perfil'
        }

class NinoForm(forms.ModelForm):
    """Formulario para crear y editar niños"""
    
    class Meta:
        model = Nino
        fields = ['nombres', 'apellidos', 'fecha_nacimiento', 'edad', 'genero', 
                  'idioma_nativo', 'imagen']
        
        widgets = {
            'nombres': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-700 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-200',
                'placeholder': 'Ej: Juan Carlos'
            }),
            'apellidos': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-700 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-200',
                'placeholder': 'Ej: García López'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-700 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-200'
            }),
            'edad': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-700 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-200',
                'min': '6',
                'max': '12',
                'placeholder': 'Entre 6 y 12 años'
            }),
            'genero': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-700 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-200'
            }),
            'idioma_nativo': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-700 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-200',
                'placeholder': 'Ej: Español'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*'
            })
        }
        
        labels = {
            'nombres': 'Nombres',
            'apellidos': 'Apellidos',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'edad': 'Edad',
            'genero': 'Género',
            'idioma_nativo': 'Idioma Nativo',
            'imagen': 'Imagen'
        }
    
    def clean_edad(self):
        """Validar que la edad esté entre 6 y 12 años"""
        edad = self.cleaned_data.get('edad')
        if edad and (edad < 6 or edad > 12):
            raise forms.ValidationError('La edad debe estar entre 6 y 12 años')
        return edad
    
    def clean_imagen(self):
        """Validar tamaño y tipo de imagen solo si es un archivo nuevo"""
        imagen = self.cleaned_data.get('imagen')
        
        # Si imagen es None o False, no hay archivo nuevo
        if not imagen:
            return imagen
        
        # Si es un ImageFieldFile (imagen existente), no validar
        # Solo validar si es un archivo nuevo (UploadedFile)
        if hasattr(imagen, 'content_type'):
            # Es un archivo nuevo subido
            # Validar tamaño (5MB máximo)
            if imagen.size > 5 * 1024 * 1024:
                raise forms.ValidationError('El archivo es demasiado grande. Máximo 5MB.')
            
            # Validar tipo de archivo
            if not imagen.content_type.startswith('image/'):
                raise forms.ValidationError('El archivo debe ser una imagen.')
        
        return imagen
