from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Evaluacion(models.Model):
    """Modelo para evaluaciones cognitivas realizadas a los niños"""
    
    ESTADO_CHOICES = [
        ('en_proceso', 'En Proceso'),
        ('completada', 'Completada'),
        ('interrumpida', 'Interrumpida'),
    ]
    
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
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)],
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
    
    TIPOS_PRUEBA_CHOICES = [
        ('buscar_palabras', 'Buscar Palabras'),
        ('ordenar_palabras', 'Ordenar Palabras'),
        ('quiz_interactivo', 'Quiz Interactivo'),
        ('memoria_visual', 'Memoria Visual'),
        ('reconocimiento_patron', 'Reconocimiento de Patrón'),
    ]
    
    evaluacion = models.ForeignKey(
        Evaluacion,
        on_delete=models.CASCADE,
        related_name='pruebas_cognitivas',
        verbose_name="Evaluación"
    )
    
    numero_prueba = models.PositiveIntegerField(verbose_name="Número de Prueba")
    tipo_prueba = models.CharField(
        max_length=50,
        choices=TIPOS_PRUEBA_CHOICES,
        verbose_name="Tipo de Prueba"
    )
    clics = models.PositiveIntegerField(default=0, verbose_name="Clics")
    aciertos = models.PositiveIntegerField(default=0, verbose_name="Aciertos")
    errores = models.PositiveIntegerField(default=0, verbose_name="Errores")
    puntaje = models.IntegerField(default=0, verbose_name="Puntaje")
    precision = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)],
        verbose_name="Precisión (%)"
    )
    tasa_error = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)],
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
        return f"Prueba {self.numero_prueba} - {self.get_tipo_prueba_display()} (Eval: {self.evaluacion.id})"
    
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
