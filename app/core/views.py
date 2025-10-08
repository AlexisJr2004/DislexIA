from django.views.generic import TemplateView

class CalendarView(TemplateView):
    template_name = 'calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Calendario - DislexIA',
            'active_section': 'calendar',
        })
        return context

class DocumentsView(TemplateView):
    template_name = 'documents.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Recursos Digitales - DislexIA',
            'active_section': 'documents',
        })
        return context

class SettingsView(TemplateView):
    template_name = 'settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Configuraciones - DislexIA',
            'active_section': 'settings',
        })
        return context

class SupportView(TemplateView):
    template_name = 'support.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Soporte - DislexIA',
            'active_section': 'support',
        })
        return context

class ProfileView(TemplateView):
    template_name = 'profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Perfil - DislexIA',
            'active_section': 'profile',
        })
        return context
