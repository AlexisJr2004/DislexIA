from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

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
    
    def actualizar_estadisticas(self):
        """Actualiza las estadísticas del juego basándose en las pruebas realizadas"""
        # Contar pruebas de este juego específico
        pruebas = self.pruebas_realizadas.all()
        self.total_jugadas = pruebas.count()
        
        # Contar evaluaciones completadas que incluyan este juego
        evaluaciones_completadas = pruebas.filter(
            evaluacion__estado='completada'
        ).values('evaluacion').distinct().count()
        
        self.total_completados = evaluaciones_completadas
        self.save(update_fields=['total_jugadas', 'total_completados'])

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
        unique_together = ['evaluacion', 'numero_prueba']
        
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
