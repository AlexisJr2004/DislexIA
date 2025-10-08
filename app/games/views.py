from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import json
import os
from django.conf import settings

from .models import Juego, SesionJuego, Evaluacion
from app.core.models import Nino

class GameListView(TemplateView):
    template_name = 'game_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener todos los juegos activos ordenados por su orden de visualización
        juegos = Juego.objects.filter(activo=True).order_by('orden_visualizacion', 'nombre')
        
        context.update({
            'page_title': 'Juegos - DislexIA',
            'active_section': 'games',
            'juegos': juegos,
        })
        return context

class InitGameView(TemplateView):
    """Vista para inicializar un juego y crear la sesión"""
    template_name = 'init_game.html'
    
    def get(self, request, *args, **kwargs):
        juego_slug = kwargs.get('juego_slug')
        
        # Obtener el juego
        juego = get_object_or_404(Juego, slug=juego_slug, activo=True)
        
        # IMPORTANTE: Por ahora usar el niño con ID=1 por defecto
        try:
            nino = Nino.objects.get(id=1)
        except Nino.DoesNotExist:
            messages.error(request, "No se encontró un niño configurado. Por favor, configure al menos un niño antes de continuar.")
            return redirect('games:game_list')
        
        # Crear nueva evaluación
        evaluacion = Evaluacion.objects.create(
            nino=nino,
            fecha_hora_inicio=timezone.now(),
            estado='en_proceso'
        )
        
        # Crear nueva sesión de juego
        sesion = SesionJuego.crear_nueva_sesion(
            evaluacion=evaluacion,
            juego=juego,
            nivel=1  # Nivel por defecto
        )
        
        # Redirigir a la página del juego
        return redirect('games:play_game', url_sesion=sesion.url_sesion)

class PlayGameView(TemplateView):
    """Vista para renderizar el contenido del juego"""
    template_name = 'play_game.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        url_sesion = kwargs.get('url_sesion')
        
        # Obtener la sesión
        sesion = get_object_or_404(SesionJuego, url_sesion=url_sesion)
        
        # Verificar si el archivo de configuración existe
        if not sesion.juego.archivo_configuracion_existe():
            # Crear archivo template si no existe
            sesion.juego.crear_archivo_configuracion_template()
        
        # Leer el contenido del JSON
        game_config = None
        try:
            ruta_completa = os.path.join(settings.BASE_DIR, sesion.juego.ruta_archivo_configuracion)
            with open(ruta_completa, 'r', encoding='utf-8') as f:
                game_config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # Si hay error, crear archivo básico
            sesion.juego.crear_archivo_configuracion_template()
            # Intentar leer nuevamente
            try:
                with open(ruta_completa, 'r', encoding='utf-8') as f:
                    game_config = json.load(f)
            except:
                game_config = {"error": "No se pudo cargar la configuración del juego"}
        
        context.update({
            'page_title': f'{sesion.juego.nombre} - DislexIA',
            'active_section': 'games',
            'sesion': sesion,
            'juego': sesion.juego,
            'evaluacion': sesion.evaluacion,
            'nino': sesion.evaluacion.nino,
            'game_config': game_config,
            'game_config_json': json.dumps(game_config, ensure_ascii=False, indent=2) if game_config else '{}',
        })
        
        return context

@csrf_exempt
@require_http_methods(["POST"])
def finish_game_session(request, url_sesion):
    """API endpoint para finalizar una sesión de juego"""
    try:
        # Obtener la sesión
        sesion = get_object_or_404(SesionJuego, url_sesion=url_sesion)
        
        # Parsear datos del POST
        data = json.loads(request.body)
        
        puntaje_final = data.get('puntaje_total', 0)
        preguntas_contestadas = data.get('preguntas_respondidas', 0)
        tiempo_total = data.get('tiempo_total_segundos', 0)
        
        # Finalizar sesión
        sesion.finalizar_sesion(puntaje_final, preguntas_contestadas, tiempo_total)
        
        # También finalizar la evaluación si es necesaria
        evaluacion = sesion.evaluacion
        evaluacion.fecha_hora_fin = timezone.now()
        evaluacion.estado = 'completada'
        evaluacion.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Sesión finalizada correctamente',
            'sesion_id': sesion.id,
            'evaluacion_id': evaluacion.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

