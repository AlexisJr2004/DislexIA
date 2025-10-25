from datetime import datetime, date, timedelta
import logging
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.http import JsonResponse
from app.core.models import Cita, Nino

logger = logging.getLogger(__name__)

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
