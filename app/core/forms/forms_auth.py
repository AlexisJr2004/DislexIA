from django import forms
from app.core.models import Profesional
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm

class ProfesionalRegistrationForm(UserCreationForm):
    """Formulario para registro de nuevos profesionales"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    nombres = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all',
            'placeholder': 'Tus nombres'
        })
    )
    apellidos = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all',
            'placeholder': 'Tus apellidos'
        })
    )
    especialidad = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all',
            'placeholder': 'Ej: Neuropsicólogo, Psicólogo Educativo'
        })
    )
    numero_licencia = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all',
            'placeholder': 'Número de licencia profesional (opcional)'
        })
    )
    imagen = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'hidden',
            'accept': 'image/*',
            'id': 'imagen-input'
        }),
        label='Imagen de perfil',
        help_text='Formatos aceptados: JPG, PNG, GIF (Máx. 2MB)'
    )
    
    class Meta:
        model = Profesional
        fields = ['username', 'email', 'nombres', 'apellidos', 'especialidad', 'numero_licencia', 'imagen', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar campos heredados
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all',
            'placeholder': 'Nombre de usuario'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all',
            'placeholder': 'Confirmar contraseña'
        })
        
        # Personalizar etiquetas
        self.fields['username'].label = 'Nombre de usuario'
        self.fields['email'].label = 'Correo electrónico'
        self.fields['nombres'].label = 'Nombres'
        self.fields['apellidos'].label = 'Apellidos'
        self.fields['especialidad'].label = 'Especialidad'
        self.fields['numero_licencia'].label = 'Número de licencia'
        self.fields['imagen'].label = 'Imagen de perfil (opcional)'
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar contraseña'
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.nombres = self.cleaned_data['nombres']
        user.apellidos = self.cleaned_data['apellidos']
        user.especialidad = self.cleaned_data['especialidad']
        user.numero_licencia = self.cleaned_data.get('numero_licencia', '')
        
        # Manejar la imagen si fue cargada
        if self.cleaned_data.get('imagen'):
            user.imagen = self.cleaned_data['imagen']
        
        if commit:
            user.save()
        return user

class ProfesionalLoginForm(AuthenticationForm):
    """Formulario para login de profesionales"""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all',
            'placeholder': 'Nombre de usuario',
            'autofocus': True
        }),
        label='Nombre de usuario'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all',
            'placeholder': 'Contraseña'
        }),
        label='Contraseña'
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-purple-600 bg-gray-100 border-gray-300 rounded focus:ring-purple-500 focus:ring-2'
        }),
        label='Recordarme'
    )

class ProfesionalPasswordResetForm(PasswordResetForm):
    """Formulario para solicitar recuperación de contraseña"""
    
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all',
            'placeholder': 'correo@ejemplo.com',
            'autofocus': True
        }),
        label='Correo electrónico'
    )

class ProfesionalSetPasswordForm(SetPasswordForm):
    """Formulario para establecer nueva contraseña"""
    
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all',
            'placeholder': 'Nueva contraseña',
            'autofocus': True
        }),
        label='Nueva contraseña'
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all',
            'placeholder': 'Confirmar nueva contraseña'
        }),
        label='Confirmar contraseña'
    )
