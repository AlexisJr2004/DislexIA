import logging
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.shortcuts import redirect
from django.db.utils import OperationalError
from django.utils import timezone
from app.core.forms.forms_auth import ProfesionalLoginForm, ProfesionalRegistrationForm, ProfesionalPasswordResetForm, ProfesionalSetPasswordForm
from app.core.models import LoginAttempt

logger = logging.getLogger(__name__)

class ProfesionalLoginView(LoginView):
    """Vista personalizada para el login de profesionales"""
    form_class = ProfesionalLoginForm
    template_name = 'auth/login.html'
    redirect_authenticated_user = True
    
    def _get_client_ip(self, request):
        """Obtener la IP real del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip
    
    def get(self, request, *args, **kwargs):
        """Manejar GET request y verificar cookies"""
        # Verificar si viene de un logout exitoso
        if request.COOKIES.get('logout_message'):
            messages.info(request, '✅ Has cerrado sesión exitosamente.')
        
        # Verificar si viene de una eliminación de cuenta
        if request.COOKIES.get('account_deleted'):
            messages.warning(request, '⚠️ Tu cuenta ha sido eliminada permanentemente. Esperamos verte de nuevo pronto.')
        
        response = super().get(request, *args, **kwargs)
        
        # Eliminar las cookies si existen
        if request.COOKIES.get('logout_message'):
            response.delete_cookie('logout_message')
        if request.COOKIES.get('account_deleted'):
            response.delete_cookie('account_deleted')
        
        return response
    
    def get_success_url(self):
        return reverse_lazy('dashboard')
    
    def form_valid(self, form):
        """Login exitoso - limpiar intentos fallidos y establecer sesión"""
        username = form.cleaned_data.get('username')
        
        # Registrar intento exitoso
        LoginAttempt.objects.create(
            username=username,
            ip_address=self._get_client_ip(self.request),
            exitoso=True,
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')[:500]
        )
        
        # Limpiar intentos fallidos antiguos
        LoginAttempt.limpiar_intentos_antiguos(username)
        
        # Configurar duración de sesión
        remember_me = form.cleaned_data.get('remember_me')
        if not remember_me:
            # Si no marca "recordarme", la sesión expira al cerrar el navegador
            self.request.session.set_expiry(0)
        else:
            # Mantener sesión por 2 semanas
            self.request.session.set_expiry(1209600)
        
        messages.success(self.request, f'¡Bienvenido de nuevo, {form.get_user().nombre_completo}!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Login fallido - registrar intento y verificar bloqueo"""
        username = form.cleaned_data.get('username', '')
        
        # Verificar si la cuenta está bloqueada ANTES de procesar
        if username and LoginAttempt.esta_bloqueado(username):
            tiempo_restante = LoginAttempt.obtener_tiempo_restante_bloqueo(username)
            messages.error(
                self.request,
                f'🔒 Tu cuenta ha sido bloqueada temporalmente por múltiples intentos fallidos. '
                f'Intenta nuevamente en {tiempo_restante} minutos.'
            )
            logger.warning(f"Intento de login en cuenta bloqueada: {username} desde IP {self._get_client_ip(self.request)}")
            return super().form_invalid(form)
        
        # Registrar intento fallido
        if username:
            LoginAttempt.objects.create(
                username=username,
                ip_address=self._get_client_ip(self.request),
                exitoso=False,
                user_agent=self.request.META.get('HTTP_USER_AGENT', '')[:500]
            )
            
            # Verificar cuántos intentos lleva
            intentos = LoginAttempt.obtener_intentos_recientes(username)
            intentos_restantes = 5 - intentos
            
            if intentos >= 5:
                # Cuenta bloqueada
                messages.error(
                    self.request,
                    f'🔒 Has excedido el número máximo de intentos de login. '
                    f'Tu cuenta ha sido bloqueada temporalmente por 30 minutos.'
                )
                logger.warning(f"Cuenta bloqueada por intentos fallidos: {username} desde IP {self._get_client_ip(self.request)}")
            elif intentos >= 3:
                # Advertencia
                messages.warning(
                    self.request,
                    f'⚠️ Usuario o contraseña incorrectos. Te quedan {intentos_restantes} intentos antes de que tu cuenta sea bloqueada.'
                )
            else:
                # Error normal
                messages.error(
                    self.request,
                    'Usuario o contraseña incorrectos. Por favor, intenta de nuevo.'
                )
        else:
            messages.error(
                self.request,
                'Usuario o contraseña incorrectos. Por favor, intenta de nuevo.'
            )
        
        return super().form_invalid(form)

class ProfesionalRegisterView(CreateView):
    """Vista para registro de nuevos profesionales"""
    form_class = ProfesionalRegistrationForm
    template_name = 'auth/register.html'
    success_url = reverse_lazy('dashboard')
    
    def dispatch(self, request, *args, **kwargs):
        # Si ya está autenticado, redirigir al dashboard
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        # Guardar el usuario con el consentimiento GDPR
        # IMPORTANTE: commit=True para que se ejecute el código de ConsentimientoGDPR
        self.object = form.save(commit=True, request=self.request)
        
        # Autenticar automáticamente después del registro
        login(self.request, self.object)
        messages.success(
            self.request, 
            f'¡Registro exitoso! Bienvenido a DislexIA, {self.object.nombre_completo}.'
        )
        
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error en el registro. Por favor, verifica los datos ingresados.')
        return super().form_invalid(form)

    def post(self, request, *args, **kwargs):
        """Sobrescribimos post para capturar errores de BD (p.ej. columna faltante) y evitar 500s.

        Si ocurre un OperationalError, se registra y se muestra un mensaje amigable al usuario
        indicando acción recomendada (revisar migraciones o la estructura del modelo `Profesional`).
        """
        try:
            return super().post(request, *args, **kwargs)
        except OperationalError as e:
            # Mensaje claro para el usuario
            messages.error(request, (
                'Error del servidor al procesar el registro: falta una columna en la base de datos. '
                'Esto suele ocurrir cuando el modelo y la base de datos están desincronizados (migrations pendientes) '
                'o falta una migración. Por favor, ejecuta `python manage.py migrate` o restaura el esquema correcto.'
            ))
            # Log completo para depuración
            logger.exception('OperationalError en ProfesionalRegisterView durante registro: %s', e)
            # Redirigir al formulario de registro para que el usuario no vea un 500
            return redirect('core:register')
        except Exception as e:
            # Capturar otros errores inesperados para evitar caída y registrar
            logger.exception('Error inesperado en ProfesionalRegisterView: %s', e)
            messages.error(request, 'Ocurrió un error inesperado. Por favor contacta al administrador.')
            return redirect('core:register')

class ProfesionalLogoutView(LogoutView):
    """Vista para cerrar sesión"""
    template_name = None  # No usar template, solo redirigir
    http_method_names = ['get', 'post', 'options']
    
    def get_next_page(self):
        """Obtener la página a la que redirigir después del logout"""
        return reverse_lazy('core:login')
    
    def dispatch(self, request, *args, **kwargs):
        """Procesar el logout y agregar mensaje"""
        response = super().dispatch(request, *args, **kwargs)
        # Asegurarse de cerrar la sesión correctamente
        request.session.flush()
        # Agregar un mensaje como cookie temporal que se mostrará en el login
        if isinstance(response, redirect.__class__) or hasattr(response, 'url'):
            response.set_cookie('logout_message', '1', max_age=5)
        return response

class ProfesionalPasswordResetView(PasswordResetView):
    """Vista para solicitar recuperación de contraseña"""
    form_class = ProfesionalPasswordResetForm
    template_name = 'auth/password_reset_form.html'
    email_template_name = 'auth/password_reset_email.html'
    html_email_template_name = 'auth/password_reset_email.html'
    subject_template_name = 'auth/password_reset_subject.txt'
    success_url = reverse_lazy('core:password_reset_done')
    
    def form_valid(self, form):
        messages.success(
            self.request, 
            'Si el correo electrónico existe en nuestro sistema, recibirás un enlace de recuperación.'
        )
        return super().form_valid(form)

class ProfesionalPasswordResetDoneView(PasswordResetDoneView):
    """Vista de confirmación después de solicitar recuperación"""
    template_name = 'auth/password_reset_done.html'

class ProfesionalPasswordResetConfirmView(PasswordResetConfirmView):
    """Vista para establecer nueva contraseña usando el token"""
    form_class = ProfesionalSetPasswordForm
    template_name = 'auth/password_reset_confirm.html'
    success_url = reverse_lazy('core:password_reset_complete')
    
    def form_valid(self, form):
        messages.success(
            self.request, 
            '¡Contraseña cambiada exitosamente! Ya puedes iniciar sesión con tu nueva contraseña.'
        )
        return super().form_valid(form)

class ProfesionalPasswordResetCompleteView(PasswordResetCompleteView):
    """Vista final después de cambiar la contraseña"""
    template_name = 'auth/password_reset_complete.html'
