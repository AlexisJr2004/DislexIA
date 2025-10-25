import logging
from datetime import datetime, date
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from app.core.models import Cita
from app.core.utils.email_utils import enviar_correo_cita_doctor, enviar_correo_cita_padres

logger = logging.getLogger(__name__)

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
