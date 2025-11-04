from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.db.models import Count
from django.conf import settings
from django.utils import timezone
import json

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
    profesional = models.ForeignKey(
        'Profesional',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ninos',
        verbose_name='Profesional'
    )
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

    def cantidad_juegos(self):
        """Retorna la cantidad de juegos asociados a este niño"""
        return self.juego_set.count()

# Modelo de usuario personalizado usando AbstractUser de Django
class Profesional(AbstractUser):
    """Modelo para profesionales que validan las evaluaciones"""
    
    # Campos adicionales (username, email, password, first_name, last_name ya vienen de AbstractUser)
    nombres = models.CharField(max_length=100, verbose_name="Nombres", blank=True)
    apellidos = models.CharField(max_length=100, verbose_name="Apellidos", blank=True)
    imagen = models.ImageField(
        upload_to='profesionales/',
        verbose_name="Imagen",
        help_text="Imagen del profesional (opcional)",
        null=True,
        blank=True
    )
    especialidad = models.CharField(max_length=100, verbose_name="Especialidad", blank=True)
    numero_licencia = models.CharField(max_length=100, unique=True, verbose_name="Número de Licencia", null=True, blank=True)
    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        default=DEFAULTS['profesional_rol'],
        verbose_name="Rol"
    )
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")
    ultimo_acceso = models.DateTimeField(null=True, blank=True, verbose_name="Último Acceso")
    # El campo 'activo' ya viene como 'is_active' en AbstractUser
    
    # Usar email como campo de autenticación
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        verbose_name = "Profesional"
        verbose_name_plural = "Profesionales"
        ordering = ['-fecha_registro']
        
    def __str__(self):
        if self.nombres and self.apellidos:
            return f"{self.nombres} {self.apellidos}"
        return self.username
    
    @property
    def nombre_completo(self):
        if self.nombres and self.apellidos:
            return f"{self.nombres} {self.apellidos}"
        elif self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

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

    ReporteIA = models.OneToOneField(
        ReporteIA,
        default=1,
        on_delete=models.CASCADE,
        related_name='validacion_profesional',
        verbose_name="Reporte IA"
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

class Cita(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='citas')
    nombre_paciente = models.CharField(max_length=200, verbose_name="Nombre del Paciente")
    email_padres = models.EmailField(max_length=254, null=True, blank=True, verbose_name="Email de los Padres")
    foto_paciente = models.ImageField(upload_to='pacientes/', null=True, blank=True, verbose_name="Foto del Paciente")
    fecha = models.DateField(verbose_name="Fecha de la Cita")
    hora = models.TimeField(verbose_name="Hora de la Cita")
    notas = models.TextField(blank=True, null=True, verbose_name="Notas adicionales")
    completada = models.BooleanField(default=False, verbose_name="Completada")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cita"
        verbose_name_plural = "Citas"
        ordering = ['fecha', 'hora']

    def __str__(self):
        return f"{self.nombre_paciente} - {self.fecha} {self.hora}"


# ============================================
# MODELOS PARA CUMPLIMIENTO GDPR
# ============================================

class ConsentimientoGDPR(models.Model):
    """
    Modelo para registrar el consentimiento explícito del usuario
    Cumplimiento: Artículos 6, 7 y 13 GDPR
    """
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='consentimientos_gdpr',
        verbose_name="Usuario"
    )
    
    # Fecha y hora del consentimiento
    fecha_consentimiento = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Consentimiento")
    
    # Consentimientos específicos
    acepta_terminos = models.BooleanField(
        default=False,
        verbose_name="Acepta Términos y Condiciones",
        help_text="El usuario acepta los términos y condiciones del servicio"
    )
    acepta_privacidad = models.BooleanField(
        default=False,
        verbose_name="Acepta Política de Privacidad",
        help_text="El usuario acepta la política de privacidad"
    )
    acepta_tratamiento_datos = models.BooleanField(
        default=False,
        verbose_name="Acepta Tratamiento de Datos",
        help_text="El usuario consiente el tratamiento de sus datos personales"
    )
    acepta_cookies = models.BooleanField(
        default=False,
        verbose_name="Acepta Uso de Cookies",
        help_text="El usuario acepta el uso de cookies"
    )
    acepta_comunicaciones = models.BooleanField(
        default=False,
        verbose_name="Acepta Comunicaciones",
        help_text="El usuario acepta recibir comunicaciones (opcional)"
    )
    
    # Información de contexto (prueba de consentimiento)
    ip_address = models.GenericIPAddressField(verbose_name="Dirección IP")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    version_terminos = models.CharField(
        max_length=20,
        default="1.0",
        verbose_name="Versión de Términos",
        help_text="Versión de términos y condiciones aceptados"
    )
    version_privacidad = models.CharField(
        max_length=20,
        default="1.0",
        verbose_name="Versión de Privacidad",
        help_text="Versión de política de privacidad aceptada"
    )
    
    # Control de revocación
    consentimiento_activo = models.BooleanField(
        default=True,
        verbose_name="Consentimiento Activo",
        help_text="Indica si el consentimiento sigue siendo válido"
    )
    fecha_revocacion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Revocación",
        help_text="Fecha en que el usuario revocó su consentimiento"
    )
    
    class Meta:
        verbose_name = "Consentimiento GDPR"
        verbose_name_plural = "Consentimientos GDPR"
        ordering = ['-fecha_consentimiento']
        
    def __str__(self):
        return f"Consentimiento {self.usuario.username} - {self.fecha_consentimiento.strftime('%d/%m/%Y')}"
    
    def revocar_consentimiento(self):
        """Revoca el consentimiento del usuario"""
        self.consentimiento_activo = False
        self.fecha_revocacion = timezone.now()
        self.save()
    
    def es_valido(self):
        """Verifica si el consentimiento es válido"""
        return (
            self.consentimiento_activo and
            self.acepta_terminos and
            self.acepta_privacidad and
            self.acepta_tratamiento_datos
        )


class ConsentimientoTutor(models.Model):
    """
    Modelo para consentimiento de tutores legales para datos de menores
    Cumplimiento: Artículo 8 GDPR (Condiciones aplicables al consentimiento del niño)
    """
    RELACION_CHOICES = [
        ('padre', 'Padre'),
        ('madre', 'Madre'),
        ('tutor_legal', 'Tutor Legal'),
        ('representante', 'Representante Legal'),
    ]
    
    # Relación con el niño
    nino = models.OneToOneField(
        Nino,
        on_delete=models.CASCADE,
        related_name='consentimiento_tutor',
        verbose_name="Niño"
    )
    
    # Datos del tutor
    nombre_completo_tutor = models.CharField(max_length=200, verbose_name="Nombre Completo del Tutor")
    relacion = models.CharField(
        max_length=20,
        choices=RELACION_CHOICES,
        verbose_name="Relación con el Niño"
    )
    documento_identidad = models.CharField(
        max_length=50,
        verbose_name="Documento de Identidad",
        help_text="Cédula, pasaporte u otro documento oficial"
    )
    email = models.EmailField(verbose_name="Email del Tutor")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono de Contacto")
    
    # Consentimientos específicos
    acepta_evaluacion = models.BooleanField(
        default=False,
        verbose_name="Autoriza Evaluación Cognitiva",
        help_text="El tutor autoriza la evaluación cognitiva del menor"
    )
    acepta_almacenamiento_datos = models.BooleanField(
        default=False,
        verbose_name="Autoriza Almacenamiento de Datos",
        help_text="El tutor autoriza el almacenamiento de datos del menor"
    )
    acepta_uso_imagen = models.BooleanField(
        default=False,
        verbose_name="Autoriza Uso de Imagen",
        help_text="El tutor autoriza el uso de la imagen del menor en la plataforma"
    )
    acepta_compartir_profesionales = models.BooleanField(
        default=False,
        verbose_name="Autoriza Compartir con Profesionales",
        help_text="El tutor autoriza compartir información con profesionales asignados"
    )
    
    # Información de contexto
    fecha_consentimiento = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Consentimiento")
    ip_address = models.GenericIPAddressField(verbose_name="Dirección IP")
    firma_digital = models.TextField(
        blank=True,
        verbose_name="Firma Digital",
        help_text="Hash o representación de firma digital del tutor"
    )
    
    # Control de validez
    consentimiento_activo = models.BooleanField(default=True, verbose_name="Consentimiento Activo")
    fecha_expiracion = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de Expiración",
        help_text="Fecha hasta la cual el consentimiento es válido (opcional)"
    )
    fecha_renovacion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Renovación",
        help_text="Última fecha en que se renovó el consentimiento"
    )
    
    # Notas adicionales
    notas = models.TextField(
        blank=True,
        verbose_name="Notas Adicionales",
        help_text="Cualquier observación o nota relevante"
    )
    
    class Meta:
        verbose_name = "Consentimiento de Tutor"
        verbose_name_plural = "Consentimientos de Tutores"
        ordering = ['-fecha_consentimiento']
        
    def __str__(self):
        return f"Consentimiento {self.nombre_completo_tutor} - {self.nino.nombre_completo}"
    
    def es_valido(self):
        """Verifica si el consentimiento del tutor es válido"""
        if not self.consentimiento_activo:
            return False
        
        # Verificar si ha expirado
        if self.fecha_expiracion and timezone.now().date() > self.fecha_expiracion:
            return False
        
        # Verificar consentimientos mínimos
        return (
            self.acepta_evaluacion and
            self.acepta_almacenamiento_datos
        )
    
    def revocar_consentimiento(self):
        """Revoca el consentimiento del tutor"""
        self.consentimiento_activo = False
        self.save()


class AuditoriaAcceso(models.Model):
    """
    Modelo para registrar accesos y operaciones sobre datos personales
    Cumplimiento: Artículo 30 GDPR (Registro de actividades de tratamiento)
    """
    ACCION_CHOICES = [
        ('READ', 'Lectura'),
        ('CREATE', 'Creación'),
        ('UPDATE', 'Actualización'),
        ('DELETE', 'Eliminación'),
        ('EXPORT', 'Exportación'),
        ('LOGIN', 'Inicio de Sesión'),
        ('LOGOUT', 'Cierre de Sesión'),
        ('LOGIN_FAILED', 'Intento de Login Fallido'),
        ('PASSWORD_CHANGE', 'Cambio de Contraseña'),
        ('PASSWORD_RESET', 'Restablecimiento de Contraseña'),
        ('CONSENT_GIVEN', 'Consentimiento Otorgado'),
        ('CONSENT_REVOKED', 'Consentimiento Revocado'),
        ('DATA_ANONYMIZED', 'Datos Anonimizados'),
    ]
    
    # Usuario que realiza la acción
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='auditorias',
        verbose_name="Usuario"
    )
    
    # Información de la acción
    accion = models.CharField(
        max_length=20,
        choices=ACCION_CHOICES,
        verbose_name="Acción Realizada"
    )
    tabla_afectada = models.CharField(
        max_length=100,
        verbose_name="Tabla/Modelo Afectado",
        help_text="Nombre del modelo Django afectado"
    )
    registro_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="ID del Registro",
        help_text="ID del registro afectado"
    )
    
    # Contexto de la acción
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")
    ip_address = models.GenericIPAddressField(verbose_name="Dirección IP")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    
    # Detalles adicionales
    detalles = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Detalles de la Operación",
        help_text="Información adicional sobre la operación en formato JSON"
    )
    
    # Resultado de la operación
    exitoso = models.BooleanField(default=True, verbose_name="Operación Exitosa")
    mensaje_error = models.TextField(
        blank=True,
        verbose_name="Mensaje de Error",
        help_text="Mensaje de error si la operación falló"
    )
    
    class Meta:
        verbose_name = "Auditoría de Acceso"
        verbose_name_plural = "Auditorías de Acceso"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['usuario', 'timestamp']),
            models.Index(fields=['accion', 'timestamp']),
            models.Index(fields=['tabla_afectada', 'registro_id']),
        ]
        
    def __str__(self):
        usuario_str = self.usuario.username if self.usuario else "Sistema"
        return f"{usuario_str} - {self.get_accion_display()} - {self.timestamp.strftime('%d/%m/%Y %H:%M')}"
    
    @classmethod
    def registrar(cls, usuario, accion, tabla_afectada, registro_id=None, ip_address=None, 
                  detalles=None, exitoso=True, mensaje_error='', user_agent=''):
        """
        Método de clase para registrar fácilmente una auditoría
        
        Uso:
        AuditoriaAcceso.registrar(
            usuario=request.user,
            accion='READ',
            tabla_afectada='Nino',
            registro_id=nino.id,
            ip_address=request.META.get('REMOTE_ADDR'),
            detalles={'campo_accedido': 'nombre_completo'}
        )
        """
        return cls.objects.create(
            usuario=usuario,
            accion=accion,
            tabla_afectada=tabla_afectada,
            registro_id=registro_id,
            ip_address=ip_address or '0.0.0.0',
            detalles=detalles,
            exitoso=exitoso,
            mensaje_error=mensaje_error,
            user_agent=user_agent
        )


class PoliticaRetencionDatos(models.Model):
    """
    Modelo para definir políticas de retención de datos
    Cumplimiento: Artículo 5(1)(e) GDPR (Limitación del plazo de conservación)
    """
    TIPO_DATO_CHOICES = [
        ('evaluacion', 'Evaluaciones'),
        ('reporte_ia', 'Reportes IA'),
        ('sesion_juego', 'Sesiones de Juego'),
        ('cita', 'Citas'),
        ('auditoria', 'Auditorías'),
        ('usuario_inactivo', 'Usuarios Inactivos'),
    ]
    
    tipo_dato = models.CharField(
        max_length=50,
        choices=TIPO_DATO_CHOICES,
        unique=True,
        verbose_name="Tipo de Dato"
    )
    dias_retencion = models.PositiveIntegerField(
        verbose_name="Días de Retención",
        help_text="Número de días que se conservan los datos antes de ser eliminados/anonimizados"
    )
    accion_al_vencer = models.CharField(
        max_length=20,
        choices=[('eliminar', 'Eliminar'), ('anonimizar', 'Anonimizar')],
        default='anonimizar',
        verbose_name="Acción al Vencer"
    )
    activa = models.BooleanField(default=True, verbose_name="Política Activa")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    
    class Meta:
        verbose_name = "Política de Retención de Datos"
        verbose_name_plural = "Políticas de Retención de Datos"
        
    def __str__(self):
        return f"{self.get_tipo_dato_display()} - {self.dias_retencion} días - {self.get_accion_al_vencer_display()}"


class LoginAttempt(models.Model):
    """
    Modelo para rastrear intentos de login fallidos
    Implementa bloqueo de cuenta después de 5 intentos fallidos
    """
    username = models.CharField(
        max_length=150,
        verbose_name="Nombre de Usuario",
        db_index=True
    )
    ip_address = models.GenericIPAddressField(
        verbose_name="Dirección IP"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha y Hora",
        db_index=True
    )
    exitoso = models.BooleanField(
        default=False,
        verbose_name="Intento Exitoso"
    )
    user_agent = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="User Agent"
    )
    
    class Meta:
        verbose_name = "Intento de Login"
        verbose_name_plural = "Intentos de Login"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['username', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]
    
    def __str__(self):
        estado = "Exitoso" if self.exitoso else "Fallido"
        return f"{self.username} - {estado} - {self.timestamp.strftime('%d/%m/%Y %H:%M:%S')}"
    
    @classmethod
    def obtener_intentos_recientes(cls, username, minutos=30):
        """
        Obtiene el número de intentos fallidos en los últimos X minutos
        """
        desde = timezone.now() - timezone.timedelta(minutes=minutos)
        return cls.objects.filter(
            username=username,
            exitoso=False,
            timestamp__gte=desde
        ).count()
    
    @classmethod
    def esta_bloqueado(cls, username, max_intentos=5, minutos=30):
        """
        Verifica si una cuenta está bloqueada por múltiples intentos fallidos
        """
        intentos = cls.obtener_intentos_recientes(username, minutos)
        return intentos >= max_intentos
    
    @classmethod
    def obtener_tiempo_restante_bloqueo(cls, username, minutos=30):
        """
        Obtiene el tiempo restante de bloqueo en minutos
        """
        desde = timezone.now() - timezone.timedelta(minutes=minutos)
        primer_intento_fallido = cls.objects.filter(
            username=username,
            exitoso=False,
            timestamp__gte=desde
        ).order_by('timestamp').first()
        
        if primer_intento_fallido:
            tiempo_transcurrido = timezone.now() - primer_intento_fallido.timestamp
            tiempo_restante = timezone.timedelta(minutes=minutos) - tiempo_transcurrido
            return max(0, int(tiempo_restante.total_seconds() / 60))
        return 0
    
    @classmethod
    def limpiar_intentos_antiguos(cls, username):
        """
        Limpia intentos fallidos antiguos (más de 30 minutos)
        """
        desde = timezone.now() - timezone.timedelta(minutes=30)
        cls.objects.filter(
            username=username,
            timestamp__lt=desde
        ).delete()
