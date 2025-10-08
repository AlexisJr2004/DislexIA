from django.views.generic import TemplateView
from .models import Juego

class GameListView(TemplateView):
    template_name = 'game-list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener todos los juegos activos ordenados por su orden de visualización
        juegos = Juego.objects.filter(activo=True).order_by('orden_visualizacion', 'nombre')
        
        # Actualizar estadísticas de cada juego
        for juego in juegos:
            juego.actualizar_estadisticas()
        
        context.update({
            'page_title': 'Juegos - DislexIA',
            'active_section': 'games',
            'juegos': juegos,
        })
        return context

class BuscarPalabrasView(TemplateView):
    template_name = '/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Buscar Palabras - DislexIA',
            'active_section': 'games',
        })
        return context

class OrdenarPalabrasView(TemplateView):
    template_name = '/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Ordenar Palabras - DislexIA',
            'active_section': 'games',
        })
        return context

class QuizInteractivoView(TemplateView):
    template_name = '/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Quiz Interactivo - DislexIA',
            'active_section': 'games',
        })
        return context

class SeleccionarPalabraImagenView(TemplateView):
    template_name = '/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Seleccionar Palabra por Imagen - DislexIA',
            'active_section': 'games',
        })
        return context

class EscribirNombreObjetoView(TemplateView):
    template_name = '/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Escribir Nombre del Objeto - DislexIA',
            'active_section': 'games',
        })
        return context

class CompletarPalabraLetraView(TemplateView):
    template_name = '/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Completar Palabra con Letra - DislexIA',
            'active_section': 'games',
        })
        return context

class SeleccionarPalabraAudioView(TemplateView):
    template_name = '/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Seleccionar Palabra por Audio - DislexIA',
            'active_section': 'games',
        })
        return context

class EncontrarErrorPalabraView(TemplateView):
    template_name = '/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Encontrar Error en Palabra - DislexIA',
            'active_section': 'games',
        })
        return context
