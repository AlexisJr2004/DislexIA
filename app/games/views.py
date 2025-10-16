from django.views.generic import TemplateView, View
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
class InitSequentialEvaluationView(View):
    """Vista para inicializar una evaluación secuencial completa con todos los juegos activos"""

    def get(self, request, *args, **kwargs):
        print("=== InitSequentialEvaluationView called ===")
        
        # Obtener nino_id del querystring
        nino_id = request.GET.get('nino_id')

        if not nino_id:
            messages.error(request, "ID de niño no proporcionado.")
            return redirect('games:game_list')

        try:
            nino_id = int(nino_id)
        except (ValueError, TypeError):
            messages.error(request, "ID de niño inválido.")
            return redirect('games:game_list')

        # Verificar que el niño pertenece al profesional actual
        try:
            nino = Nino.objects.get(id=nino_id, profesional=request.user)
        except Nino.DoesNotExist:
            messages.error(request, "Niño no encontrado o no autorizado.")
            return redirect('games:game_list')

        # Crear nueva evaluación
        evaluacion = Evaluacion.objects.create(
            nino=nino,
            fecha_hora_inicio=timezone.now(),
            estado='en_proceso'
        )

        # Obtener todos los juegos activos ordenados por orden_visualizacion
        juegos = Juego.objects.filter(activo=True).order_by('orden_visualizacion')

        if not juegos.exists():
            messages.error(request, "No hay juegos activos disponibles.")
            return redirect('games:game_list')

        # Crear sesiones para todos los juegos
        sesiones_creadas = []
        for juego in juegos:
            try:
                sesion = SesionJuego.crear_nueva_sesion(
                    evaluacion=evaluacion,
                    juego=juego,
                    nivel=1  # Nivel por defecto
                )
                sesiones_creadas.append(sesion)
            except Exception as e:
                # Continuar con el siguiente juego
                continue

        if not sesiones_creadas:
            messages.error(request, "Error al crear las sesiones de juegos.")
            return redirect('games:game_list')

        # Redirigir al primer juego
        primera_sesion = sesiones_creadas[0]
        print(f"=== Redirecting to first game: {primera_sesion.url_sesion} ===")
        return redirect('games:play_game', url_sesion=primera_sesion.url_sesion)


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
        print(f"=== PlayGameView called with url_sesion: {url_sesion} ===")
        
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
        
        # Obtener todas las sesiones de esta evaluación ordenadas
        sesiones_evaluacion = SesionJuego.objects.filter(
            evaluacion=sesion.evaluacion
        ).select_related('juego').order_by('fecha_inicio')

        # Obtener todos los juegos activos ordenados
        juegos = Juego.objects.filter(activo=True).order_by('orden_visualizacion')

        # Agregar init_url a cada juego
        juegos_con_urls = []
        for juego in juegos:
            # Buscar si ya existe una sesión para este juego en la evaluación actual
            sesion_existente = sesiones_evaluacion.filter(juego=juego).first()
            if sesion_existente:
                # Usar la URL de la sesión existente
                init_url = f'/games/play/{sesion_existente.url_sesion}/'
            else:
                # Si no existe, crear nueva sesión (caso legacy)
                init_url = f'/games/init/{juego.slug}/?nino_id={sesion.evaluacion.nino.id}'
            
            juegos_con_urls.append({
                'id': juego.id,
                'slug': juego.slug,
                'nombre': juego.nombre,
                'init_url': init_url
            })
        
        context.update({
            'page_title': f'{sesion.juego.nombre} - DislexIA',
            'active_section': 'games',
            'sesion': sesion,
            'juego': sesion.juego,
            'evaluacion': sesion.evaluacion,
            'nino': sesion.evaluacion.nino,
            'game_config': game_config,
            'game_config_json': json.dumps(game_config, ensure_ascii=False, indent=2) if game_config else '{}',
            'juegos': juegos_con_urls,
            'juegos_json': json.dumps(juegos_con_urls, ensure_ascii=False),
        })
        
        print(f"=== PlayGameView returning template for game: {sesion.juego.nombre} ===")
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
        
        # Verificar si debemos finalizar la evaluación completa
        evaluacion = sesion.evaluacion
        total_sesiones = SesionJuego.objects.filter(evaluacion=evaluacion).count()
        sesiones_completadas = SesionJuego.objects.filter(evaluacion=evaluacion, estado='completada').count()
        
        # Si todas las sesiones están completadas, finalizar la evaluación
        if sesiones_completadas == total_sesiones:
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
            nino__profesional=self.request.user  # Solo el profesional asignado puede ver
        )

        # Obtener todas las sesiones de esta evaluación (no solo completadas)
        sesiones = SesionJuego.objects.filter(
            evaluacion=evaluacion
        ).select_related('juego').order_by('fecha_inicio')

        # Calcular métricas totales desde las pruebas cognitivas
        from .models import PruebaCognitiva
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

        # Calcular métricas por sesión/juego
        sesiones_con_metricas = []
        for sesion in sesiones:
            # Obtener todas las pruebas cognitivas de este juego en esta evaluación
            pruebas_juego = pruebas.filter(juego=sesion.juego)
            
            # Calcular métricas para este juego
            juego_clics = sum(prueba.clics for prueba in pruebas_juego)
            juego_aciertos = sum(prueba.aciertos for prueba in pruebas_juego)
            juego_errores = sum(prueba.errores for prueba in pruebas_juego)
            juego_puntaje = sum(prueba.puntaje for prueba in pruebas_juego)
            
            # Calcular precisión del juego
            juego_precision = 0
            if juego_clics > 0:
                juego_precision = (juego_aciertos / juego_clics) * 100
            
            # Calcular tasa de error del juego
            juego_tasa_error = 0
            if juego_clics > 0:
                juego_tasa_error = (juego_errores / juego_clics) * 100
            
            # Agregar métricas a la sesión
            sesiones_con_metricas.append({
                'sesion': sesion,
                'clics': juego_clics,
                'aciertos': juego_aciertos,
                'errores': juego_errores,
                'puntaje': juego_puntaje,
                'precision': juego_precision,
                'tasa_error': juego_tasa_error,
            })

        context.update({
            'page_title': f'Resultados - {evaluacion.nino.nombre_completo}',
            'active_section': 'games',
            'evaluacion': evaluacion,
            'sesiones': sesiones,
            'sesiones_con_metricas': sesiones_con_metricas,
            'total_clics': total_clics,
            'total_aciertos': total_aciertos,
            'total_errores': total_errores,
            'puntaje_total': puntaje_total,
            'precision_promedio': precision_promedio,
            'tasa_error': tasa_error,
        })

        return context

