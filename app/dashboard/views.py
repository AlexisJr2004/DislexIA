from django.views.generic import TemplateView

class DashboardView(TemplateView):
    """
    Vista principal del dashboard que muestra el resumen de actividades.
    """
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Dashboard - Panel Administrativo',
            'active_section': 'dashboard',
            # Aquí puedes agregar datos específicos del dashboard
            'total_courses': 12,
            'completed_courses': 8,
            'progress_percentage': 65,
        })
        return context