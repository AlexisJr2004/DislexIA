from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from app.games.models import Evaluacion, SesionJuego, Juego, PruebaCognitiva

@method_decorator(login_required, name='dispatch')
class SequentialResultsView(TemplateView):
    """Vista para mostrar los resultados completos de una evaluación secuencial de juegos"""
    template_name = 'sequential_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        evaluacion_id = kwargs.get('evaluacion_id')

        # Obtener la evaluación
        evaluacion = get_object_or_404(
            Evaluacion,
            id=evaluacion_id,
            nino__profesional=self.request.user
        )

        # Obtener todas las sesiones de esta evaluación
        sesiones = SesionJuego.objects.filter(
            evaluacion=evaluacion
        ).select_related('juego').order_by('fecha_inicio')

        # Calcular métricas totales desde las pruebas cognitivas
        pruebas = PruebaCognitiva.objects.filter(evaluacion=evaluacion)

        total_clics = sum(prueba.clics for prueba in pruebas)
        total_aciertos = sum(prueba.aciertos for prueba in pruebas)
        total_errores = sum(prueba.errores for prueba in pruebas)
        puntaje_total = sum(prueba.puntaje for prueba in pruebas)

        # Calcular precisión promedio
        precision_promedio = 0
        if total_clics > 0:
            precision_promedio = (total_aciertos / total_clics) * 100

        # Calcular tasa de error
        tasa_error = 0
        if total_clics > 0:
            tasa_error = (total_errores / total_clics) * 100

        # ⭐ NUEVO: Agrupar métricas por juego
        from collections import defaultdict
        
        juegos_agrupados = defaultdict(lambda: {
            'veces_jugado': 0,
            'puntaje_total': 0,
            'clics_total': 0,
            'aciertos_total': 0,
            'errores_total': 0,
            'juego_obj': None
        })
        
        # Agrupar por juego
        for sesion in sesiones:
            juego_id = sesion.juego.id
            
            # Obtener métricas de este juego en esta sesión
            pruebas_sesion = pruebas.filter(juego=sesion.juego)
            
            sesion_clics = sum(p.clics for p in pruebas_sesion)
            sesion_aciertos = sum(p.aciertos for p in pruebas_sesion)
            sesion_errores = sum(p.errores for p in pruebas_sesion)
            sesion_puntaje = sum(p.puntaje for p in pruebas_sesion)
            
            juegos_agrupados[juego_id]['veces_jugado'] += 1
            juegos_agrupados[juego_id]['puntaje_total'] += sesion_puntaje
            juegos_agrupados[juego_id]['clics_total'] += sesion_clics
            juegos_agrupados[juego_id]['aciertos_total'] += sesion_aciertos
            juegos_agrupados[juego_id]['errores_total'] += sesion_errores
            juegos_agrupados[juego_id]['juego_obj'] = sesion.juego
        
        juegos_unicos = set(pruebas.values_list('juego', flat=True))

        juegos_resumen = []
        for juego_id in juegos_unicos:
            juego_obj = Juego.objects.get(id=juego_id)
            pruebas_juego = pruebas.filter(juego=juego_obj)
            clics_total = sum(p.clics for p in pruebas_juego)
            aciertos_total = sum(p.aciertos for p in pruebas_juego)
            errores_total = sum(p.errores for p in pruebas_juego)
            puntaje_total = sum(p.puntaje for p in pruebas_juego)
            precision = (aciertos_total / clics_total * 100) if clics_total > 0 else 0

            juegos_resumen.append({
                'juego': juego_obj,
                'veces_jugado': sesiones.filter(juego=juego_obj).count(),
                'puntaje': puntaje_total,
                'clics': clics_total,
                'aciertos': aciertos_total,
                'errores': errores_total,
                'precision': round(precision, 1)
            })
        
        # Ordenar por nombre de juego
        juegos_resumen.sort(key=lambda x: x['juego'].nombre)

        context.update({
            'page_title': f'Resultados - {evaluacion.nino.nombre_completo}',
            'active_section': 'games',
            'evaluacion': evaluacion,
            'sesiones': sesiones,
            'juegos_resumen': juegos_resumen,  # ⭐ NUEVO
            'total_clics': total_clics,
            'total_aciertos': total_aciertos,
            'total_errores': total_errores,
            'puntaje_total': puntaje_total,
            'precision_promedio': precision_promedio,
            'tasa_error': tasa_error,
        })

        return context
