from django.contrib import admin
from .models import Juego, Evaluacion, PruebaCognitiva

@admin.register(Juego)
class JuegoAdmin(admin.ModelAdmin):
    """Administrador para el modelo Juego - completamente editable"""
    
    list_display = [
        'nombre', 
        'categoria_display',
        'dificultad', 
        'color_tema', 
        'puntuacion_promedio',
        'total_jugadas',
        'total_completados',
        'porcentaje_completado',
        'activo',
        'orden_visualizacion'
    ]
    list_filter = [
        'categoria', 
        'dificultad', 
        'color_tema', 
        'activo',
        'fecha_creacion'
    ]
    search_fields = ['nombre', 'descripcion']
    ordering = ['orden_visualizacion', 'nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'categoria', 'imagen')
        }),
        ('Configuración Técnica', {
            'fields': ('dificultad', 'color_tema', 'duracion_estimada_minutos', 'activo', 'orden_visualizacion')
        }),
        ('Estadísticas', {
            'fields': ('puntuacion_promedio', 'total_jugadas', 'total_completados'),
            'classes': ('collapse',)
        }),
        ('Información Técnica', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    # Acciones personalizadas
    actions = ['activar_juegos', 'desactivar_juegos']
    
    def activar_juegos(self, request, queryset):
        """Activa los juegos seleccionados"""
        updated = queryset.update(activo=True)
        self.message_user(request, f'{updated} juegos activados correctamente.')
    activar_juegos.short_description = 'Activar juegos seleccionados'
    
    def desactivar_juegos(self, request, queryset):
        """Desactiva los juegos seleccionados"""
        updated = queryset.update(activo=False)
        self.message_user(request, f'{updated} juegos desactivados correctamente.')
    desactivar_juegos.short_description = 'Desactivar juegos seleccionados'
    
    def categoria_display(self, obj):
        """Muestra la categoría con formato legible"""
        return obj.categoria_display
    categoria_display.short_description = 'Categoría'
    
    def porcentaje_completado(self, obj):
        """Muestra el porcentaje de completado formateado"""
        return f"{obj.porcentaje_completado}%"
    porcentaje_completado.short_description = 'Completado (%)'
    
    def save_model(self, request, obj, form, change):
        """Override save para actualizar estadísticas después de guardar"""
        super().save_model(request, obj, form, change)

@admin.register(Evaluacion)
class EvaluacionAdmin(admin.ModelAdmin):
    """Administrador para el modelo Evaluacion - solo lectura"""
    
    list_display = [
        'id',
        'nino',
        'estado',
        'fecha_hora_inicio',
        'duracion_total_minutos',
        'precision_promedio',
        'total_clics',
        'total_aciertos',
        'total_errores'
    ]
    list_filter = ['estado', 'fecha_hora_inicio', 'dispositivo']
    search_fields = ['nino__nombres', 'nino__apellidos']
    ordering = ['-fecha_hora_inicio']
    
    # Solo lectura - no se puede agregar, cambiar o eliminar
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    # Hacer todos los campos de solo lectura
    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields]

@admin.register(PruebaCognitiva)
class PruebaCognitivaAdmin(admin.ModelAdmin):
    """Administrador para el modelo PruebaCognitiva - solo lectura"""
    
    list_display = [
        'id',
        'evaluacion',
        'juego',
        'juego_categoria',
        'numero_prueba',
        'clics',
        'aciertos',
        'errores',
        'precision',
        'tasa_error',
        'tiempo_respuesta_segundos_formatted'
    ]
    list_filter = ['juego__categoria', 'fecha_ejecucion', 'juego']
    search_fields = ['evaluacion__nino__nombres', 'evaluacion__nino__apellidos', 'juego__nombre']
    ordering = ['-fecha_ejecucion']
    
    # Solo lectura - no se puede agregar, cambiar o eliminar
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    # Hacer todos los campos de solo lectura
    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields]
    
    def juego_categoria(self, obj):
        """Muestra la categoría del juego"""
        return obj.juego.categoria_display if obj.juego else 'Sin categoría'
    juego_categoria.short_description = 'Categoría del Juego'
    
    def tiempo_respuesta_segundos_formatted(self, obj):
        """Muestra el tiempo de respuesta en segundos formateado"""
        return f"{obj.tiempo_respuesta_segundos:.2f}s"
    tiempo_respuesta_segundos_formatted.short_description = 'Tiempo Respuesta'