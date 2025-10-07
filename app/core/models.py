from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Nino(models.Model):
    """Modelo para almacenar información de los niños evaluados"""
    
    GENERO_CHOICES = [
        ('Masculino', 'Masculino'),
        ('Femenino', 'Femenino'),
        ('Otro', 'Otro'),
    ]
    
    nombres = models.CharField(max_length=100, verbose_name="Nombres")
    apellidos = models.CharField(max_length=100, verbose_name="Apellidos")
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento")
    edad = models.PositiveIntegerField(
        validators=[MinValueValidator(6), MaxValueValidator(12)],
        verbose_name="Edad"
    )
    genero = models.CharField(
        max_length=20, 
        choices=GENERO_CHOICES,
        verbose_name="Género"
    )
    idioma_nativo = models.CharField(max_length=50, verbose_name="Idioma Nativo")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    
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
    
    ROL_CHOICES = [
        ('administrador', 'Administrador'),
        ('profesional', 'Profesional'),
        ('docente', 'Docente'),
    ]
    
    nombres = models.CharField(max_length=100, verbose_name="Nombres")
    apellidos = models.CharField(max_length=100, verbose_name="Apellidos")
    especialidad = models.CharField(max_length=100, verbose_name="Especialidad")
    numero_licencia = models.CharField(max_length=100, unique=True, verbose_name="Número de Licencia")
    email = models.EmailField(unique=True, verbose_name="Email")
    password_hash = models.CharField(max_length=255, verbose_name="Hash de Contraseña")
    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        default='profesional',
        verbose_name="Rol"
    )
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")
    ultimo_acceso = models.DateTimeField(null=True, blank=True, verbose_name="Último Acceso")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    
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
    
    CLASIFICACION_RIESGO_CHOICES = [
        ('Bajo', 'Bajo'),
        ('Medio', 'Medio'),
        ('Alto', 'Alto'),
    ]
    
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
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)],
        verbose_name="Índice de Riesgo"
    )
    clasificacion_riesgo = models.CharField(
        max_length=20,
        choices=CLASIFICACION_RIESGO_CHOICES,
        verbose_name="Clasificación de Riesgo"
    )
    confianza_prediccion = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
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
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)],
        verbose_name="Índice Ajustado"
    )
    diagnostico_final = models.TextField(verbose_name="Diagnóstico Final")
    notas_clinicas = models.TextField(blank=True, verbose_name="Notas Clínicas")
    plan_tratamiento = models.TextField(blank=True, verbose_name="Plan de Tratamiento")
    requiere_seguimiento = models.BooleanField(default=False, verbose_name="Requiere Seguimiento")
    fecha_validacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Validación")
    
    class Meta:
        verbose_name = "Validación Profesional"
        verbose_name_plural = "Validaciones Profesionales"
        ordering = ['-fecha_validacion']
        
    def __str__(self):
        return f"Validación - {self.evaluacion} por {self.profesional}"
