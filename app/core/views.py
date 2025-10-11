from django.views.generic import TemplateView, UpdateView, ListView
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404, render
from .forms import ProfesionalLoginForm, ProfesionalRegistrationForm, ProfesionalUpdateForm, ProfesionalPasswordResetForm, ProfesionalSetPasswordForm, NinoForm
from django.contrib.auth import login
from django.db.utils import OperationalError
import logging
from .models import Nino
from django.http import JsonResponse
from django.views import View

logger = logging.getLogger(__name__)


# ==================== VISTAS DE AUTENTICACIÓN ====================

class ProfesionalLoginView(LoginView):
    """Vista personalizada para el login de profesionales"""
    form_class = ProfesionalLoginForm
    template_name = 'auth/login.html'
    redirect_authenticated_user = True
    
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
        messages.error(self.request, 'Usuario o contraseña incorrectos. Por favor, intenta de nuevo.')
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
        response = super().form_valid(form)
        # Autenticar automáticamente después del registro
        login(self.request, self.object)
        messages.success(
            self.request, 
            f'¡Registro exitoso! Bienvenido a DislexIA, {self.object.nombre_completo}.'
        )
        return response
    
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


# ==================== VISTAS PROTEGIDAS ====================

@method_decorator(login_required, name='dispatch')
class CalendarView(TemplateView):
    template_name = 'calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Calendario - DislexIA',
            'active_section': 'calendar',
        })
        return context

@method_decorator(login_required, name='dispatch')
class DocumentsView(TemplateView):
    template_name = 'documents.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Recursos Digitales - DislexIA',
            'active_section': 'documents',
        })
        return context

@method_decorator(login_required, name='dispatch')
class SettingsView(TemplateView):
    template_name = 'settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Configuraciones - DislexIA',
            'active_section': 'settings',
        })
        return context

@method_decorator(login_required, name='dispatch')
class SupportView(TemplateView):
    template_name = 'support.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Soporte - DislexIA',
            'active_section': 'support',
        })
        return context

@method_decorator(login_required, name='dispatch')
class ProfileView(TemplateView):
    template_name = 'profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Perfil - DislexIA',
            'active_section': 'profile',
            'form': ProfesionalUpdateForm(instance=self.request.user)
        })
        return context


@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(UpdateView):
    """Vista para actualizar el perfil del profesional"""
    model = None  # Se establece dinámicamente
    form_class = ProfesionalUpdateForm
    success_url = reverse_lazy('core:profile')
    
    def get_object(self, queryset=None):
        # Retornar el usuario actual
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, '¡Perfil actualizado exitosamente!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al actualizar el perfil. Por favor, verifica los datos.')
        return redirect('core:profile')


@method_decorator(login_required, name='dispatch')
class DeleteAccountView(TemplateView):
    """Vista para eliminar la cuenta del usuario permanentemente"""
    
    def post(self, request, *args, **kwargs):
        """Procesar la eliminación de la cuenta"""
        user = request.user
        username = user.username
        
        try:
            # Cerrar sesión del usuario
            from django.contrib.auth import logout
            logout(request)
            
            # Eliminar la cuenta permanentemente
            user.delete()
            
            # Mensaje de confirmación (se guarda en cookie para mostrarlo después del redirect)
            messages.success(request, f'La cuenta de {username} ha sido eliminada permanentemente.')
            
            # Redirigir al login
            response = redirect('core:login')
            response.set_cookie('account_deleted', 'true', max_age=10)
            return response
            
        except Exception as e:
            messages.error(request, f'Error al eliminar la cuenta: {str(e)}')
            return redirect('core:settings')


# ==================== VISTAS DE RECUPERACIÓN DE CONTRASEÑA ====================

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


@method_decorator(login_required, name='dispatch')
class EditarNinoView(UpdateView):
    """Vista para editar los datos de un niño asociado a un profesional"""
    model = Nino
    form_class = NinoForm
    template_name = 'nino/editar_nino.html'
    success_url = reverse_lazy('core:calendar')

    def get_object(self, queryset=None):
        """Asegurarse de que el profesional solo pueda editar sus propios niños."""
        return get_object_or_404(Nino, pk=self.kwargs['pk'], profesional=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'El niño ha sido actualizado exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Hubo un error al actualizar el niño. Por favor, verifica los datos ingresados.')
        return super().form_invalid(form)

    def get_initial(self):
        """Asegurar que los valores iniciales incluyan la fecha de nacimiento."""
        initial = super().get_initial()
        nino = self.get_object()
        initial['fecha_nacimiento'] = nino.fecha_nacimiento.strftime('%Y-%m-%d')
        return initial


class ObtenerDatosNinoView(View):
    def get(self, request, pk):
        """Devuelve los datos de un niño en formato JSON."""
        try:
            nino = Nino.objects.get(pk=pk, profesional=request.user)
            return JsonResponse({
                'success': True,
                'nino': {
                    'nombres': nino.nombres,
                    'apellidos': nino.apellidos,
                    'fecha_nacimiento': nino.fecha_nacimiento.strftime('%Y-%m-%d'),
                    'edad': nino.edad,
                    'genero': nino.genero,
                    'idioma_nativo': nino.idioma_nativo,
                }
            })
        except Nino.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Niño no encontrado.'}, status=404)


class ListaNinosView(ListView):
    model = Nino
    template_name = 'nino/lista_ninos.html'
    context_object_name = 'ninos'


class EliminarNinoView(DeleteView):
    model = Nino
    template_name = 'nino/confirmar_eliminar_nino.html'
    success_url = reverse_lazy('core:lista_ninos')
