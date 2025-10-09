from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@method_decorator(login_required, name='dispatch')
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