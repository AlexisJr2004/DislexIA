from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from app.core.forms.forms_profile import ProfesionalUpdateForm
from django.shortcuts import redirect

@method_decorator(login_required, name='dispatch')
class ProfileView(TemplateView):
    template_name = 'profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Perfil - DislexIA',
            'active_section': 'profile',
            'form': ProfesionalUpdateForm(instance=self.request.user)
        })
        return context

@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(UpdateView):
    """Vista para actualizar el perfil del profesional"""
    model = None  # Se establece dinámicamente
    form_class = ProfesionalUpdateForm
    success_url = reverse_lazy('core:profile')
    
    def get_object(self, queryset=None):
        # Retornar el usuario actual
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, '¡Perfil actualizado exitosamente!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al actualizar el perfil. Por favor, verifica los datos.')
        return redirect('core:profile')

@method_decorator(login_required, name='dispatch')
class DeleteAccountView(TemplateView):
    """Vista para eliminar la cuenta del usuario permanentemente"""
    
    def post(self, request, *args, **kwargs):
        """Procesar la eliminación de la cuenta"""
        user = request.user
        username = user.username
        
        try:
            # Cerrar sesión del usuario
            from django.contrib.auth import logout
            logout(request)
            
            # Eliminar la cuenta permanentemente
            user.delete()
            
            # Mensaje de confirmación (se guarda en cookie para mostrarlo después del redirect)
            messages.success(request, f'La cuenta de {username} ha sido eliminada permanentemente.')
            
            # Redirigir al login
            response = redirect('core:login')
            response.set_cookie('account_deleted', 'true', max_age=10)
            return response
            
        except Exception as e:
            messages.error(request, f'Error al eliminar la cuenta: {str(e)}')
            return redirect('core:settings')
