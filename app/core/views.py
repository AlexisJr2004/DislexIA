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
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views import View
from django.db.utils import OperationalError
import json
import logging
from datetime import datetime, date, time, timedelta
from .models import Cita, Nino
from .utils.email_utils import enviar_correo_cita_doctor, enviar_correo_cita_padres

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
    if request.method == 'POST':
        try:
            nombre_paciente = request.POST.get('nombre_paciente')
            email_padres = request.POST.get('email_padres')
            fecha_str = request.POST.get('fecha')
            hora_str = request.POST.get('hora')
            notas = request.POST.get('notas', '')
            foto_paciente = request.FILES.get('foto_paciente')
            
            # Validaciones
            errors = {}
            if not nombre_paciente:
                errors['nombre'] = 'El nombre del paciente es requerido'
            if not email_padres:
                errors['email'] = 'El correo electrónico es requerido'
            if not fecha_str:
                errors['fecha'] = 'La fecha es requerida'
            if not hora_str:
                errors['hora'] = 'La hora es requerida'
            
            if errors:
                return JsonResponse({'success': False, 'errors': errors}, status=400)
            
            # Convertir strings a objetos date y time
            try:
                fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                hora_obj = datetime.strptime(hora_str, '%H:%M').time()
            except ValueError as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Formato de fecha u hora inválido: {str(e)}'
                }, status=400)
            
            # Crear la cita
            cita = Cita.objects.create(
                usuario=request.user,
                nombre_paciente=nombre_paciente,
                email_padres=email_padres,
                fecha=fecha_obj,
                hora=hora_obj,
                notas=notas,
                foto_paciente=foto_paciente
            )
            
            # Enviar correos
            email_doctor_enviado = enviar_correo_cita_doctor(request.user, cita)
            email_padres_enviado = enviar_correo_cita_padres(email_padres, cita, request.user)
            
            # Mensaje de respuesta
            mensaje = 'Cita agendada exitosamente'
            if email_doctor_enviado and email_padres_enviado:
                mensaje += '. Se han enviado las confirmaciones por correo.'
            elif email_doctor_enviado or email_padres_enviado:
                mensaje += '. Algunos correos no pudieron ser enviados.'
            else:
                mensaje += ', pero hubo un error al enviar las confirmaciones por correo.'
            
            return JsonResponse({
                'success': True,
                'message': mensaje,
                'cita_id': cita.id
            })
            
        except Exception as e:
            logger.exception(f"Error al crear cita: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Error al crear la cita: {str(e)}'
            }, status=500)
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

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


@method_decorator(login_required, name='dispatch')
class EditarNinoView(UpdateView):
    """Vista para editar los datos de un niño asociado a un profesional"""
    model = Nino
    form_class = NinoForm
    template_name = 'nino/editar_nino.html'
    success_url = reverse_lazy('core:lista_ninos')

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


@method_decorator(login_required, name='dispatch')
class ObtenerDatosNinoView(View):
    """Vista para obtener datos de un niño en formato JSON"""
    
    def get(self, request, pk):
        """Devuelve los datos de un niño en formato JSON."""
        try:
            nino = Nino.objects.get(pk=pk, profesional=request.user)
            return JsonResponse({
                'success': True,
                'nino': {
                    'id': nino.id,
                    'nombres': nino.nombres,
                    'apellidos': nino.apellidos,
                    'fecha_nacimiento': nino.fecha_nacimiento.strftime('%Y-%m-%d'),
                    'edad': nino.edad,
                    'genero': nino.genero,
                    'idioma_nativo': nino.idioma_nativo,
                    'imagen': nino.imagen.url if nino.imagen else None,
                }
            })
        except Nino.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Niño no encontrado.'}, status=404)


@method_decorator(login_required, name='dispatch')
class ListaNinosView(ListView):
    """Vista para listar todos los niños asociados al profesional"""
    model = Nino
    template_name = 'nino/lista_ninos.html'
    context_object_name = 'ninos'
    
    def get_queryset(self):
        """Filtrar solo los niños del profesional actual"""
        return Nino.objects.filter(profesional=self.request.user).order_by('-fecha_registro')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Lista de Niños - DislexIA',
            'active_section': 'lista_ninos',
        })
        return context


@method_decorator(login_required, name='dispatch')
class EliminarNinoView(DeleteView):
    """Vista para eliminar un niño con confirmación"""
    model = Nino
    template_name = 'nino/confirmar_eliminar_nino.html'
    success_url = reverse_lazy('core:lista_ninos')
    
    def get_object(self, queryset=None):
        """Asegurarse de que el profesional solo pueda eliminar sus propios niños."""
        return get_object_or_404(Nino, pk=self.kwargs['pk'], profesional=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        """Personalizar el mensaje de éxito"""
        nino = self.get_object()
        nombre_completo = nino.nombre_completo
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, f'El niño {nombre_completo} ha sido eliminado exitosamente.')
        return response


@login_required
@require_http_methods(["POST"])
def agregar_nino_ajax(request):
    """Agregar un niño mediante AJAX"""
    try:
        logger.info(f"=== Iniciando agregar_nino_ajax para usuario {request.user} ===")
        logger.info(f"POST data: {request.POST}")
        logger.info(f"FILES: {request.FILES}")
        
        form = NinoForm(request.POST, request.FILES)
        
        if form.is_valid():
            nino = form.save(commit=False)
            nino.profesional = request.user
            nino.save()
            
            logger.info(f"Niño guardado exitosamente: {nino.id} - {nino.nombre_completo}")
            
            # Formatear fecha de nacimiento
            from datetime import datetime
            fecha_formatted = nino.fecha_nacimiento.strftime('%d/%m/%Y')
            
            return JsonResponse({
                'success': True,
                'message': f'El niño {nino.nombre_completo} ha sido agregado exitosamente.',
                'nino': {
                    'id': nino.id,
                    'nombres': nino.nombres,
                    'apellidos': nino.apellidos,
                    'nombre_completo': nino.nombre_completo,
                    'edad': nino.edad,
                    'genero': nino.genero,
                    'idioma_nativo': nino.idioma_nativo,
                    'fecha_nacimiento_formatted': fecha_formatted,
                    'imagen_url': nino.imagen.url if nino.imagen else None
                }
            })
        else:
            logger.error(f"Errores de validación del formulario: {form.errors}")
            logger.error(f"Errores por campo: {dict(form.errors)}")
            
            return JsonResponse({
                'success': False,
                'error': 'Error de validación. Por favor revisa los campos.',
                'errors': dict(form.errors)
            }, status=400)
            
    except Exception as e:
        logger.exception(f"Error inesperado en agregar_nino_ajax: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Error del servidor: {str(e)}'
        }, status=500)

@login_required
def get_notificaciones(request):
    """Obtener notificaciones del usuario"""
    try:
        ahora = datetime.now()
        hoy = date.today()
        manana = hoy + timedelta(days=1)
        
        # 1. Citas próximas (próximas 24 horas)
        citas_proximas = Cita.objects.filter(
            usuario=request.user,
            fecha__gte=hoy,
            fecha__lte=manana,
            completada=False
        ).order_by('fecha', 'hora')[:5]
        
        # 2. Citas de hoy pendientes
        citas_hoy = Cita.objects.filter(
            usuario=request.user,
            fecha=hoy,
            completada=False
        ).count()
        
        # 3. Citas vencidas (pasadas y no completadas)
        citas_vencidas = Cita.objects.filter(
            usuario=request.user,
            fecha__lt=hoy,
            completada=False
        ).count()
        
        # 4. Total de pacientes registrados
        total_pacientes = Nino.objects.filter(
            profesional=request.user,
            activo=True
        ).count()
        
        notificaciones = []
        
        # Agregar notificaciones de citas próximas
        for cita in citas_proximas:
            hora_cita = datetime.combine(cita.fecha, cita.hora)
            tiempo_restante = hora_cita - ahora
            
            if tiempo_restante.total_seconds() > 0:
                horas_restantes = int(tiempo_restante.total_seconds() / 3600)
                
                if horas_restantes <= 1:
                    mensaje = f"Cita con {cita.nombre_paciente} en menos de 1 hora"
                    tipo = 'urgente'
                elif horas_restantes <= 3:
                    mensaje = f"Cita con {cita.nombre_paciente} en {horas_restantes} horas"
                    tipo = 'advertencia'
                else:
                    mensaje = f"Cita con {cita.nombre_paciente} mañana a las {cita.hora.strftime('%H:%M')}"
                    tipo = 'info'
                
                notificaciones.append({
                    'id': cita.id,
                    'tipo': tipo,
                    'mensaje': mensaje,
                    'fecha': cita.fecha.isoformat(),
                    'hora': cita.hora.strftime('%H:%M'),
                    'paciente': cita.nombre_paciente,
                    'foto': cita.foto_paciente.url if cita.foto_paciente else None,
                    'icono': 'fa-clock',
                    'tiempo': f"{horas_restantes}h"
                })
        
        # Notificación de citas vencidas
        if citas_vencidas > 0:
            notificaciones.append({
                'tipo': 'error',
                'mensaje': f'Tienes {citas_vencidas} cita{"s" if citas_vencidas > 1 else ""} pendiente{"s" if citas_vencidas > 1 else ""} de completar',
                'icono': 'fa-exclamation-triangle',
                'accion': 'revisar_vencidas'
            })
        
        # Notificación resumen del día
        if citas_hoy > 0:
            notificaciones.append({
                'tipo': 'info',
                'mensaje': f'Tienes {citas_hoy} cita{"s" if citas_hoy > 1 else ""} programada{"s" if citas_hoy > 1 else ""} para hoy',
                'icono': 'fa-calendar-check',
                'accion': 'ver_calendario'
            })
        
        # Notificación de bienvenida si es nuevo usuario
        if total_pacientes == 0:
            notificaciones.append({
                'tipo': 'info',
                'mensaje': '¡Bienvenido! Comienza agregando tus primeros pacientes',
                'icono': 'fa-user-plus',
                'accion': 'agregar_paciente'
            })
        
        return JsonResponse({
            'success': True,
            'notificaciones': notificaciones,
            'total': len(notificaciones),
            'no_leidas': len([n for n in notificaciones if n.get('tipo') in ['urgente', 'error']])
        })
        
    except Exception as e:
        logger.exception(f"Error al obtener notificaciones: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
