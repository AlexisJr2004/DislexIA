from django.views.generic import TemplateView

class BuscarPalabrasView(TemplateView):
    template_name = 'buscar-palabras.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Buscar Palabras - DislexIA',
            'active_section': 'games',
        })
        return context

class OrdenarPalabrasView(TemplateView):
    template_name = 'ordenar-palabras.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Ordenar Palabras - DislexIA',
            'active_section': 'games',
        })
        return context

class QuizInteractivoView(TemplateView):
    template_name = 'quiz-interactivo.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Quiz Interactivo - DislexIA',
            'active_section': 'games',
        })
        return context
