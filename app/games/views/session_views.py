from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib import messages
import json
from app.core.models import Nino, ReporteIA
from app.games.models import Juego, SesionJuego, Evaluacion
from app.games.ml_models.predictor import predecir_dislexia_desde_evaluacion
from django.core.management import call_command
from app.games.forms.forms_populate import PopulateSessionsForm

@method_decorator(login_required, name='dispatch')
class GameSessionListView(TemplateView):
    """Vista para listar las sesiones de juegos del profesional autenticado"""
    template_name = 'game_session_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        profesional = self.request.user
        
        # ⭐ Solo obtener filtro de estado (sin búsqueda)
        filtro_estado = self.request.GET.get('estado', 'todos')
        
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
        # Agregar el formulario de populate al contexto
        from app.games.forms.forms_populate import PopulateSessionsForm
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
            'form_populate': PopulateSessionsForm(),
        })
        
        return context

@method_decorator(login_required, name='dispatch')
class InitSequentialEvaluationView(View):

    def get(self, request, *args, **kwargs):
        nino_id = request.GET.get('nino_id')

        if not nino_id:
            messages.error(request, "ID de niño no proporcionado.")
            return redirect('games:session_list')

        try:
            nino_id = int(nino_id)
        except (ValueError, TypeError):
            messages.error(request, "ID de niño inválido.")
            return redirect('games:session_list')

        try:
            nino = Nino.objects.get(id=nino_id, profesional=request.user)
        except Nino.DoesNotExist:
            messages.error(request, "Niño no encontrado o no autorizado.")
            return redirect('games:session_list')

        sesion_activa = Evaluacion.objects.filter(
            nino=nino,
            estado='en_proceso'
        ).first()
        
        if sesion_activa:
            messages.warning(
                request, 
                f'El niño {nino.nombre_completo} ya tiene una sesión de evaluación activa iniciada el '
                f'{sesion_activa.fecha_hora_inicio.strftime("%d/%m/%Y a las %H:%M")}. '
                f'Puedes continuar con la sesión existente o cancelarla para crear una nueva.'
            )
            return redirect('games:session_list')

        evaluacion = Evaluacion.objects.create(
            nino=nino,
            fecha_hora_inicio=timezone.now(),
            estado='en_proceso',
            dispositivo=request.META.get('HTTP_USER_AGENT', '')[:50]
        )

        juegos = Juego.objects.filter(activo=True).order_by('orden_visualizacion')

        if not juegos.exists():
            messages.error(request, "No hay juegos activos disponibles.")
            return redirect('games:session_list')

        juegos_list = list(juegos)
        num_juegos = len(juegos_list)

        TOTAL_SESIONES = 32
        sesiones_creadas = []

        for i in range(TOTAL_SESIONES):
            try:
                juego_index = i % num_juegos
                juego = juegos_list[juego_index]
                
                sesion = SesionJuego.crear_nueva_sesion(
                    evaluacion=evaluacion,
                    juego=juego,
                    nivel=1
                )
                
                sesion.ejercicio_numero = i + 1
                sesion.save(update_fields=['ejercicio_numero'])
                
                sesiones_creadas.append(sesion)
                
            except Exception as e:
                import traceback
                traceback.print_exc()
                continue

        if not sesiones_creadas:
            messages.error(request, "Error al crear las sesiones de juegos.")
            return redirect('games:game_list')

        primera_sesion = sesiones_creadas[0]
        
        messages.success(
            request,
            f'¡Evaluación iniciada para {nino.nombre_completo}! '
            f'Se han creado {len(sesiones_creadas)} juegos. Comenzando con el primer juego.'
        )
        
        return redirect('games:play_game', url_sesion=primera_sesion.url_sesion)


@method_decorator(login_required, name='dispatch')
class ResumeEvaluationView(View):
    def get(self, request, evaluacion_id, *args, **kwargs):
        try:
            evaluacion = Evaluacion.objects.get(
                id=evaluacion_id,
                nino__profesional=request.user
            )
        except Evaluacion.DoesNotExist:
            messages.error(request, "Evaluación no encontrada o no autorizada.")
            return redirect('games:session_list')

        if evaluacion.estado != 'en_proceso':
            messages.warning(
                request, 
                f"Esta evaluación ya está {evaluacion.get_estado_display()}. "
                f"No se puede continuar una evaluación que no está en proceso."
            )
            return redirect('games:session_list')

        sesion_pendiente = SesionJuego.objects.filter(
            evaluacion=evaluacion
        ).exclude(
            estado='completada'
        ).order_by('ejercicio_numero').first()

        total_sesiones = SesionJuego.objects.filter(evaluacion=evaluacion).count()
        sesiones_completadas = SesionJuego.objects.filter(
            evaluacion=evaluacion, 
            estado='completada'
        ).count()

        if not sesion_pendiente:
            if total_sesiones > 0 and sesiones_completadas == total_sesiones:
                evaluacion.estado = 'completada'
                evaluacion.fecha_hora_fin = timezone.now()
                evaluacion.save()
                messages.success(request, "¡Evaluación completada! Todas las sesiones han sido finalizadas.")
            else:
                messages.info(request, "No hay sesiones pendientes en esta evaluación.")
            
            return redirect('games:sequential_results', evaluacion_id=evaluacion.id)
        
        messages.success(
            request,
            f'Continuando evaluación de {evaluacion.nino.nombre_completo}. '
            f'Progreso actual: {sesion_pendiente.ejercicio_numero}/{total_sesiones}'
        )
        return redirect('games:play_game', url_sesion=sesion_pendiente.url_sesion)


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
                
                # Realizar predicción
                resultado_prediccion = predecir_dislexia_desde_evaluacion(evaluacion.id)
                
                if resultado_prediccion['success']:
                    pred = resultado_prediccion['prediccion']
                    
                    print(f"✅ Predicción exitosa:")
                    print(f"   - Clasificación: {pred['clasificacion']}")
                    print(f"   - Probabilidad: {pred['probabilidad_porcentaje']}%")
                    print(f"   - Nivel de riesgo: {pred['clasificacion_riesgo']}")
                    
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
                            'nivel_riesgo': pred['clasificacion_riesgo'],
                            'simulacion': pred.get('simulacion', False)
                        }
                        
                        # Mapear nivel de riesgo a clasificación
                        if pred['clasificacion_riesgo'] == 'ALTO':
                            clasificacion_riesgo = 'alto'
                        elif pred['clasificacion_riesgo'] == 'MEDIO':
                            clasificacion_riesgo = 'medio'
                        else:
                            clasificacion_riesgo = 'bajo'
                        
                        # Crear o actualizar ReporteIA
                        reporte, created = ReporteIA.objects.update_or_create(
                            evaluacion=evaluacion,
                            defaults={
                                'indice_riesgo': pred['probabilidad'] * 100,  # Convertir a escala 0-100
                                'clasificacion_riesgo': pred['clasificacion_riesgo'],
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

def delete_evaluacion(request, evaluacion_id):
    """
    Eliminar o interrumpir una evaluación.
    - Si está 'en_proceso': La marca como 'interrumpida'
    - Si está 'completada' o 'interrumpida': La elimina físicamente
    """
    try:
        evaluacion = Evaluacion.objects.get(
            id=evaluacion_id,
            nino__profesional=request.user
        )
        
        nino_nombre = evaluacion.nino.nombre_completo
        estado_actual = evaluacion.estado
        
        if estado_actual == 'en_proceso':
            evaluacion.estado = 'interrumpida'
            evaluacion.fecha_hora_fin = timezone.now()
            evaluacion.save()
            
            messages.warning(
                request, 
                f'Sesión de {nino_nombre} marcada como interrumpida.'
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Sesión de {nino_nombre} interrumpida correctamente',
                'action': 'interrupted',
                'evaluacion_id': evaluacion.id,
                'estado_final': evaluacion.estado
            })
        else:
            messages.success(request, f'Evaluación de {nino_nombre} eliminada correctamente')
            evaluacion.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Evaluación de {nino_nombre} eliminada correctamente',
                'action': 'deleted',
                'evaluacion_id': evaluacion_id
            })
    
    except Evaluacion.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Evaluación no encontrada'
        }, status=404)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
    
@login_required
def ejecutar_populate_sessions(request):
    form = PopulateSessionsForm(request.POST)
    if form.is_valid():
        riesgo = form.cleaned_data['riesgo']
        try:
            call_command('populate_sessions', riesgo=riesgo)
            messages.success(request, 'Comando ejecutado correctamente.')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    else:
        messages.error(request, f'Formulario inválido. {form.errors}')
    return redirect('games:session_list')