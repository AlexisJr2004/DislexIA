from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Nino, Profesional, ReporteIA, ValidacionProfesional, Cita,
    ConsentimientoGDPR, ConsentimientoTutor, AuditoriaAcceso, PoliticaRetencionDatos, LoginAttempt
)


@admin.register(Nino)
class NinoAdmin(admin.ModelAdmin):
    """Administrador para el modelo Niño - completamente editable"""
    
    list_display = [
        'nombre_completo_display',
        'edad',
        'genero',
        'idioma_nativo',
        'profesional_display',
        'fecha_nacimiento',
        'total_evaluaciones',
        'ultima_evaluacion',
        'activo',
        'fecha_registro'
    ]
    list_filter = [
        'genero',
        'edad',
        'idioma_nativo',
        'profesional',
        'activo',
        'fecha_registro'
    ]
    search_fields = ['nombres', 'apellidos', 'idioma_nativo', 'profesional__nombres', 'profesional__apellidos']
    ordering = ['-fecha_registro', 'apellidos', 'nombres']
    list_per_page = 25
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombres', 'apellidos', 'fecha_nacimiento', 'edad', 'imagen')
        }),
        ('Características', {
            'fields': ('genero', 'idioma_nativo')
        }),
        ('Profesional Asignado', {
            'fields': ('profesional',)
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Fechas del Sistema', {
            'fields': ('fecha_registro',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['fecha_registro']
    
    def nombre_completo_display(self, obj):
        """Muestra el nombre completo con formato"""
        return format_html(
            '<strong>{}</strong>',
            obj.nombre_completo
        )
    nombre_completo_display.short_description = 'Nombre Completo'
    
    def profesional_display(self, obj):
        """Muestra el profesional asignado con formato"""
        if obj.profesional:
            return format_html(
                '<span style="color: #007bff;">{}</span>',
                obj.profesional.nombre_completo
            )
        return format_html(
            '<span style="color: #dc3545;">Sin asignar</span>'
        )
    profesional_display.short_description = 'Profesional'
    
    def total_evaluaciones(self, obj):
        """Muestra el total de evaluaciones del niño"""
        count = obj.evaluaciones.count()
        if count > 0:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">{}</span>',
                count
            )
        return format_html(
            '<span style="color: #6c757d;">0</span>'
        )
    total_evaluaciones.short_description = 'Total Evaluaciones'
    
    def ultima_evaluacion(self, obj):
        """Muestra la fecha de la última evaluación"""
        ultima = obj.evaluaciones.first()  # Ya está ordenado por -fecha_hora_inicio
        if ultima:
            return format_html(
                '<span style="color: #007bff;">{}</span>',
                ultima.fecha_hora_inicio.strftime('%d/%m/%Y')
            )
        return format_html(
            '<span style="color: #6c757d;">Sin evaluaciones</span>'
        )
    ultima_evaluacion.short_description = 'Última Evaluación'
    
    def get_queryset(self, request):
        """Optimizar consultas con prefetch_related"""
        return super().get_queryset(request).select_related('profesional').prefetch_related('evaluaciones')


@admin.register(Profesional)
class ProfesionalAdmin(admin.ModelAdmin):
    """Administrador para el modelo Profesional"""
    
    list_display = [
        'nombre_completo_display',
        'username',
        'especialidad',
        'numero_licencia',
        'email',
        'rol',
        'total_ninos',
        'total_validaciones',
        'ultimo_acceso',
        'is_active'
    ]
    list_filter = [
        'rol',
        'especialidad',
        'is_active',
        'is_staff',
        'fecha_registro'
    ]
    search_fields = ['username', 'nombres', 'apellidos', 'especialidad', 'numero_licencia', 'email']
    ordering = ['-fecha_registro', 'apellidos', 'nombres']
    
    fieldsets = (
        ('Credenciales de Acceso', {
            'fields': ('username', 'password', 'email')
        }),
        ('Información Personal', {
            'fields': ('nombres', 'apellidos', 'first_name', 'last_name', 'imagen')
        }),
        ('Información Profesional', {
            'fields': ('especialidad', 'numero_licencia', 'rol')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Fechas Importantes', {
            'fields': ('fecha_registro', 'ultimo_acceso', 'last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['fecha_registro', 'last_login', 'date_joined']
    
    def nombre_completo_display(self, obj):
        """Muestra el nombre completo con formato"""
        return format_html(
            '<strong>{}</strong>',
            obj.nombre_completo
        )
    nombre_completo_display.short_description = 'Nombre Completo'
    
    def total_ninos(self, obj):
        """Muestra el total de niños asignados"""
        count = obj.ninos.count()
        if count > 0:
            return format_html(
                '<span style="color: #17a2b8; font-weight: bold;">{}</span>',
                count
            )
        return format_html(
            '<span style="color: #6c757d;">0</span>'
        )
    total_ninos.short_description = 'Niños Asignados'
    
    def total_validaciones(self, obj):
        """Muestra el total de validaciones realizadas"""
        count = obj.validaciones.count()
        return format_html(
            '<span style="color: #28a745; font-weight: bold;">{}</span>',
            count
        )
    total_validaciones.short_description = 'Validaciones'
    
    def get_queryset(self, request):
        """Optimizar consultas con prefetch_related"""
        return super().get_queryset(request).prefetch_related('ninos', 'validaciones')


@admin.register(ReporteIA)
class ReporteIAAdmin(admin.ModelAdmin):
    """Administrador para el modelo ReporteIA - solo lectura"""
    
    list_display = [
        'id',
        'evaluacion_display',
        'clasificacion_riesgo_display',
        'indice_riesgo',
        'confianza_prediccion',
        'fecha_generacion'
    ]
    list_filter = [
        'clasificacion_riesgo',
        'fecha_generacion'
    ]
    search_fields = [
        'evaluacion__nino__nombres',
        'evaluacion__nino__apellidos',
        'clasificacion_riesgo'
    ]
    ordering = ['-fecha_generacion']
    
    def evaluacion_display(self, obj):
        """Muestra información de la evaluación"""
        return format_html(
            '<strong>{}</strong><br><small>ID: {}</small>',
            obj.evaluacion.nino.nombre_completo,
            obj.evaluacion.id
        )
    evaluacion_display.short_description = 'Evaluación'
    
    def clasificacion_riesgo_display(self, obj):
        """Muestra la clasificación con colores"""
        color_map = {
            'bajo': '#28a745',
            'medio': '#ffc107',
            'alto': '#dc3545'
        }
        color = color_map.get(obj.clasificacion_riesgo, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_clasificacion_riesgo_display()
        )
    clasificacion_riesgo_display.short_description = 'Clasificación'
    
    # Solo lectura
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields]


@admin.register(ValidacionProfesional)
class ValidacionProfesionalAdmin(admin.ModelAdmin):
    """Administrador para el modelo ValidacionProfesional"""
    
    list_display = [
        'id',
        'profesional_display',
        'evaluacion_display',
        'riesgo_confirmado_display',
        'indice_ajustado',
        'requiere_seguimiento_display',
        'fecha_validacion'
    ]
    list_filter = [
        'riesgo_confirmado',
        'requiere_seguimiento',
        'fecha_validacion',
        'profesional'
    ]
    search_fields = [
        'evaluacion__nino__nombres',
        'evaluacion__nino__apellidos',
        'profesional__nombres',
        'profesional__apellidos'
    ]
    ordering = ['-fecha_validacion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('profesional', 'evaluacion')
        }),
        ('Diagnóstico', {
            'fields': ('riesgo_confirmado', 'indice_ajustado', 'diagnostico_final')
        }),
        ('Detalles Clínicos', {
            'fields': ('notas_clinicas', 'plan_tratamiento', 'requiere_seguimiento')
        }),
        ('Fecha', {
            'fields': ('fecha_validacion',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['fecha_validacion']
    
    def profesional_display(self, obj):
        """Muestra el profesional con formato"""
        return format_html(
            '<strong>{}</strong>',
            obj.profesional.nombre_completo
        )
    profesional_display.short_description = 'Profesional'
    
    def evaluacion_display(self, obj):
        """Muestra información de la evaluación"""
        return format_html(
            '<strong>{}</strong><br><small>ID: {}</small>',
            obj.evaluacion.nino.nombre_completo,
            obj.evaluacion.id
        )
    evaluacion_display.short_description = 'Evaluación'
    
    def riesgo_confirmado_display(self, obj):
        """Muestra el riesgo confirmado con colores"""
        if obj.riesgo_confirmado:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">✓ Confirmado</span>'
            )
        return format_html(
            '<span style="color: #28a745; font-weight: bold;">✗ No confirmado</span>'
        )
    riesgo_confirmado_display.short_description = 'Riesgo'
    
    def requiere_seguimiento_display(self, obj):
        """Muestra si requiere seguimiento con íconos"""
        if obj.requiere_seguimiento:
            return format_html(
                '<span style="color: #ffc107; font-weight: bold;">📋 Sí</span>'
            )
        return format_html(
            '<span style="color: #6c757d;">➖ No</span>'
        )
    requiere_seguimiento_display.short_description = 'Seguimiento'


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    """Administrador para el modelo Cita"""
    
    list_display = [
        'nombre_paciente',
        'usuario_display',
        'fecha',
        'hora',
        'completada_display',
        'created_at'
    ]
    list_filter = [
        'completada',
        'fecha',
        'created_at',
        'usuario'
    ]
    search_fields = [
        'nombre_paciente',
        'email_padres',
        'usuario__username',
        'usuario__nombres',
        'usuario__apellidos'
    ]
    ordering = ['-fecha', '-hora']
    
    fieldsets = (
        ('Información del Paciente', {
            'fields': ('nombre_paciente', 'email_padres', 'foto_paciente')
        }),
        ('Información de la Cita', {
            'fields': ('usuario', 'fecha', 'hora', 'notas')
        }),
        ('Estado', {
            'fields': ('completada',)
        }),
        ('Fechas del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def usuario_display(self, obj):
        """Muestra el usuario profesional"""
        return format_html(
            '<strong>{}</strong>',
            obj.usuario.nombre_completo
        )
    usuario_display.short_description = 'Profesional'
    
    def completada_display(self, obj):
        """Muestra el estado de la cita con colores"""
        if obj.completada:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">✓ Completada</span>'
            )
        return format_html(
            '<span style="color: #ffc107; font-weight: bold;">⏳ Pendiente</span>'
        )
    completada_display.short_description = 'Estado'


# ============================================
# ADMINISTRADORES PARA MODELOS GDPR
# ============================================

@admin.register(ConsentimientoGDPR)
class ConsentimientoGDPRAdmin(admin.ModelAdmin):
    """Administrador para Consentimientos GDPR"""
    
    list_display = [
        'usuario_display',
        'fecha_consentimiento',
        'acepta_terminos',
        'acepta_privacidad',
        'acepta_tratamiento_datos',
        'consentimiento_activo_display',
        'version_terminos',
        'ip_address',
    ]
    list_filter = [
        'consentimiento_activo',
        'acepta_terminos',
        'acepta_privacidad',
        'acepta_tratamiento_datos',
        'fecha_consentimiento',
    ]
    search_fields = ['usuario__username', 'usuario__email', 'ip_address']
    ordering = ['-fecha_consentimiento']
    readonly_fields = ['fecha_consentimiento', 'fecha_revocacion']
    
    fieldsets = (
        ('Usuario', {
            'fields': ('usuario', 'ip_address', 'user_agent')
        }),
        ('Consentimientos', {
            'fields': (
                'acepta_terminos',
                'acepta_privacidad',
                'acepta_tratamiento_datos',
                'acepta_cookies',
                'acepta_comunicaciones'
            )
        }),
        ('Versiones', {
            'fields': ('version_terminos', 'version_privacidad')
        }),
        ('Estado', {
            'fields': ('consentimiento_activo', 'fecha_consentimiento', 'fecha_revocacion')
        }),
    )
    
    def usuario_display(self, obj):
        return format_html('<strong>{}</strong>', obj.usuario.nombre_completo)
    usuario_display.short_description = 'Usuario'
    
    def consentimiento_activo_display(self, obj):
        if obj.consentimiento_activo:
            return format_html('<span style="color: #28a745; font-weight: bold;">✓ Activo</span>')
        return format_html('<span style="color: #dc3545; font-weight: bold;">✗ Revocado</span>')
    consentimiento_activo_display.short_description = 'Estado'


@admin.register(ConsentimientoTutor)
class ConsentimientoTutorAdmin(admin.ModelAdmin):
    """Administrador para Consentimientos de Tutores"""
    
    list_display = [
        'nino_display',
        'nombre_completo_tutor',
        'relacion',
        'email',
        'consentimiento_activo_display',
        'fecha_consentimiento',
    ]
    list_filter = [
        'consentimiento_activo',
        'relacion',
        'acepta_evaluacion',
        'acepta_almacenamiento_datos',
        'fecha_consentimiento',
    ]
    search_fields = [
        'nombre_completo_tutor',
        'email',
        'documento_identidad',
        'nino__nombres',
        'nino__apellidos'
    ]
    ordering = ['-fecha_consentimiento']
    
    fieldsets = (
        ('Niño', {
            'fields': ('nino',)
        }),
        ('Datos del Tutor', {
            'fields': (
                'nombre_completo_tutor',
                'relacion',
                'documento_identidad',
                'email',
                'telefono'
            )
        }),
        ('Consentimientos', {
            'fields': (
                'acepta_evaluacion',
                'acepta_almacenamiento_datos',
                'acepta_uso_imagen',
                'acepta_compartir_profesionales'
            )
        }),
        ('Información Adicional', {
            'fields': (
                'fecha_consentimiento',
                'ip_address',
                'firma_digital',
                'notas'
            )
        }),
        ('Validez', {
            'fields': (
                'consentimiento_activo',
                'fecha_expiracion',
                'fecha_renovacion'
            )
        }),
    )
    
    readonly_fields = ['fecha_consentimiento']
    
    def nino_display(self, obj):
        return format_html('<strong>{}</strong>', obj.nino.nombre_completo)
    nino_display.short_description = 'Niño'
    
    def consentimiento_activo_display(self, obj):
        if obj.es_valido():
            return format_html('<span style="color: #28a745; font-weight: bold;">✓ Válido</span>')
        return format_html('<span style="color: #dc3545; font-weight: bold;">✗ Inválido/Expirado</span>')
    consentimiento_activo_display.short_description = 'Estado'


@admin.register(AuditoriaAcceso)
class AuditoriaAccesoAdmin(admin.ModelAdmin):
    """Administrador para Auditorías de Acceso"""
    
    list_display = [
        'timestamp',
        'usuario_display',
        'accion_display',
        'tabla_afectada',
        'registro_id',
        'ip_address',
        'exitoso_display',
    ]
    list_filter = [
        'accion',
        'tabla_afectada',
        'exitoso',
        'timestamp',
    ]
    search_fields = [
        'usuario__username',
        'tabla_afectada',
        'ip_address',
        'registro_id'
    ]
    ordering = ['-timestamp']
    readonly_fields = [
        'timestamp',
        'usuario',
        'accion',
        'tabla_afectada',
        'registro_id',
        'ip_address',
        'user_agent',
        'detalles',
        'exitoso',
        'mensaje_error'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('timestamp', 'usuario', 'accion', 'exitoso')
        }),
        ('Datos Afectados', {
            'fields': ('tabla_afectada', 'registro_id')
        }),
        ('Contexto Técnico', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Detalles', {
            'fields': ('detalles', 'mensaje_error'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Solo administradores pueden eliminar auditorías
        return request.user.is_superuser
    
    def usuario_display(self, obj):
        if obj.usuario:
            return format_html('<strong>{}</strong>', obj.usuario.username)
        return format_html('<span style="color: #6c757d;">Sistema</span>')
    usuario_display.short_description = 'Usuario'
    
    def accion_display(self, obj):
        color_map = {
            'READ': '#17a2b8',
            'CREATE': '#28a745',
            'UPDATE': '#ffc107',
            'DELETE': '#dc3545',
            'EXPORT': '#6f42c1',
            'LOGIN': '#007bff',
            'LOGOUT': '#6c757d',
            'LOGIN_FAILED': '#dc3545',
        }
        color = color_map.get(obj.accion, '#000000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_accion_display()
        )
    accion_display.short_description = 'Acción'
    
    def exitoso_display(self, obj):
        if obj.exitoso:
            return format_html('<span style="color: #28a745;">✓</span>')
        return format_html('<span style="color: #dc3545;">✗</span>')
    exitoso_display.short_description = 'Éxito'


@admin.register(PoliticaRetencionDatos)
class PoliticaRetencionDatosAdmin(admin.ModelAdmin):
    """Administrador para Políticas de Retención de Datos"""
    
    list_display = [
        'tipo_dato_display',
        'dias_retencion',
        'accion_al_vencer_display',
        'activa_display',
        'fecha_actualizacion',
    ]
    list_filter = ['tipo_dato', 'accion_al_vencer', 'activa']
    ordering = ['tipo_dato']
    
    fieldsets = (
        ('Configuración', {
            'fields': ('tipo_dato', 'dias_retencion', 'accion_al_vencer', 'activa')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    def tipo_dato_display(self, obj):
        return format_html('<strong>{}</strong>', obj.get_tipo_dato_display())
    tipo_dato_display.short_description = 'Tipo de Dato'
    
    def accion_al_vencer_display(self, obj):
        color = '#dc3545' if obj.accion_al_vencer == 'eliminar' else '#17a2b8'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_accion_al_vencer_display()
        )
    accion_al_vencer_display.short_description = 'Acción'
    
    def activa_display(self, obj):
        if obj.activa:
            return format_html('<span style="color: #28a745;">✓ Activa</span>')
        return format_html('<span style="color: #6c757d;">✗ Inactiva</span>')
    activa_display.short_description = 'Estado'


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    """Administrador para Intentos de Login"""
    
    list_display = [
        'timestamp',
        'username',
        'ip_address',
        'exitoso_display',
        'intentos_recientes',
    ]
    list_filter = [
        'exitoso',
        'timestamp',
    ]
    search_fields = [
        'username',
        'ip_address',
    ]
    ordering = ['-timestamp']
    readonly_fields = [
        'username',
        'ip_address',
        'timestamp',
        'exitoso',
        'user_agent',
    ]
    
    fieldsets = (
        ('Información del Intento', {
            'fields': ('username', 'exitoso', 'timestamp')
        }),
        ('Información Técnica', {
            'fields': ('ip_address', 'user_agent')
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def exitoso_display(self, obj):
        if obj.exitoso:
            return format_html('<span style="color: #28a745; font-weight: bold;">✓ Exitoso</span>')
        return format_html('<span style="color: #dc3545; font-weight: bold;">✗ Fallido</span>')
    exitoso_display.short_description = 'Estado'
    
    def intentos_recientes(self, obj):
        """Muestra intentos recientes del usuario"""
        count = LoginAttempt.obtener_intentos_recientes(obj.username)
        if count >= 5:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">🔒 {} (BLOQUEADO)</span>',
                count
            )
        elif count >= 3:
            return format_html(
                '<span style="color: #ffc107; font-weight: bold;">⚠️ {}</span>',
                count
            )
        return format_html('<span style="color: #28a745;">{}</span>', count)
    intentos_recientes.short_description = 'Intentos (30 min)'
