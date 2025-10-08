from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Importar constantes
from .constants import (
    GENERO_CHOICES,
    ROL_CHOICES,
    CLASIFICACION_RIESGO_CHOICES,
    EDAD_MIN,
    EDAD_MAX,
    INDICE_RIESGO_MIN,
    INDICE_RIESGO_MAX,
    CONFIANZA_MIN,
    CONFIANZA_MAX,
    DEFAULTS
)

class Nino(models.Model):
    """Modelo para almacenar información de los niños evaluados"""
    
    nombres = models.CharField(max_length=100, verbose_name="Nombres")
    apellidos = models.CharField(max_length=100, verbose_name="Apellidos")
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento")
    edad = models.PositiveIntegerField(
        validators=[MinValueValidator(EDAD_MIN), MaxValueValidator(EDAD_MAX)],
        verbose_name="Edad"
    )
    imagen = models.ImageField(
        upload_to='ninos/', 
        verbose_name="Imagen",
        help_text="Imagen del niño (opcional)",
        # default='ninos/default_child_image.png',
        null=True,
        blank=True
        )
    genero = models.CharField(
        max_length=20, 
        choices=GENERO_CHOICES,
        verbose_name="Género"
    )
    idioma_nativo = models.CharField(max_length=50, verbose_name="Idioma Nativo")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")
    activo = models.BooleanField(default=DEFAULTS['nino_activo'], verbose_name="Activo")
    
    class Meta:
        verbose_name = "Niño"
        verbose_name_plural = "Niños"
        ordering = ['-fecha_registro']
        
    def __str__(self):
        return f"{self.nombres} {self.apellidos}"
    
    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

# Se puede usar AbstractUser para facilitar el registro y autenticación
class Profesional(models.Model):
    """Modelo para profesionales que validan las evaluaciones"""
    
    nombres = models.CharField(max_length=100, verbose_name="Nombres")
    apellidos = models.CharField(max_length=100, verbose_name="Apellidos")
    imagen = models.ImageField(
        upload_to='profesionales/',
        verbose_name="Imagen",
        help_text="Imagen del profesional (opcional)",
        null=True,
        blank=True
    )
    especialidad = models.CharField(max_length=100, verbose_name="Especialidad")
    numero_licencia = models.CharField(max_length=100, unique=True, verbose_name="Número de Licencia")
    email = models.EmailField(unique=True, verbose_name="Email")
    password_hash = models.CharField(max_length=255, verbose_name="Hash de Contraseña")
    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        default=DEFAULTS['profesional_rol'],
        verbose_name="Rol"
    )
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")
    ultimo_acceso = models.DateTimeField(null=True, blank=True, verbose_name="Último Acceso")
    activo = models.BooleanField(default=DEFAULTS['profesional_activo'], verbose_name="Activo")
    
    class Meta:
        verbose_name = "Profesional"
        verbose_name_plural = "Profesionales"
        ordering = ['-fecha_registro']
        
    def __str__(self):
        return f"{self.nombres} {self.apellidos} - {self.especialidad}"
    
    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

class ReporteIA(models.Model):
    """Modelo para almacenar reportes generados por IA"""
    
    # Relación con evaluación (se importará desde games)
    evaluacion = models.OneToOneField(
        'games.Evaluacion',
        on_delete=models.CASCADE,
        related_name='reporte_ia',
        verbose_name="Evaluación"
    )
    
    indice_riesgo = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(INDICE_RIESGO_MIN), MaxValueValidator(INDICE_RIESGO_MAX)],
        verbose_name="Índice de Riesgo"
    )
    clasificacion_riesgo = models.CharField(
        max_length=20,
        choices=CLASIFICACION_RIESGO_CHOICES,
        verbose_name="Clasificación de Riesgo"
    )
    confianza_prediccion = models.PositiveIntegerField(
        validators=[MinValueValidator(CONFIANZA_MIN), MaxValueValidator(CONFIANZA_MAX)],
        verbose_name="Confianza de Predicción (%)"
    )
    caracteristicas_json = models.JSONField(
        verbose_name="Características (JSON)",
        help_text="Datos estructurados de las características analizadas"
    )
    recomendaciones = models.TextField(verbose_name="Recomendaciones")
    metricas_relevantes = models.JSONField(
        verbose_name="Métricas Relevantes",
        help_text="Métricas clave del análisis"
    )
    fecha_generacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Generación")
    
    class Meta:
        verbose_name = "Reporte IA"
        verbose_name_plural = "Reportes IA"
        ordering = ['-fecha_generacion']
        
    def __str__(self):
        return f"Reporte IA - {self.evaluacion} ({self.clasificacion_riesgo})"

class ValidacionProfesional(models.Model):
    """Modelo para validaciones realizadas por profesionales"""
    
    profesional = models.ForeignKey(
        Profesional,
        on_delete=models.CASCADE,
        related_name='validaciones',
        verbose_name="Profesional"
    )
    evaluacion = models.OneToOneField(
        'games.Evaluacion',
        on_delete=models.CASCADE,
        related_name='validacion_profesional',
        verbose_name="Evaluación"
    )
    
    riesgo_confirmado = models.BooleanField(verbose_name="Riesgo Confirmado")
    indice_ajustado = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(INDICE_RIESGO_MIN), MaxValueValidator(INDICE_RIESGO_MAX)],
        verbose_name="Índice Ajustado"
    )
    diagnostico_final = models.TextField(verbose_name="Diagnóstico Final")
    notas_clinicas = models.TextField(blank=True, verbose_name="Notas Clínicas")
    plan_tratamiento = models.TextField(blank=True, verbose_name="Plan de Tratamiento")
    requiere_seguimiento = models.BooleanField(default=DEFAULTS['requiere_seguimiento'], verbose_name="Requiere Seguimiento")
    fecha_validacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Validación")
    
    class Meta:
        verbose_name = "Validación Profesional"
        verbose_name_plural = "Validaciones Profesionales"
        ordering = ['-fecha_validacion']
        
    def __str__(self):
        return f"Validación - {self.evaluacion} por {self.profesional}"
