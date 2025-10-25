from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Sum
from django.utils import timezone

# Importar constantes globales y específicas
from config.constants import DIFICULTAD_CHOICES, ESTADO_CHOICES, COLOR_CHOICES, COLOR_GRADIENTE_MAP
from .constants import (
    CATEGORIAS_JUEGO_CHOICES,
    JUEGO_DEFAULTS,
    PUNTUACION_MIN,
    PUNTUACION_MAX,
    PRECISION_MIN,
    PRECISION_MAX
)

class Juego(models.Model):
    """Modelo para gestionar los diferentes tipos de juegos disponibles"""
    
    nombre = models.CharField(
        max_length=100, 
        verbose_name="Nombre del Juego",
        help_text="Nombre único y descriptivo del juego"
    )
    descripcion = models.TextField(
        verbose_name="Descripción",
        help_text="Descripción detallada de cómo se juega y qué habilidades desarrolla"
    )
    categoria = models.CharField(
        max_length=50,
        choices=CATEGORIAS_JUEGO_CHOICES,
        verbose_name="Categoría del Juego",
        help_text="Categoría general del juego (ej: Reconocimiento Visual, Comprensión Auditiva)"
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name="Identificador URL",
        help_text="Identificador único para la URL del juego (se genera automáticamente)"
    )
    imagen = models.ImageField(
        upload_to='games/',
        verbose_name="Imagen del Juego",
        help_text="Imagen que se mostrará en la card del juego",
        default='games/default_game_image.png'
    )
    dificultad = models.CharField(
        max_length=20,
        choices=DIFICULTAD_CHOICES,
        default=JUEGO_DEFAULTS['dificultad'],
        verbose_name="Dificultad"
    )
    color_tema = models.CharField(
        max_length=20,
        choices=COLOR_CHOICES,
        default=JUEGO_DEFAULTS['color_tema'],
        verbose_name="Color del Tema",
        help_text="Color principal que se usará en la card del juego"
    )
    duracion_estimada_minutos = models.PositiveIntegerField(
        default=JUEGO_DEFAULTS['duracion_estimada_minutos'],
        verbose_name="Duración Estimada (minutos)"
    )
    puntuacion_promedio = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=JUEGO_DEFAULTS['puntuacion_promedio'],
        validators=[MinValueValidator(PUNTUACION_MIN), MaxValueValidator(PUNTUACION_MAX)],
        verbose_name="Puntuación Promedio (1-5 estrellas)"
    )
    activo = models.BooleanField(default=JUEGO_DEFAULTS['activo'], verbose_name="Activo")
    orden_visualizacion = models.PositiveIntegerField(
        default=JUEGO_DEFAULTS['orden_visualizacion'],
        verbose_name="Orden de Visualización",
        help_text="Orden en que aparecerá el juego en la lista (menor número = primero)"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    
    # Estadísticas del juego (se calculan automáticamente)
    total_jugadas = models.PositiveIntegerField(default=JUEGO_DEFAULTS['total_jugadas'], verbose_name="Total de Jugadas")
    total_completados = models.PositiveIntegerField(default=JUEGO_DEFAULTS['total_completados'], verbose_name="Total Completados")
    
    class Meta:
        verbose_name = "Juego"
        verbose_name_plural = "Juegos"
        ordering = ['orden_visualizacion', 'nombre']
        
    def __str__(self):
        return self.nombre

    @property
    def porcentaje_completado(self):
        """Calcula el porcentaje de juegos completados vs jugadas"""
        if self.total_jugadas > 0:
            return round((self.total_completados / self.total_jugadas) * 100)
        return 0
    
    @property
    def color_gradiente_inicio(self):
        """Retorna el color de inicio del gradiente según el color tema"""
        return COLOR_GRADIENTE_MAP.get(self.color_tema, COLOR_GRADIENTE_MAP['purple'])['inicio']
    
    @property
    def color_gradiente_fin(self):
        """Retorna el color de fin del gradiente según el color tema"""
        return COLOR_GRADIENTE_MAP.get(self.color_tema, COLOR_GRADIENTE_MAP['purple'])['fin']
    
    @classmethod
    def por_categoria(cls, categoria):
        """Retorna todos los juegos activos de una categoría específica"""
        return cls.objects.filter(categoria=categoria, activo=True).order_by('orden_visualizacion')
    
    @classmethod
    def categorias_disponibles(cls):
        """Retorna las categorías que tienen juegos activos"""
        return cls.objects.filter(activo=True).values_list('categoria', flat=True).distinct()
    
    @property
    def categoria_display(self):
        """Retorna el nombre legible de la categoría"""
        return dict(CATEGORIAS_JUEGO_CHOICES).get(self.categoria, self.categoria)
    
    def save(self, *args, **kwargs):
        """Override save para generar automáticamente el slug"""
        from django.utils.text import slugify
        import re
        
        # Verificar si el nombre ha cambiado (para regenerar el slug)
        regenerar_slug = False
        if self.pk:
            try:
                old_instance = Juego.objects.get(pk=self.pk)
                if old_instance.nombre != self.nombre:
                    regenerar_slug = True
            except Juego.DoesNotExist:
                regenerar_slug = True
        
        # Generar o regenerar slug si es necesario
        if not self.slug or regenerar_slug:
            # Generar slug base limpio
            base_slug = slugify(self.nombre)
            # Remover caracteres especiales y normalizar
            base_slug = re.sub(r'[^\w\s-]', '', base_slug).strip()
            base_slug = re.sub(r'[-\s]+', '-', base_slug)
            
            slug = base_slug
            counter = 1
            
            # Asegurar que el slug sea único
            while Juego.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug
        
        super().save(*args, **kwargs)
    
    def generar_url_sesion(self, evaluacion_id):
        """
        Genera una URL única para una sesión específica de juego
        Esto permite que el mismo niño juegue el mismo juego múltiples veces
        con URLs diferentes para cada sesión/evaluación
        """
        import uuid
        session_token = str(uuid.uuid4())[:8]  # 8 caracteres únicos
        return f"{self.slug}-eval-{evaluacion_id}-{session_token}"
    
    @classmethod
    def obtener_por_url_sesion(cls, url_sesion):
        """
        Obtiene un juego basado en su URL de sesión
        Extrae el slug del juego de la URL de sesión
        """
        try:
            # Extraer el slug base de la URL de sesión
            # Formato: "slug-eval-123-abc12345"
            slug_base = url_sesion.split('-eval-')[0]
            return cls.objects.get(slug=slug_base, activo=True)
        except (cls.DoesNotExist, IndexError):
            return None
    
    @property
    def archivo_configuracion(self):
        """
        Retorna el nombre del archivo JSON de configuración basado en el slug
        El archivo se genera automáticamente: slug + '.json'
        """
        return f"{self.slug}.json"
    
    @property
    def ruta_archivo_configuracion(self):
        """
        Retorna la ruta completa del archivo JSON de configuración
        """
        return f"app/games/static/data/{self.archivo_configuracion}"
    
    @property
    def url_archivo_configuracion(self):
        """
        Retorna la URL del archivo JSON para uso en el frontend
        """
        return f"/static/data/{self.archivo_configuracion}"
    
    def archivo_configuracion_existe(self):
        """
        Verifica si el archivo JSON de configuración existe
        """
        import os
        from django.conf import settings
        
        ruta_completa = os.path.join(settings.BASE_DIR, self.ruta_archivo_configuracion)
        return os.path.exists(ruta_completa)
    
    def crear_archivo_configuracion_template(self):
        """
        Crea un archivo JSON template básico si no existe
        """
        import json
        import os
        from django.conf import settings
        
        if self.archivo_configuracion_existe():
            return False  # Ya existe
        
        # Template básico
        template = {
            "game_info": {
                "game_slug": self.slug,
                "json_version": "1.0",
                "total_questions": 0,
                "created_date": "2025-10-08",
                "last_updated": "2025-10-08"
            },
            "levels": [],
            "scoring": {
                "correct_answer": 10,
                "time_bonus": 5,
                "perfect_level": 50
            },
            "confusion_types": {
                "inversion_letras": "Inversión de letras (b/d, p/q)",
                "sustitucion_letras": "Sustitución de letras similares (m/n, r/l)",
                "inversion_silabas": "Inversión de sílabas",
                "omision_letras": "Omisión de letras"
            }
        }
        
        # Crear directorio si no existe
        ruta_directorio = os.path.join(settings.BASE_DIR, "app", "games", "static", "data")
        os.makedirs(ruta_directorio, exist_ok=True)
        
        # Crear archivo
        ruta_completa = os.path.join(settings.BASE_DIR, self.ruta_archivo_configuracion)
        with open(ruta_completa, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        
        return True  # Archivo creado

class Evaluacion(models.Model):
    """Modelo para evaluaciones cognitivas realizadas a los niños"""
    
    # Relación con el niño (desde core)
    nino = models.ForeignKey(
        'core.Nino',
        on_delete=models.CASCADE,
        related_name='evaluaciones',
        verbose_name="Niño"
    )
    
    fecha_hora_inicio = models.DateTimeField(verbose_name="Fecha y Hora de Inicio")
    fecha_hora_fin = models.DateTimeField(null=True, blank=True, verbose_name="Fecha y Hora de Fin")
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='en_proceso',
        verbose_name="Estado"
    )
    duracion_total_minutos = models.PositiveIntegerField(
        null=True, 
        blank=True,
        verbose_name="Duración Total (minutos)"
    )
    total_clics = models.PositiveIntegerField(default=0, verbose_name="Total de Clics")
    total_aciertos = models.PositiveIntegerField(default=0, verbose_name="Total de Aciertos")
    total_errores = models.PositiveIntegerField(default=0, verbose_name="Total de Errores")
    precision_promedio = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(PRECISION_MIN), MaxValueValidator(PRECISION_MAX)],
        verbose_name="Precisión Promedio (%)"
    )
    dispositivo = models.CharField(max_length=50, blank=True, verbose_name="Dispositivo")
    
    class Meta:
        verbose_name = "Evaluación"
        verbose_name_plural = "Evaluaciones"
        ordering = ['-fecha_hora_inicio']
        
    def __str__(self):
        return f"Evaluación {self.id} - {self.nino.nombre_completo} ({self.estado})"
    
    @property
    def tasa_aciertos(self):
        """Calcula la tasa de aciertos"""
        if self.total_clics > 0:
            return (self.total_aciertos / self.total_clics) * 100
        return 0
    
    @property
    def tasa_errores(self):
        """Calcula la tasa de errores"""
        if self.total_clics > 0:
            return (self.total_errores / self.total_clics) * 100
        return 0
    
    def calcular_duracion(self):
        """Calcula la duración de la evaluación si está completada"""
        if self.fecha_hora_fin and self.fecha_hora_inicio:
            delta = self.fecha_hora_fin - self.fecha_hora_inicio
            return delta.total_seconds() / 60  # Retorna en minutos
        return None

class PruebaCognitiva(models.Model):
    """Modelo para pruebas cognitivas individuales dentro de una evaluación"""
    
    evaluacion = models.ForeignKey(
        Evaluacion,
        on_delete=models.CASCADE,
        related_name='pruebas_cognitivas',
        verbose_name="Evaluación"
    )
    juego = models.ForeignKey(
        Juego,
        on_delete=models.CASCADE,
        related_name='pruebas_realizadas',
        verbose_name="Juego"
    )
    
    numero_prueba = models.PositiveIntegerField(verbose_name="Número de Prueba")
    clics = models.PositiveIntegerField(default=0, verbose_name="Clics")
    aciertos = models.PositiveIntegerField(default=0, verbose_name="Aciertos")
    errores = models.PositiveIntegerField(default=0, verbose_name="Errores")
    puntaje = models.IntegerField(default=0, verbose_name="Puntaje")
    precision = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(PRECISION_MIN), MaxValueValidator(PRECISION_MAX)],
        verbose_name="Precisión (%)"
    )
    tasa_error = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(PRECISION_MIN), MaxValueValidator(PRECISION_MAX)],
        verbose_name="Tasa de Error (%)"
    )
    tiempo_respuesta_ms = models.PositiveIntegerField(
        verbose_name="Tiempo de Respuesta (ms)",
        help_text="Tiempo promedio de respuesta en milisegundos"
    )
    fecha_ejecucion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Ejecución")
    
    class Meta:
        verbose_name = "Prueba Cognitiva"
        verbose_name_plural = "Pruebas Cognitivas"
        ordering = ['evaluacion', 'numero_prueba']
        unique_together = ['evaluacion', 'juego', 'numero_prueba']
        
    def __str__(self):
        juego_nombre = self.juego.nombre if self.juego else "Sin Juego Asignado"
        return f"Prueba {self.numero_prueba} - {juego_nombre} (Eval: {self.evaluacion.id})"
    
    def save(self, *args, **kwargs):
        """Override save para calcular automáticamente precisión y tasa de error"""
        if self.clics > 0:
            self.precision = (self.aciertos / self.clics) * 100
            self.tasa_error = (self.errores / self.clics) * 100
        super().save(*args, **kwargs)
    
    @property
    def tiempo_respuesta_segundos(self):
        """Convierte el tiempo de respuesta a segundos"""
        return self.tiempo_respuesta_ms / 1000

class SesionJuego(models.Model):
    """
    Modelo para manejar sesiones únicas de juego por evaluación
    Cada vez que un niño juega un juego, se crea una nueva sesión con URL única
    """
    
    evaluacion = models.ForeignKey(
        Evaluacion,
        on_delete=models.CASCADE,
        related_name='sesiones_juego',
        verbose_name="Evaluación"
    )
    juego = models.ForeignKey(
        Juego,
        on_delete=models.CASCADE,
        related_name='sesiones',
        verbose_name="Juego"
    )
    
    url_sesion = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="URL de Sesión",
        help_text="URL única para esta sesión de juego"
    )
    nivel_seleccionado = models.PositiveIntegerField(
        default=1,
        verbose_name="Nivel Seleccionado",
        help_text="Nivel de dificultad seleccionado para esta sesión"
    )
    fecha_inicio = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Inicio")
    fecha_fin = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Fin")
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='en_proceso',
        verbose_name="Estado de la Sesión"
    )
    
    # Configuración de sesión (datos mínimos necesarios)
    puntaje_total = models.PositiveIntegerField(
        default=0,
        verbose_name="Puntaje Total",
        help_text="Puntaje total obtenido en esta sesión"
    )
    preguntas_respondidas = models.PositiveIntegerField(
        default=0,
        verbose_name="Preguntas Respondidas"
    )
    tiempo_total_segundos = models.PositiveIntegerField(
        default=0,
        verbose_name="Tiempo Total (segundos)"
    )
        # === NUEVOS CAMPOS PARA EL MODELO IA (métricas agregadas del minijuego) ===
    clicks_total = models.PositiveIntegerField(
        default=0,
        verbose_name="Clicks Totales",
        help_text="Total de clics realizados en todo el minijuego"
    )

    hits_total = models.PositiveIntegerField(
        default=0,
        verbose_name="Hits Totales",
        help_text="Total de aciertos en todo el minijuego"
    )

    misses_total = models.PositiveIntegerField(
        default=0,
        verbose_name="Misses Totales",
        help_text="Total de fallos en todo el minijuego"
    )

    score_total = models.IntegerField(
        default=0,
        verbose_name="Score Total",
        help_text="Puntuación total obtenida en el minijuego"
    )

    accuracy_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)],
        verbose_name="Accuracy (%)",
        help_text="Porcentaje de precisión: (hits / clicks) * 100"
    )

    missrate_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)],
        verbose_name="Missrate (%)",
        help_text="Porcentaje de tasa de error: (misses / clicks) * 100"
    )
        # Número de ejercicio global (1-32) para mapeo al modelo
    ejercicio_numero = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Número de Ejercicio",
        help_text="Posición del minijuego en la secuencia (1-32) para el modelo IA"
    )

    class Meta:
        verbose_name = "Sesión de Juego"
        verbose_name_plural = "Sesiones de Juego"
        ordering = ['-fecha_inicio']
        unique_together = ['evaluacion', 'juego', 'url_sesion']
    
    def __str__(self):
        return f"Sesión {self.juego.nombre} - Eval {self.evaluacion.id} ({self.estado})"
    
    def save(self, *args, **kwargs):
        """Override save para generar URL única"""
        if not self.url_sesion:
            self.url_sesion = self.juego.generar_url_sesion(self.evaluacion.id)
        
        super().save(*args, **kwargs)
    
    @property
    def archivo_configuracion_juego(self):
        """Retorna el archivo JSON que debe cargar el frontend para este juego"""
        return self.juego.archivo_configuracion
    
    @property
    def url_configuracion_juego(self):
        """Retorna la URL del archivo JSON que debe cargar el frontend"""
        return self.juego.url_archivo_configuracion
    
    def finalizar_sesion(self, puntaje_final, preguntas_contestadas, tiempo_total, 
                        clicks=0, hits=0, misses=0):
        """
        Finaliza la sesión con los resultados obtenidos
        Ahora incluye métricas agregadas para el modelo IA
        """        
        self.estado = 'completada'
        self.fecha_fin = timezone.now()
        self.puntaje_total = puntaje_final
        self.preguntas_respondidas = preguntas_contestadas
        self.tiempo_total_segundos = tiempo_total
        
        # === NUEVAS MÉTRICAS PARA EL MODELO IA ===
        self.clicks_total = clicks
        self.hits_total = hits
        self.misses_total = misses
        self.score_total = puntaje_final  # Usar el mismo que puntaje_total
        
        # Calcular accuracy y missrate
        if clicks > 0:
            self.accuracy_percent = (hits / clicks) * 100
            self.missrate_percent = (misses / clicks) * 100
        else:
            self.accuracy_percent = 0.00
            self.missrate_percent = 0.00
        
        self.save(update_fields=[
            'estado', 'fecha_fin', 'puntaje_total', 
            'preguntas_respondidas', 'tiempo_total_segundos',
            'clicks_total', 'hits_total', 'misses_total', 
            'score_total', 'accuracy_percent', 'missrate_percent'
        ])

    def calcular_metricas_desde_pruebas(self):
        """
        Calcula y actualiza las métricas agregadas desde todas las PruebaCognitivas
        asociadas a esta sesión
        """

        # Obtener todas las pruebas cognitivas de esta sesión
        pruebas = PruebaCognitiva.objects.filter(
            evaluacion=self.evaluacion,
            juego=self.juego
        )
        
        # Sumar métricas
        agregados = pruebas.aggregate(
            total_clics=Sum('clics'),
            total_aciertos=Sum('aciertos'),
            total_errores=Sum('errores'),
            total_puntaje=Sum('puntaje')
        )
        
        self.clicks_total = agregados['total_clics'] or 0
        self.hits_total = agregados['total_aciertos'] or 0
        self.misses_total = agregados['total_errores'] or 0
        self.score_total = agregados['total_puntaje'] or 0
        
        # Calcular porcentajes
        if self.clicks_total > 0:
            self.accuracy_percent = (self.hits_total / self.clicks_total) * 100
            self.missrate_percent = (self.misses_total / self.clicks_total) * 100
        else:
            self.accuracy_percent = 0.00
            self.missrate_percent = 0.00
        
        self.save(update_fields=[
            'clicks_total', 'hits_total', 'misses_total', 
            'score_total', 'accuracy_percent', 'missrate_percent'
        ])
        
        return {
            'clicks': self.clicks_total,
            'hits': self.hits_total,
            'misses': self.misses_total,
            'score': self.score_total,
            'accuracy': float(self.accuracy_percent),
            'missrate': float(self.missrate_percent)
        }
    @property
    def duracion_sesion(self):
        """Calcula la duración de la sesión en minutos"""
        if self.fecha_fin and self.fecha_inicio:
            delta = self.fecha_fin - self.fecha_inicio
            return delta.total_seconds() / 60
        return None
    
    @classmethod
    def crear_nueva_sesion(cls, evaluacion, juego, nivel=1):
        """
        Crea una nueva sesión de juego para una evaluación específica
        Retorna la sesión creada con URL única
        """
        sesion = cls.objects.create(
            evaluacion=evaluacion,
            juego=juego,
            nivel_seleccionado=nivel
        )
        return sesion
