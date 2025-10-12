from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from .forms import ProfesionalLoginForm, ProfesionalRegistrationForm, ProfesionalUpdateForm, ProfesionalPasswordResetForm, ProfesionalSetPasswordForm
from django.contrib.auth import login
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from datetime import datetime, date
from .models import Cita
from app.resources.models import Recurso
from django.shortcuts import render


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


@login_required
def get_citas_dia(request):
    """Obtener citas del día para el sidebar"""
    fecha_str = request.GET.get('fecha', date.today().isoformat())
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        fecha = date.today()
    
    citas = Cita.objects.filter(
        usuario=request.user,
        fecha=fecha
    ).order_by('hora')
    
    citas_data = [{
        'id': cita.id,
        'nombre_paciente': cita.nombre_paciente,
        'foto_paciente': cita.foto_paciente.url if cita.foto_paciente else None,
        'hora': cita.hora.strftime('%H:%M'),
        'fecha': cita.fecha.isoformat(),
        'completada': cita.completada,
        'notas': cita.notas
    } for cita in citas]
    
    return JsonResponse({'citas': citas_data})

@login_required
@require_http_methods(["POST"])
def crear_cita(request):
    """Crear una nueva cita"""
    try:
        print("=== DEBUG: Iniciando crear_cita ===")
        print(f"POST data: {request.POST}")
        print(f"FILES: {request.FILES}")
        
        # Manejar FormData en lugar de JSON
        nombre_paciente = request.POST.get('nombre_paciente')
        fecha_str = request.POST.get('fecha')
        hora_str = request.POST.get('hora')
        notas = request.POST.get('notas', '')
        
        print(f"Datos recibidos - Paciente: {nombre_paciente}, Fecha: {fecha_str}, Hora: {hora_str}")
        
        if not nombre_paciente or not fecha_str or not hora_str:
            return JsonResponse({
                'success': False, 
                'error': 'Faltan campos requeridos'
            }, status=400)
        
        # Convertir strings a objetos date y time
        from datetime import datetime
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        hora = datetime.strptime(hora_str, '%H:%M').time()
        
        cita = Cita.objects.create(
            usuario=request.user,
            nombre_paciente=nombre_paciente,
            fecha=fecha,
            hora=hora,
            notas=notas
        )
        
        print(f"Cita creada con ID: {cita.id}")
        
        # Manejar archivo de foto si existe
        if 'foto_paciente' in request.FILES:
            cita.foto_paciente = request.FILES['foto_paciente']
            cita.save()
            print("Foto agregada exitosamente")
        
        return JsonResponse({
            'success': True,
            'cita': {
                'id': cita.id,
                'nombre_paciente': cita.nombre_paciente,
                'fecha': cita.fecha.isoformat(),  # Ahora sí es un objeto date
                'hora': cita.hora.strftime('%H:%M'),  # Ahora sí es un objeto time
                'foto_paciente': cita.foto_paciente.url if cita.foto_paciente else None
            }
        })
    except ValueError as e:
        print(f"=== ERROR de formato en crear_cita: {str(e)} ===")
        return JsonResponse({
            'success': False, 
            'error': f'Formato de fecha u hora inválido: {str(e)}'
        }, status=400)
    except Exception as e:
        print(f"=== ERROR en crear_cita: {str(e)} ===")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False, 
            'error': str(e)
        }, status=400)

@login_required
@require_http_methods(["DELETE"])
def eliminar_cita(request, cita_id):
    """Eliminar una cita"""
    try:
        cita = Cita.objects.get(id=cita_id, usuario=request.user)
        cita.delete()
        return JsonResponse({'success': True})
    except Cita.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Cita no encontrada'}, status=404)

@login_required
@require_http_methods(["POST"])
def marcar_cita_completada(request, cita_id):
    """Marcar cita como completada"""
    try:
        cita = Cita.objects.get(id=cita_id, usuario=request.user)
        cita.completada = not cita.completada
        cita.save()
        return JsonResponse({'success': True, 'completada': cita.completada})
    except Cita.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Cita no encontrada'}, status=404)

@login_required
@require_http_methods(["GET"])
def recursos_view(request):
    recursos = Recurso.objects.filter(activo=True)
    
    context = {
        'page_title': 'Recursos sobre Dislexia',
        'recursos': recursos,
    }
    return render(request, 'documents.html', context)