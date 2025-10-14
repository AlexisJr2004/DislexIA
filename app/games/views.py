from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import json
import os
from django.conf import settings

from .models import Juego, SesionJuego, Evaluacion
from app.core.models import Nino, Profesional
from app.core.forms import NinoForm

@method_decorator(login_required, name='dispatch')
class GameListView(TemplateView):
    template_name = 'game_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener todos los juegos activos ordenados por su orden de visualización
        juegos = Juego.objects.filter(activo=True).order_by('orden_visualizacion', 'nombre')
        
        # Obtener el profesional actual directamente desde el usuario
        profesional = self.request.user

        # Obtener los niños asociados al profesional actual
        ninos = Nino.objects.filter(profesional=profesional)

        context.update({
            'page_title': 'Juegos - DislexIA',
            'active_section': 'games',
            'juegos': juegos,
            'ninos': ninos,
        })
        return context

@method_decorator(login_required, name='dispatch')
class GameSessionListView(TemplateView):
    """Vista para listar las sesiones de juegos del profesional autenticado"""
    template_name = 'game_session_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener el profesional actual directamente desde el usuario
        profesional = self.request.user

        # Obtener las sesiones de juegos asociadas a los niños del profesional
        sesiones = SesionJuego.objects.filter(
            evaluacion__nino__profesional=profesional
        ).select_related('juego', 'evaluacion__nino').order_by('-fecha_inicio')

        context.update({
            'page_title': 'Sesiones de Juegos - DislexIA',
            'active_section': 'games',
            'sesiones': sesiones,
        })
        return context

@method_decorator(login_required, name='dispatch')
class InitGameView(TemplateView):
    """Vista para inicializar un juego y crear la sesión"""
    template_name = 'init_game.html'
    
    def get(self, request, *args, **kwargs):
        juego_slug = kwargs.get('juego_slug')
        
        # Obtener el juego
        juego = get_object_or_404(Juego, slug=juego_slug, activo=True)
        
        # Priorizar nino_id pasado por querystring
        nino = None
        nino_id = request.GET.get('nino_id')
        if nino_id:
            try:
                nino = Nino.objects.get(id=int(nino_id))
            except (Nino.DoesNotExist, ValueError):
                messages.error(request, "Niño no encontrado (nino_id inválido).")
                return redirect('games:game_list')

        # Si no se pasó nino_id, intentar usar el primer niño asociado al profesional
        if not nino:
            user = getattr(request, 'user', None)
            if user and user.is_authenticated and isinstance(user, Profesional):
                # intentar obtener un niño asociado a este profesional
                nino = Nino.objects.filter(profesional=user, activo=True).order_by('-fecha_registro').first()

        # Si aún no hay niño, usar por defecto id=1 (legacy) o pedir crear uno
        if not nino:
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

@method_decorator(login_required, name='dispatch')
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
def save_question_response(request):
    """API endpoint para guardar la respuesta a una pregunta específica"""
    try:
        data = json.loads(request.body)
        
        session_url = data.get('session_url')
        question_id = data.get('question_id')
        is_correct = data.get('is_correct', False)
        response_time_ms = data.get('response_time_ms', 0)
        points_earned = data.get('points_earned', 0)
        
        # Obtener la sesión
        sesion = get_object_or_404(SesionJuego, url_sesion=session_url)
        
        # Crear o actualizar PruebaCognitiva
        from .models import PruebaCognitiva
        
        prueba, created = PruebaCognitiva.objects.get_or_create(
            evaluacion=sesion.evaluacion,
            juego=sesion.juego,
            numero_prueba=question_id,
            defaults={
                'clics': 1,
                'aciertos': 1 if is_correct else 0,
                'errores': 0 if is_correct else 1,
                'puntaje': points_earned,
                'tiempo_respuesta_ms': response_time_ms
            }
        )
        
        if not created:
            # Actualizar existente
            prueba.clics += 1
            if is_correct:
                prueba.aciertos += 1
            else:
                prueba.errores += 1
            prueba.puntaje += points_earned
            prueba.save()
        
        # Actualizar estadísticas de la sesión
        sesion.puntaje_total += points_earned if is_correct else 0
        if is_correct:
            sesion.preguntas_respondidas += 1
        sesion.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Respuesta guardada correctamente',
            'prueba_id': prueba.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def save_level_complete(request):
    """API endpoint para guardar la finalización de un nivel"""
    try:
        data = json.loads(request.body)
        
        session_url = data.get('session_url')
        level = data.get('level', 1)
        total_questions = data.get('total_questions', 0)
        correct_answers = data.get('correct_answers', 0)
        incorrect_answers = data.get('incorrect_answers', 0)
        
        # Obtener la sesión
        sesion = get_object_or_404(SesionJuego, url_sesion=session_url)
        
        # Actualizar estadísticas de la evaluación
        evaluacion = sesion.evaluacion
        evaluacion.total_aciertos += correct_answers
        evaluacion.total_errores += incorrect_answers
        evaluacion.total_clics += total_questions
        
        # Calcular precisión promedio
        total_respuestas = evaluacion.total_aciertos + evaluacion.total_errores
        if total_respuestas > 0:
            evaluacion.precision_promedio = (evaluacion.total_aciertos / total_respuestas) * 100
        
        evaluacion.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Nivel {level} completado correctamente',
            'evaluacion_stats': {
                'total_aciertos': evaluacion.total_aciertos,
                'total_errores': evaluacion.total_errores,
                'precision_promedio': float(evaluacion.precision_promedio)
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def finish_game_session(request, url_sesion):
    """API endpoint para finalizar una sesión de juego"""
    try:
        # Obtener la sesión
        sesion = get_object_or_404(SesionJuego, url_sesion=url_sesion)
        
        # Parsear datos del POST
        data = json.loads(request.body)
        
        puntaje_final = data.get('total_score', sesion.puntaje_total)
        preguntas_contestadas = data.get('total_correct', 0) + data.get('total_incorrect', 0)
        tiempo_total = data.get('total_time_seconds', 0)
        
        # Finalizar sesión
        sesion.finalizar_sesion(puntaje_final, preguntas_contestadas, tiempo_total)
        
        # También finalizar la evaluación si es necesaria
        evaluacion = sesion.evaluacion
        evaluacion.fecha_hora_fin = timezone.now()
        evaluacion.estado = 'completada'
        evaluacion.duracion_total_minutos = tiempo_total // 60
        evaluacion.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Sesión finalizada correctamente',
            'sesion_id': sesion.id,
            'evaluacion_id': evaluacion.id,
            'final_stats': {
                'puntaje_total': sesion.puntaje_total,
                'preguntas_respondidas': sesion.preguntas_respondidas,
                'tiempo_total_minutos': evaluacion.duracion_total_minutos,
                'precision_promedio': float(evaluacion.precision_promedio)
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def crear_nino_ajax(request):
    """Crear un niño asociado al profesional autenticado vía AJAX.
    Espera campos del NinoForm en POST.
    """
    try:
        # Si el usuario no está autenticado, retornar error
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Autenticación requerida'}, status=401)

        # Bind form
        form = NinoForm(request.POST, request.FILES)
        if form.is_valid():
            nino = form.save(commit=False)
            # Asignar profesional si es instancia de Profesional
            if isinstance(user, Profesional):
                nino.profesional = user
            nino.save()
            return JsonResponse({
                'success': True, 
                'nino': {
                    'id': nino.id, 
                    'nombres': nino.nombres,
                    'apellidos': nino.apellidos,
                    'nombre_completo': nino.nombre_completo,
                    'edad': nino.edad,
                    'genero': nino.genero
                }
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def asignar_nino(request):
    """Asocia un niño existente con un juego."""
    nino_id = request.POST.get('nino_id')
    juego_slug = request.POST.get('juego_slug')

    if not nino_id or not juego_slug:
        return JsonResponse({'success': False, 'error': 'Datos incompletos.'}, status=400)

    try:
        nino = Nino.objects.get(id=nino_id, profesional=request.user)
        juego = Juego.objects.get(slug=juego_slug)

        # Crear o actualizar la sesión del juego
        # Nota: Aquí puedes ajustar la lógica según tu modelo
        # Por ejemplo, crear una evaluación primero
        evaluacion = Evaluacion.objects.create(
            nino=nino,
            fecha_hora_inicio=timezone.now(),
            estado='en_proceso'
        )
        
        sesion = SesionJuego.crear_nueva_sesion(
            evaluacion=evaluacion,
            juego=juego,
            nivel=1
        )

        return JsonResponse({
            'success': True, 
            'redirect_url': f"/games/play/{sesion.url_sesion}/"
        })
    except Nino.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Niño no encontrado.'}, status=404)
    except Juego.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Juego no encontrado.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
