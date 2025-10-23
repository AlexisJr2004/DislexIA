from django.core.management.base import BaseCommand
import random
from django.utils import timezone
from app.core.models import Nino, Profesional, ReporteIA
from app.games.models import Juego, Evaluacion, SesionJuego, PruebaCognitiva
from app.games.ml_models.predictor import predecir_dislexia_desde_evaluacion

class Command(BaseCommand):
    help = 'Pobla la BD con evaluaciones de bajo rendimiento para probar el modelo de IA'

    def handle(self, *args, **options):
        NUM_JUEGOS = 6
        NUM_SESIONES = 32

        nino = Nino.objects.first()
        profesional = Profesional.objects.first()
        juegos = list(Juego.objects.all()[:NUM_JUEGOS])

        if not nino or not profesional or len(juegos) < NUM_JUEGOS:
            self.stdout.write(self.style.ERROR("Faltan datos base (niño, profesional o juegos)."))
            return

        evaluacion = Evaluacion.objects.create(
            nino=nino,
            fecha_hora_inicio=timezone.now(),
            estado='completada',
            duracion_total_minutos=30,
            total_clics=0,
            total_aciertos=0,
            total_errores=0,
            precision_promedio=0.0,
            dispositivo='PC'
        )

        total_clics = 0
        total_aciertos = 0
        total_errores = 0
        for i in range(1, NUM_SESIONES + 1):
            juego = juegos[(i - 1) % NUM_JUEGOS]
            sesion = SesionJuego.objects.create(
                evaluacion=evaluacion,
                juego=juego,
                ejercicio_numero=i,
                estado='completada',
                fecha_inicio=timezone.now(),
                fecha_fin=timezone.now(),
                puntaje_total=random.randint(1, 3),  # Puntos bajos
                preguntas_respondidas=random.randint(8, 15)
            )
            clics = random.randint(8, 15)
            aciertos = random.randint(1, 3)  # Muy pocos aciertos
            errores = clics - aciertos
            puntaje = aciertos * 1  # Puntos bajos
            PruebaCognitiva.objects.create(
                evaluacion=evaluacion,
                juego=juego,
                numero_prueba=i,
                clics=clics,
                aciertos=aciertos,
                errores=errores,
                puntaje=puntaje,
                precision=(aciertos / clics) * 100 if clics > 0 else 0,
                tasa_error=(errores / clics) * 100 if clics > 0 else 0,
                tiempo_respuesta_ms=random.randint(2000, 4000)
            )
            total_clics += clics
            total_aciertos += aciertos
            total_errores += errores
        for sesion in SesionJuego.objects.filter(evaluacion=evaluacion):
            sesion.calcular_metricas_desde_pruebas()
        evaluacion.total_clics = total_clics
        evaluacion.total_aciertos = total_aciertos
        evaluacion.total_errores = total_errores
        evaluacion.precision_promedio = (total_aciertos / total_clics) * 100 if total_clics > 0 else 0
        evaluacion.save()

        resultado = predecir_dislexia_desde_evaluacion(evaluacion.id)
        print("=== Resultado del predictor ===")
        print(resultado)
        if not hasattr(evaluacion, 'reporte_ia'):
            pred = resultado.get('prediccion', {})
            ReporteIA.objects.create(
                evaluacion=evaluacion,
                indice_riesgo=pred.get('probabilidad', 0),
                clasificacion_riesgo=pred.get('nivel_riesgo', 'bajo').lower(),
                confianza_prediccion=int(pred.get('confianza_porcentaje', pred.get('confianza', 0) * 100)),
                caracteristicas_json=resultado.get('features', {}),
                recomendaciones=pred.get('recomendacion', ''),
                metricas_relevantes=resultado.get('modelo_info', {}).get('metricas', {}),
            )
            self.stdout.write(self.style.SUCCESS("Reporte IA generado y guardado."))
        else:
            self.stdout.write(self.style.WARNING("La evaluación ya tiene un reporte IA."))

        self.stdout.write(self.style.SUCCESS(f"Evaluación de bajo rendimiento creada para el niño {nino.nombres} ({nino.id})"))