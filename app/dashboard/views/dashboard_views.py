from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    """
    Vista principal del dashboard que muestra el resumen de actividades.
    """
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        from app.games.models import SesionJuego
        from app.core.models import Nino, Profesional, ReporteIA, Cita
        from django.utils import timezone
        from django.db.models import Count, Avg
        import datetime

        context = super().get_context_data(**kwargs)
        now = timezone.now()
        first_day_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Sesiones de juego completadas este mes
        sesiones_mes = SesionJuego.objects.filter(fecha_inicio__gte=first_day_month, fecha_inicio__lte=now, estado='completada')
        total_sesiones_mes = sesiones_mes.count()
        
        # Obtener niños únicos que participaron este mes
        ninos_ids = sesiones_mes.values_list('evaluacion__nino', flat=True).distinct()
        ninos_participantes = Nino.objects.filter(id__in=ninos_ids)[:5]  # Máximo 5 para mostrar
        ninos_participantes_mes = ninos_participantes.count()

        # Progreso promedio de intervención (basado en accuracy_percent de las sesiones)
        progreso_promedio_result = sesiones_mes.aggregate(avg=Avg('accuracy_percent'))['avg']
        progreso_promedio = round(progreso_promedio_result if progreso_promedio_result else 0, 2)

        # Profesionales activos con métricas de rendimiento
        profesionales = Profesional.objects.filter(is_active=True).order_by('-ultimo_acceso')[:5]
        
        # Calcular métricas para cada profesional
        profesionales_con_metricas = []
        max_pacientes = 0  # Para calcular el porcentaje de carga
        
        for profesional in profesionales:
            # Pacientes asignados al profesional
            pacientes_asignados = Nino.objects.filter(profesional=profesional).count()
            
            # Sesiones supervisadas este mes
            sesiones_supervisadas = SesionJuego.objects.filter(
                evaluacion__nino__profesional=profesional,
                fecha_inicio__gte=first_day_month,
                fecha_inicio__lte=now,
                estado='completada'
            ).count()
            
            # Reportes IA generados este mes
            reportes_generados = ReporteIA.objects.filter(
                evaluacion__nino__profesional=profesional,
                fecha_generacion__gte=first_day_month,
                fecha_generacion__lte=now
            ).count()
            
            # Actualizar el máximo para calcular porcentajes
            if pacientes_asignados > max_pacientes:
                max_pacientes = pacientes_asignados
            
            profesionales_con_metricas.append({
                'profesional': profesional,
                'pacientes_asignados': pacientes_asignados,
                'sesiones_supervisadas': sesiones_supervisadas,
                'reportes_generados': reportes_generados,
            })
        
        # Calcular porcentaje de carga (basado en pacientes asignados)
        for prof_data in profesionales_con_metricas:
            if max_pacientes > 0:
                prof_data['porcentaje_carga'] = int((prof_data['pacientes_asignados'] / max_pacientes) * 100)
            else:
                prof_data['porcentaje_carga'] = 0

        # Últimos reportes IA
        reportes_ia = ReporteIA.objects.select_related('evaluacion').order_by('-fecha_generacion')[:5]

        # Próximas citas
        citas = Cita.objects.filter(fecha__gte=now.date()).order_by('fecha', 'hora')[:5]
        
        # Total de pacientes (niños) registrados en el sistema
        total_pacientes = Nino.objects.count()
        
        # Pacientes activos este mes (con sesiones)
        pacientes_activos_mes = ninos_participantes_mes

        # Calcular tiempo total invertido en sesiones este mes
        from django.db.models import Sum
        tiempo_total_dict = sesiones_mes.aggregate(total=Sum('tiempo_total_segundos'))
        tiempo_total_segundos = tiempo_total_dict['total'] if tiempo_total_dict['total'] else 0
        
        # Convertir segundos a horas, minutos y segundos
        tiempo_total_horas = tiempo_total_segundos // 3600
        tiempo_total_minutos = (tiempo_total_segundos % 3600) // 60
        tiempo_total_segs = tiempo_total_segundos % 60
        
        # Últimas sesiones completadas con duración
        ultimas_sesiones = SesionJuego.objects.filter(
            estado='completada'
        ).select_related('juego', 'evaluacion__nino').order_by('-fecha_inicio')[:3]

        context.update({
            'page_title': 'Dashboard - Panel Administrativo',
            'active_section': 'dashboard',
            'total_sesiones_mes': total_sesiones_mes,
            'ninos_participantes_mes': ninos_participantes_mes,
            'ninos_participantes': ninos_participantes,
            'progreso_promedio': progreso_promedio,
            'profesionales': profesionales,
            'profesionales_con_metricas': profesionales_con_metricas,
            'reportes_ia': reportes_ia,
            'citas': citas,
            'tiempo_total_horas': tiempo_total_horas,
            'tiempo_total_minutos': tiempo_total_minutos,
            'tiempo_total_segs': tiempo_total_segs,
            'ultimas_sesiones': ultimas_sesiones,
            'total_pacientes': total_pacientes,
            'pacientes_activos_mes': pacientes_activos_mes,
        })
        return context
