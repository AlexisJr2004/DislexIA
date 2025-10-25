import json
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from app.games.models import Juego, SesionJuego, Evaluacion, PruebaCognitiva
from app.core.models import Nino

@csrf_exempt
@require_http_methods(["POST"])
def save_question_response(request):
    """API endpoint para guardar la respuesta a una pregunta específica"""
    try:
        data = json.loads(request.body)
        
        print(f"📥 question-response recibido:")
        print(f"   session_url: {data.get('session_url')}")
        print(f"   question_id: {data.get('question_id')}")
        print(f"   is_correct: {data.get('is_correct')}")
        
        session_url = data.get('session_url')
        question_id = data.get('question_id')
        is_correct = data.get('is_correct', False)
        response_time_ms = data.get('response_time_ms', 0)
        points_earned = data.get('points_earned', 0)
        
        if not session_url:
            raise ValueError("session_url es requerido")
        if question_id is None:
            raise ValueError("question_id es requerido")
        
        sesion = get_object_or_404(SesionJuego, url_sesion=session_url)
        
        # ⭐ CAMBIO: Buscar por (evaluacion, juego, numero_prueba)
        try:
            prueba = PruebaCognitiva.objects.get(
                evaluacion=sesion.evaluacion,
                juego=sesion.juego,
                numero_prueba=question_id
            )
            # Si existe, actualizar
            prueba.clics += 1
            if is_correct:
                prueba.aciertos += 1
            else:
                prueba.errores += 1
            prueba.puntaje += points_earned
            prueba.save()
            created = False
            
        except PruebaCognitiva.DoesNotExist:
            # Si no existe, crear
            prueba = PruebaCognitiva.objects.create(
                evaluacion=sesion.evaluacion,
                juego=sesion.juego,
                numero_prueba=question_id,
                clics=1,
                aciertos=1 if is_correct else 0,
                errores=0 if is_correct else 1,
                puntaje=points_earned,
                tiempo_respuesta_ms=response_time_ms
            )
            created = True
        
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
        
    except ValueError as e:
        print(f"❌ Error de validación en question-response: {e}")
        print(f"   Datos recibidos: {json.loads(request.body)}")
        return JsonResponse({
            'success': False,
            'error': f'Datos inválidos: {str(e)}'
        }, status=400)
        
    except Exception as e:
        print(f"❌ Error en question-response: {e}")
        print(f"   Request body: {request.body.decode('utf-8')}")
        import traceback
        traceback.print_exc()
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
