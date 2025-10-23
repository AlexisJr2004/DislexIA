from django.core.management.base import BaseCommand
import random
from django.utils import timezone
from app.core.models import Nino, Profesional, ReporteIA
from app.games.models import Juego, Evaluacion, SesionJuego, PruebaCognitiva
from app.games.ml_models.predictor import predecir_dislexia_desde_evaluacion
import os

class Command(BaseCommand):
    help = 'Pobla la BD con evaluaciones realistas para probar el modelo de IA'

    def add_arguments(self, parser):
        parser.add_argument(
            '--riesgo', 
            type=str, 
            choices=['alto', 'medio', 'bajo'], 
            default='medio',
            help='Nivel de riesgo a simular (alto, medio, bajo)'
        )

    def handle(self, *args, **options):
        riesgo = options['riesgo']

        nino = Nino.objects.first()
        profesional = Profesional.objects.first()

        if not nino or not profesional:
            self.stdout.write(self.style.ERROR("Faltan datos base (niño o profesional)."))
            return

        # ====================================================================
        # MAPEO CORRECTO DE JUEGOS (por nombre exacto)
        # ====================================================================
        # Según tus datos reales, el orden es:
        JUEGOS_ORDEN = [
            "Completa la Palabra",           # Juego 1
            "Encuentra el Error",             # Juego 2
            "Escribe el Nombre del Objeto",  # Juego 3
            "Ordenar Palabras",               # Juego 4
            "Palabra que Escuches",           # Juego 5
            "Selecciona la Palabra Correcta" # Juego 6
        ]

        # Obtener juegos en el orden correcto
        juegos_dict = {juego.nombre: juego for juego in Juego.objects.all()}
        juegos = []
        
        for nombre in JUEGOS_ORDEN:
            if nombre in juegos_dict:
                juegos.append(juegos_dict[nombre])
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ Juego '{nombre}' no encontrado en BD"))
        
        if len(juegos) < 6:
            self.stdout.write(self.style.ERROR(f"❌ Solo se encontraron {len(juegos)}/6 juegos necesarios"))
            return

        self.stdout.write(self.style.SUCCESS(f"\n✅ Juegos cargados en orden:"))
        for idx, juego in enumerate(juegos, 1):
            self.stdout.write(f"   {idx}. {juego.nombre}")

        # ====================================================================
        # CREAR EVALUACIÓN
        # ====================================================================
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

        # ====================================================================
        # CONFIGURACIÓN POR PERFIL
        # ====================================================================
        # Cada tupla: (precisión_objetivo, clicks_por_sesion, num_sesiones)
        PERFILES = {
            'alto': [
                (15, 5, 5),   # 15% = 1 acierto de cada 5-6 intentos
                (10, 5, 5),   # 10% = CRÍTICO, casi todo mal
                (12, 5, 6),   # 12% = muy bajo
                (18, 5, 5),   # 18% = bajo
                (20, 5, 5),   # 20% = bajo
                (8, 5, 6),    # 8% = PEOR juego, casi todo mal
            ],
            'medio': [
                (96, 5, 5),   # Completa la Palabra - 96% (TUS DATOS REALES)
                (80, 5, 5),   # Encuentra el Error - 80%
                (96, 5, 6),   # Escribe Objeto - 96.7%
                (84, 5, 5),   # Ordenar Palabras - 84%
                (76, 5, 5),   # Palabra que Escuches - 76%
                (20, 5, 6),   # Selecciona Correcta - 20%
            ],
            'bajo': [
                (95, 5, 5),   # Excelente rendimiento
                (92, 5, 5),
                (96, 5, 6),
                (90, 5, 5),
                (88, 5, 5),
                (94, 5, 6),
            ],
        }

        perfil_seleccionado = PERFILES[riesgo]
        
        total_clics = 0
        total_aciertos = 0
        total_errores = 0
        ejercicio_global = 1

        self.stdout.write(self.style.SUCCESS(f"\n{'='*70}"))
        self.stdout.write(self.style.SUCCESS(f"Generando evaluación con perfil: {riesgo.upper()}"))
        self.stdout.write(self.style.SUCCESS(f"{'='*70}\n"))

        # ====================================================================
        # GENERAR SESIONES
        # ====================================================================
        for juego_idx, juego in enumerate(juegos):
            precision_objetivo, clicks_por_sesion, num_sesiones = perfil_seleccionado[juego_idx]
            
            self.stdout.write(f"\n📚 {juego.nombre}")
            self.stdout.write(f"   Sesiones: {num_sesiones}x | Clicks/sesión: {clicks_por_sesion} | Precisión objetivo: {precision_objetivo}%")
            
            sesion_aciertos_totales = 0
            sesion_clics_totales = 0

            for sesion_num in range(1, num_sesiones + 1):
                # Variación aleatoria pequeña (±3%) para realismo
                variacion = random.uniform(-3, 3)
                precision_real = max(0, min(100, precision_objetivo + variacion))
                
                clics = clicks_por_sesion
                aciertos = int(clics * (precision_real / 100))
                aciertos = max(0, min(aciertos, clics))
                errores = clics - aciertos
                puntaje = aciertos * 10

                # Crear sesión
                sesion = SesionJuego.objects.create(
                    evaluacion=evaluacion,
                    juego=juego,
                    ejercicio_numero=ejercicio_global,
                    estado='completada',
                    fecha_inicio=timezone.now(),
                    fecha_fin=timezone.now(),
                    puntaje_total=puntaje,
                    preguntas_respondidas=clics,
                    # ⭐ INICIALIZAR MÉTRICAS AGREGADAS DIRECTAMENTE
                    clicks_total=clics,
                    hits_total=aciertos,
                    misses_total=errores,
                    score_total=puntaje,
                    accuracy_percent=(aciertos / clics) * 100 if clics > 0 else 0,
                    missrate_percent=(errores / clics) * 100 if clics > 0 else 0
                )

                # Crear prueba cognitiva
                PruebaCognitiva.objects.create(
                    evaluacion=evaluacion,
                    juego=juego,
                    numero_prueba=ejercicio_global,
                    clics=clics,
                    aciertos=aciertos,
                    errores=errores,
                    puntaje=puntaje,
                    precision=(aciertos / clics) * 100 if clics > 0 else 0,
                    tasa_error=(errores / clics) * 100 if clics > 0 else 0,
                    tiempo_respuesta_ms=random.randint(1500, 3500)
                )

                sesion_aciertos_totales += aciertos
                sesion_clics_totales += clics
                total_clics += clics
                total_aciertos += aciertos
                total_errores += errores
                ejercicio_global += 1

            # Resumen del juego
            precision_juego = (sesion_aciertos_totales / sesion_clics_totales * 100) if sesion_clics_totales > 0 else 0
            self.stdout.write(self.style.SUCCESS(
                f"   ✓ {sesion_clics_totales} clicks | {sesion_aciertos_totales} aciertos | "
                f"{precision_juego:.1f}% precisión real"
            ))

        # ====================================================================
        # ACTUALIZAR MÉTRICAS
        # ====================================================================
        # Ya no es necesario llamar a calcular_metricas_desde_pruebas()
        # porque las métricas ya se inicializaron en el create()

        evaluacion.total_clics = total_clics
        evaluacion.total_aciertos = total_aciertos
        evaluacion.total_errores = total_errores
        evaluacion.precision_promedio = (total_aciertos / total_clics) * 100 if total_clics > 0 else 0
        evaluacion.save()

        # ====================================================================
        # RESUMEN FINAL
        # ====================================================================
        self.stdout.write(f"\n{'='*70}")
        self.stdout.write(self.style.WARNING("📊 RESUMEN FINAL DE LA EVALUACIÓN"))
        self.stdout.write(f"{'='*70}")
        self.stdout.write(f"Total Clicks:    {total_clics}")
        self.stdout.write(f"Total Aciertos:  {total_aciertos}")
        self.stdout.write(f"Total Errores:   {total_errores}")
        self.stdout.write(f"Precisión:       {evaluacion.precision_promedio:.1f}%")
        self.stdout.write(f"Total Sesiones:  {ejercicio_global - 1}")
        
        # Mostrar comparación con datos reales (solo para perfil medio)
        if riesgo == 'medio':
            self.stdout.write(f"\n{'='*70}")
            self.stdout.write(self.style.WARNING("🎯 COMPARACIÓN CON DATOS REALES"))
            self.stdout.write(f"{'='*70}")
            self.stdout.write(f"Esperado:  160 clicks | 119 aciertos | 74.4%")
            self.stdout.write(f"Obtenido:  {total_clics} clicks | {total_aciertos} aciertos | {evaluacion.precision_promedio:.1f}%")
            
            diff_clicks = abs(total_clics - 160)
            diff_aciertos = abs(total_aciertos - 119)
            diff_precision = abs(evaluacion.precision_promedio - 74.4)
            
            if diff_clicks <= 5 and diff_aciertos <= 5 and diff_precision <= 2:
                self.stdout.write(self.style.SUCCESS("✅ VALORES REALISTAS GENERADOS CORRECTAMENTE"))
            else:
                self.stdout.write(self.style.WARNING("⚠️ Hay diferencias significativas con los datos reales"))
        
        self.stdout.write(f"{'='*70}\n")

        # ====================================================================
        # PREDICCIÓN IA
        # ====================================================================
        self.stdout.write(self.style.SUCCESS("🤖 Ejecutando predicción con IA...\n"))
        
        # ⭐ VERIFICAR DATOS ANTES DE PREDECIR
        self.stdout.write(f"\n{'='*70}")
        self.stdout.write(self.style.WARNING("🔍 VERIFICACIÓN PRE-PREDICCIÓN"))
        self.stdout.write(f"{'='*70}")
        
        sesiones_verificacion = SesionJuego.objects.filter(evaluacion=evaluacion).order_by('ejercicio_numero')
        self.stdout.write(f"Total sesiones creadas: {sesiones_verificacion.count()}")
        
        # Mostrar primeras 3 sesiones
        for idx, s in enumerate(sesiones_verificacion[:3], 1):
            self.stdout.write(f"\nSesión {idx} (Ejercicio #{s.ejercicio_numero}):")
            self.stdout.write(f"  Juego: {s.juego.nombre}")
            self.stdout.write(f"  clicks_total: {s.clicks_total}")
            self.stdout.write(f"  hits_total: {s.hits_total}")
            self.stdout.write(f"  misses_total: {s.misses_total}")
            self.stdout.write(f"  accuracy_percent: {s.accuracy_percent}%")
        
        if sesiones_verificacion.count() > 3:
            self.stdout.write(f"\n... y {sesiones_verificacion.count() - 3} sesiones más")
        
        self.stdout.write(f"\n{'='*70}\n")
        
        resultado = predecir_dislexia_desde_evaluacion(evaluacion.id)
        
        if resultado.get('success'):
            pred = resultado.get('prediccion', {})
            
            self.stdout.write(f"\n{'='*70}")
            self.stdout.write(self.style.WARNING("🧠 RESULTADO DE PREDICCIÓN IA"))
            self.stdout.write(f"{'='*70}")
            self.stdout.write(f"Clasificación:   {pred.get('clasificacion', 'N/A')}")
            self.stdout.write(f"Riesgo:          {pred.get('nivel_riesgo', 'N/A')}")
            self.stdout.write(f"Probabilidad:    {pred.get('probabilidad_porcentaje', 0):.1f}%")
            self.stdout.write(f"Confianza:       {pred.get('confianza_porcentaje', 0):.1f}%")
            self.stdout.write(f"{'='*70}\n")

            # Crear reporte IA
            if not hasattr(evaluacion, 'reporte_ia'):
                ReporteIA.objects.create(
                    evaluacion=evaluacion,
                    indice_riesgo=pred.get('probabilidad', 0),
                    clasificacion_riesgo=pred.get('nivel_riesgo', 'bajo').lower(),
                    confianza_prediccion=int(pred.get('confianza_porcentaje', pred.get('confianza', 0) * 100)),
                    caracteristicas_json=resultado.get('features', {}),
                    recomendaciones=pred.get('recomendacion', ''),
                    metricas_relevantes=resultado.get('modelo_info', {}).get('metricas', {}),
                )
                self.stdout.write(self.style.SUCCESS("✓ Reporte IA generado y guardado\n"))
        else:
            self.stdout.write(self.style.ERROR(f"✗ Error en predicción: {resultado.get('error', 'Desconocido')}\n"))

        self.stdout.write(self.style.SUCCESS(
            f"✅ Evaluación completada para {nino.nombres} (ID: {evaluacion.id})"
        ))