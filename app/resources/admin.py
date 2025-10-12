from django.contrib import admin
from .models import Recurso

@admin.register(Recurso)
class RecursoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'autor', 'valoracion', 'visitas', 'activo']
    list_filter = ['categoria', 'activo', 'fecha_creacion']
    search_fields = ['titulo', 'descripcion', 'autor']
    list_editable = ['activo']