from django.views.generic import TemplateView, View
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

import json
import os
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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
        
        profesional = self.request.user
        
        # ⭐ Solo obtener filtro de estado (sin búsqueda)
        filtro_estado = self.request.GET.get('estado', 'todos')
        
        from .models import Evaluacion
        
        # Query base sin filtros (para estadísticas globales)
        evaluaciones_todas = Evaluacion.objects.filter(
            nino__profesional=profesional
        ).select_related('nino')
        
        # Calcular estadísticas globales
        total_evaluaciones_global = evaluaciones_todas.count()
        completadas_global = evaluaciones_todas.filter(estado='completada').count()
        en_proceso_global = evaluaciones_todas.filter(estado='en_proceso').count()
        interrumpidas_global = total_evaluaciones_global - completadas_global - en_proceso_global
        
        # Aplicar solo filtro por estado
        evaluaciones = evaluaciones_todas
        
        if filtro_estado != 'todos':
            evaluaciones = evaluaciones.filter(estado=filtro_estado)
        
        evaluaciones = evaluaciones.order_by('-fecha_hora_inicio')

        # Preparar lista con métricas
        evaluaciones_con_metricas = []
        for evaluacion in evaluaciones:
            sesiones = SesionJuego.objects.filter(evaluacion=evaluacion)
            sesiones_completadas = sesiones.filter(estado='completada').count()
            total_sesiones = sesiones.count()
            
            sesiones_comp = sesiones.filter(estado='completada')
            if sesiones_comp.exists():
                total_clicks = sum(s.clicks_total or 0 for s in sesiones_comp)
                total_hits = sum(s.hits_total or 0 for s in sesiones_comp)
                accuracy_promedio = (total_hits / total_clicks * 100) if total_clicks > 0 else 0
            else:
                accuracy_promedio = 0
            
            evaluaciones_con_metricas.append({
                'evaluacion': evaluacion,
                'sesiones_completadas': sesiones_completadas,
                'total_sesiones': total_sesiones,
                'accuracy_promedio': round(accuracy_promedio, 1),
                'progreso_porcentaje': round((sesiones_completadas / total_sesiones * 100), 1) if total_sesiones > 0 else 0
            })

        # Paginación
        paginator = Paginator(evaluaciones_con_metricas, 10)
        page = self.request.GET.get('page', 1)
        
        try:
            evaluaciones_paginadas = paginator.page(page)
        except PageNotAnInteger:
            evaluaciones_paginadas = paginator.page(1)
        except EmptyPage:
            evaluaciones_paginadas = paginator.page(paginator.num_pages)

        ninos = Nino.objects.filter(profesional=profesional)

        context.update({
            'page_title': 'Evaluaciones - DislexIA',
            'active_section': 'games',
            'evaluaciones': evaluaciones_paginadas,
            'ninos': ninos,
            'total_evaluaciones': total_evaluaciones_global,
            'evaluaciones_completadas': completadas_global,
            'evaluaciones_en_proceso': en_proceso_global,
            'evaluaciones_interrumpidas': interrumpidas_global,
            'filtro_actual': filtro_estado,
        })
        
        return context

@method_decorator(login_required, name='dispatch')
class InitSequentialEvaluationView(View):
    """Vista para inicializar una evaluación secuencial completa con todos los juegos activos"""

    def get(self, request, *args, **kwargs):
        print("="*80)
        print("🚀 InitSequentialEvaluationView LLAMADA")
        print("="*80)
        
        # Obtener nino_id del querystring
        nino_id = request.GET.get('nino_id')
        print(f"📌 nino_id recibido: {nino_id}")

        if not nino_id:
            messages.error(request, "ID de niño no proporcionado.")
            print("❌ ERROR: No se proporcionó nino_id")
            return redirect('games:game_list')

        try:
            nino_id = int(nino_id)
            print(f"✅ nino_id convertido a int: {nino_id}")
        except (ValueError, TypeError):
            messages.error(request, "ID de niño inválido.")
            print(f"❌ ERROR: nino_id inválido: {nino_id}")
            return redirect('games:game_list')

        # Verificar que el niño pertenece al profesional actual
        try:
            nino = Nino.objects.get(id=nino_id, profesional=request.user)
            print(f"✅ Niño encontrado: {nino.nombre_completo}")
        except Nino.DoesNotExist:
            messages.error(request, "Niño no encontrado o no autorizado.")
            print(f"❌ ERROR: Niño con ID {nino_id} no encontrado")
            return redirect('games:game_list')

        # Crear nueva evaluación
        print("\n📝 Creando nueva evaluación...")
        evaluacion = Evaluacion.objects.create(
            nino=nino,
            fecha_hora_inicio=timezone.now(),
            estado='en_proceso'
        )
        print(f"✅ Evaluación creada con ID: {evaluacion.id}")

        # Obtener todos los juegos activos ordenados por orden_visualizacion
        print("\n🎮 Obteniendo juegos activos...")
        juegos = Juego.objects.filter(activo=True).order_by('orden_visualizacion')
        print(f"📊 Juegos activos encontrados: {juegos.count()}")

        if not juegos.exists():
            messages.error(request, "No hay juegos activos disponibles.")
            print("❌ ERROR: No hay juegos activos")
            return redirect('games:game_list')

        # Convertir a lista para acceso por índice
        juegos_list = list(juegos)
        num_juegos = len(juegos_list)
        print(f"📋 Lista de juegos ({num_juegos}):")
        for idx, juego in enumerate(juegos_list):
            print(f"   {idx}: {juego.nombre}")

        # SISTEMA DE BUCLE: Crear 32 sesiones rotando los juegos disponibles
        TOTAL_SESIONES = 32
        sesiones_creadas = []
        
        print(f"\n🔄 INICIANDO BUCLE DE CREACIÓN DE {TOTAL_SESIONES} SESIONES...")
        print("="*80)

        for i in range(TOTAL_SESIONES):
            print(f"\n🔄 Iteración {i+1}/{TOTAL_SESIONES} iniciada")
            
            try:
                # Rotar entre los juegos disponibles usando módulo
                juego_index = i % num_juegos
                juego = juegos_list[juego_index]
                
                print(f"   🎯 Juego seleccionado: {juego.nombre} (index {juego_index})")
                
                # Crear sesión
                print(f"   ⏳ Llamando a SesionJuego.crear_nueva_sesion...")
                sesion = SesionJuego.crear_nueva_sesion(
                    evaluacion=evaluacion,
                    juego=juego,
                    nivel=1  # Nivel por defecto
                )
                print(f"   ✅ Sesión creada con ID: {sesion.id}")
                
                # Asignar número de ejercicio global (1-32)
                sesion.ejercicio_numero = i + 1
                sesion.save(update_fields=['ejercicio_numero'])
                print(f"   ✅ ejercicio_numero asignado: {sesion.ejercicio_numero}")
                
                sesiones_creadas.append(sesion)
                
                print(f"✅ Sesión {i+1}/32 creada: {juego.nombre} (ejercicio_numero={sesion.ejercicio_numero})")
                print(f"📊 Sesiones acumuladas: {len(sesiones_creadas)}")
                
            except Exception as e:
                print(f"❌ ERROR creando sesión {i+1}: {e}")
                print(f"🔍 Tipo de error: {type(e).__name__}")
                import traceback
                traceback.print_exc()
                continue

        print("\n" + "="*80)
        print(f"🎯 BUCLE FINALIZADO")
        print(f"📊 Total de sesiones creadas: {len(sesiones_creadas)}/{TOTAL_SESIONES}")
        print("="*80)

        if not sesiones_creadas:
            messages.error(request, "Error al crear las sesiones de juegos.")
            print("❌ FALLO CRÍTICO: No se crearon sesiones")
            return redirect('games:game_list')

        # Redirigir al primer juego
        primera_sesion = sesiones_creadas[0]
        print(f"\n🎮 Redirigiendo al primer juego: {primera_sesion.url_sesion}")
        print("="*80 + "\n")
        
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
        
        # ⭐ AGREGAR ESTAS 2 LÍNEAS AQUÍ:
        # Detectar si es evaluación secuencial de IA (tiene evaluacion Y ejercicio_numero)
        es_evaluacion_ia = sesion.evaluacion is not None and sesion.ejercicio_numero is not None

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
            'es_evaluacion_ia': es_evaluacion_ia,
        })
        
        print(f"=== PlayGameView returning template for game: {sesion.juego.nombre} ===")
        return context

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
        
        from .models import PruebaCognitiva
        
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
def finish_game_session(request, url_sesion):
    """API endpoint para finalizar una sesión de juego"""
    try:
        # Obtener la sesión
        sesion = get_object_or_404(SesionJuego, url_sesion=url_sesion)
        
        # Parsear datos del POST
        data = json.loads(request.body)
        puntaje_final = data.get('total_score', sesion.puntaje_total)
        total_correct = data.get('total_correct', 0)
        total_incorrect = data.get('total_incorrect', 0)
        preguntas_contestadas = total_correct + total_incorrect
        tiempo_total = data.get('total_time_seconds', 0)

        # === CALCULAR MÉTRICAS AGREGADAS ===
        # Opción 1: Si el frontend envía las métricas directamente
        clicks_total = data.get('total_clicks', preguntas_contestadas)
        hits_total = data.get('total_hits', total_correct)
        misses_total = data.get('total_misses', total_incorrect)

        # Opción 2: Si no las envía, calcularlas desde PruebaCognitiva
        if clicks_total == 0 or hits_total == 0:
            metricas = sesion.calcular_metricas_desde_pruebas()
            clicks_total = metricas['clicks']
            hits_total = metricas['hits']
            misses_total = metricas['misses']
            print(f"📊 Métricas calculadas desde PruebaCognitiva: {metricas}")

        # Finalizar sesión con métricas agregadas
        sesion.finalizar_sesion(
            puntaje_final=puntaje_final,
            preguntas_contestadas=preguntas_contestadas,
            tiempo_total=tiempo_total,
            clicks=clicks_total,
            hits=hits_total,
            misses=misses_total
        )

        print(f"✅ Sesión finalizada - Ejercicio #{sesion.ejercicio_numero}: Clicks={clicks_total}, Hits={hits_total}, Misses={misses_total}")
        
        # Verificar si debemos finalizar la evaluación completa
        evaluacion = sesion.evaluacion
        total_sesiones = SesionJuego.objects.filter(evaluacion=evaluacion).count()
        sesiones_completadas = SesionJuego.objects.filter(evaluacion=evaluacion, estado='completada').count()

        print(f"📊 Progreso: {sesiones_completadas}/{total_sesiones} sesiones completadas")

        # Si todas las sesiones están completadas, finalizar la evaluación
        if sesiones_completadas == total_sesiones:
            evaluacion.fecha_hora_fin = timezone.now()
            evaluacion.estado = 'completada'
            evaluacion.duracion_total_minutos = tiempo_total // 60
            evaluacion.save()
            
            print(f"✅ ¡EVALUACIÓN COMPLETA! Total: {total_sesiones} sesiones")
            
            # === REALIZAR PREDICCIÓN CON MODELO IA ===
            print("\n🤖 Iniciando predicción de dislexia...")
            
            try:
                from .ml_models.predictor import predecir_dislexia_desde_evaluacion
                from app.core.models import ReporteIA
                
                # Realizar predicción
                resultado_prediccion = predecir_dislexia_desde_evaluacion(evaluacion.id)
                
                if resultado_prediccion['success']:
                    pred = resultado_prediccion['prediccion']
                    
                    print(f"✅ Predicción exitosa:")
                    print(f"   - Clasificación: {pred['clasificacion']}")
                    print(f"   - Probabilidad: {pred['probabilidad_porcentaje']}%")
                    print(f"   - Nivel de riesgo: {pred['nivel_riesgo']}")
                    
                    # === GUARDAR RESULTADO EN ReporteIA ===
                    try:
                        # Preparar características en formato JSON
                        caracteristicas_json = {
                            'total_sesiones': total_sesiones,
                            'accuracy_promedio': float(evaluacion.precision_promedio),
                            'total_clicks': evaluacion.total_clics,
                            'total_aciertos': evaluacion.total_aciertos,
                            'total_errores': evaluacion.total_errores,
                            'duracion_minutos': evaluacion.duracion_total_minutos,
                            'modelo_version': resultado_prediccion.get('modelo_info', {}).get('version', 'v2.2'),
                            'umbral_utilizado': pred.get('umbral_utilizado', 0.5)
                        }
                        
                        # Preparar métricas relevantes
                        metricas_relevantes = {
                            'probabilidad': pred['probabilidad'],
                            'probabilidad_porcentaje': pred['probabilidad_porcentaje'],
                            'confianza': pred.get('confianza', 0),
                            'confianza_porcentaje': pred.get('confianza_porcentaje', 0),
                            'nivel_riesgo': pred['nivel_riesgo'],
                            'simulacion': pred.get('simulacion', False)
                        }
                        
                        # Mapear nivel de riesgo a clasificación
                        if pred['nivel_riesgo'] == 'ALTO':
                            clasificacion_riesgo = 'alto'
                        elif pred['nivel_riesgo'] == 'MEDIO':
                            clasificacion_riesgo = 'medio'
                        else:
                            clasificacion_riesgo = 'bajo'
                        
                        # Crear o actualizar ReporteIA
                        reporte, created = ReporteIA.objects.update_or_create(
                            evaluacion=evaluacion,
                            defaults={
                                'indice_riesgo': pred['probabilidad'] * 100,  # Convertir a escala 0-100
                                'clasificacion_riesgo': clasificacion_riesgo,
                                'confianza_prediccion': int(pred.get('confianza_porcentaje', 60)),
                                'caracteristicas_json': caracteristicas_json,
                                'recomendaciones': pred['recomendacion'],
                                'metricas_relevantes': metricas_relevantes
                            }
                        )
                        
                        if created:
                            print(f"✅ ReporteIA creado con ID: {reporte.id}")
                        else:
                            print(f"✅ ReporteIA actualizado con ID: {reporte.id}")
                        
                    except Exception as e:
                        print(f"⚠️ Error al guardar ReporteIA: {e}")
                        import traceback
                        traceback.print_exc()
                
                else:
                    print(f"⚠️ Error en predicción: {resultado_prediccion.get('error', 'Error desconocido')}")
            
            except Exception as e:
                print(f"❌ Error al ejecutar predicción: {e}")
                import traceback
                traceback.print_exc()
            
            # === RETORNAR RESPUESTA ===
            return JsonResponse({
                'success': True,
                'message': '¡Evaluación completa! Predicción de IA realizada.',
                'evaluacion_completada': True,
                'redirect_url': f'/games/results/{evaluacion.id}/',
                'sesion_id': sesion.id,
                'evaluacion_id': evaluacion.id,
                'prediccion_realizada': resultado_prediccion['success'] if 'resultado_prediccion' in locals() else False,
                'final_stats': {
                    'puntaje_total': sesion.puntaje_total,
                    'preguntas_respondidas': sesion.preguntas_respondidas,
                    'tiempo_total_minutos': evaluacion.duracion_total_minutos,
                    'precision_promedio': float(evaluacion.precision_promedio),
                    'sesiones_completadas': sesiones_completadas,
                    'sesiones_totales': total_sesiones
                }
            })
        else:
            # Buscar la siguiente sesión pendiente
            siguiente_sesion = SesionJuego.objects.filter(
                evaluacion=evaluacion,
                estado='en_proceso'
            ).order_by('ejercicio_numero').first()
            
            if siguiente_sesion:
                print(f"➡️ Siguiente juego: {siguiente_sesion.juego.nombre} (Ejercicio #{siguiente_sesion.ejercicio_numero})")
                
                return JsonResponse({
                    'success': True,
                    'message': f'Juego completado. Avanzando al siguiente...',
                    'evaluacion_completada': False,
                    'siguiente_url': f'/games/play/{siguiente_sesion.url_sesion}/',
                    'progreso': {
                        'completadas': sesiones_completadas,
                        'totales': total_sesiones,
                        'porcentaje': round((sesiones_completadas / total_sesiones) * 100, 1)
                    },
                    'sesion_id': sesion.id
                })
            else:
                # No hay siguiente sesión (caso raro)
                return JsonResponse({
                    'success': True,
                    'message': 'Sesión finalizada correctamente',
                    'evaluacion_completada': False,
                    'redirect_url': f'/games/results/{evaluacion.id}/',
                    'sesion_id': sesion.id
                })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required
@require_POST
def finish_individual_game(request, url_sesion):
    """Finalizar juego individual sin predicción IA - Solo marca como completada"""
    try:
        sesion = get_object_or_404(SesionJuego, url_sesion=url_sesion)
        
        # Parsear datos
        data = json.loads(request.body)
        puntaje_final = data.get('total_score', sesion.puntaje_total)
        tiempo_total = data.get('total_time_seconds', 0)
        
        # Marcar como completada
        sesion.estado = 'completada'
        sesion.fecha_fin = timezone.now()
        sesion.puntaje_total = puntaje_final
        sesion.tiempo_total_segundos = tiempo_total
        sesion.save()
        
        print(f"✅ Juego individual finalizado: {sesion.juego.nombre}")
        print(f"   Puntaje: {puntaje_final}, Tiempo: {tiempo_total}s")
        
        return JsonResponse({
            'success': True,
            'message': 'Juego finalizado correctamente',
            'redirect_url': '/games/game-list/'
        })
    
    except Exception as e:
        print(f"❌ Error al finalizar juego individual: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_POST  
def finish_evaluation_game(request, url_sesion):
    """Finalizar juego dentro de evaluación IA - Solo sale sin predecir"""
    try:
        sesion = get_object_or_404(SesionJuego, url_sesion=url_sesion)
        
        # Parsear datos
        data = json.loads(request.body)
        puntaje_final = data.get('total_score', sesion.puntaje_total)
        tiempo_total = data.get('total_time_seconds', 0)
        
        # Marcar como completada
        sesion.estado = 'completada'
        sesion.fecha_fin = timezone.now()
        sesion.puntaje_total = puntaje_final
        sesion.tiempo_total_segundos = tiempo_total
        sesion.save()
        
        evaluacion = sesion.evaluacion
        sesiones_completadas = SesionJuego.objects.filter(
            evaluacion=evaluacion, 
            estado='completada'
        ).count()
        total_sesiones = SesionJuego.objects.filter(evaluacion=evaluacion).count()
        
        print(f"✅ Juego de evaluación finalizado manualmente: {sesion.juego.nombre}")
        print(f"   Progreso: {sesiones_completadas}/{total_sesiones}")
        
        return JsonResponse({
            'success': True,
            'message': f'Juego finalizado. Progreso: {sesiones_completadas}/{total_sesiones}',
            'redirect_url': '/games/session-list/',
            'progreso': {
                'completadas': sesiones_completadas,
                'totales': total_sesiones
            }
        })
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


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
            nino__profesional=self.request.user
        )

        # Obtener todas las sesiones de esta evaluación
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


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect

@login_required
@csrf_protect
@require_POST
def delete_evaluacion(request, evaluacion_id):
    """Vista para eliminar una evaluación completa"""
    
    # ⭐ AGREGAR LOGGING PARA DEBUG
    print(f"🗑️ Vista delete_evaluacion llamada - ID: {evaluacion_id}")
    print(f"👤 Usuario: {request.user}")
    print(f"📍 Path: {request.path}")
    print(f"🌐 Method: {request.method}")
    
    try:
        evaluacion = Evaluacion.objects.get(
            id=evaluacion_id,
            nino__profesional=request.user
        )
        
        nino_nombre = evaluacion.nino.nombre_completo
        print(f"✅ Evaluación encontrada: {nino_nombre}")
        messages.success(request, f'✅ Evaluación de {nino_nombre} eliminada correctamente')
        evaluacion.delete()
        print(f"✅ Evaluación eliminada")
        
        response = JsonResponse({
            'success': True,
            'message': f'Evaluación de {nino_nombre} eliminada correctamente'
        })
        print(f"📤 Retornando JsonResponse")
        return response
    
    except Evaluacion.DoesNotExist:
        print(f"❌ Evaluación no encontrada")
        return JsonResponse({
            'success': False,
            'error': 'Evaluación no encontrada'
        }, status=404)
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)