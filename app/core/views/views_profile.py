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
    """Vista para eliminar la cuenta del usuario permanentemente
    
    Esta vista elimina:
    - La cuenta del profesional
    - Todos los niños vinculados (CASCADE)
    - Todas las evaluaciones de esos niños (CASCADE desde games.Evaluacion)
    - Todos los reportes IA (CASCADE)
    - Todas las validaciones profesionales (CASCADE)
    - Todas las citas (CASCADE)
    - Todos los consentimientos GDPR (CASCADE)
    - Todas las auditorías donde el usuario es NULL (SET_NULL en AuditoriaAcceso)
    """
    
    def post(self, request, *args, **kwargs):
        """Procesar la eliminación de la cuenta y todos sus datos relacionados"""
        user = request.user
        username = user.username
        email = user.email
        
        try:
            # Importar modelos necesarios para contar
            from app.core.models import Nino, Cita, ConsentimientoGDPR, ValidacionProfesional
            from app.games.models import Evaluacion
            
            # Contar elementos antes de eliminar (para logging/auditoría)
            ninos_count = Nino.objects.filter(profesional=user).count()
            citas_count = Cita.objects.filter(usuario=user).count()
            consentimientos_count = ConsentimientoGDPR.objects.filter(usuario=user).count()
            validaciones_count = ValidacionProfesional.objects.filter(profesional=user).count()
            
            # Contar evaluaciones de los niños del profesional
            evaluaciones_count = 0
            for nino in Nino.objects.filter(profesional=user):
                evaluaciones_count += Evaluacion.objects.filter(nino=nino).count()
            
            # Logging de la operación
            import logging
            logger = logging.getLogger('audit')
            logger.info(
                f"ELIMINACIÓN DE CUENTA - Usuario: {username} ({email}) | "
                f"Niños: {ninos_count} | Evaluaciones: {evaluaciones_count} | "
                f"Citas: {citas_count} | Consentimientos: {consentimientos_count} | "
                f"Validaciones: {validaciones_count}"
            )
            
            # Cerrar sesión del usuario ANTES de eliminar
            from django.contrib.auth import logout
            logout(request)
            
            # ELIMINACIÓN EN CASCADA:
            # Al eliminar el usuario (Profesional), Django automáticamente eliminará:
            # 1. Niños (profesional FK con CASCADE)
            # 2. Evaluaciones (nino FK con CASCADE en games.Evaluacion)
            # 3. SesionJuego (evaluacion FK con CASCADE)
            # 4. PruebaCognitiva (evaluacion FK con CASCADE)
            # 5. ReporteIA (evaluacion FK con CASCADE)
            # 6. ValidacionProfesional (profesional FK con CASCADE)
            # 7. Citas (usuario FK con CASCADE)
            # 8. ConsentimientoGDPR (usuario FK con CASCADE)
            # 9. ConsentimientoTutor (nino FK con CASCADE)
            # 10. AuditoriaAcceso (usuario FK con SET_NULL - se mantiene pero sin usuario)
            
            user.delete()
            
            # Log final
            logger.info(f"CUENTA ELIMINADA EXITOSAMENTE - {username} ({email})")
            
            # Mensaje de confirmación (se guarda en cookie para mostrarlo después del redirect)
            messages.success(
                request, 
                f'✅ Tu cuenta y todos los datos asociados han sido eliminados permanentemente. '
                f'Gracias por usar DislexIA.'
            )
            
            # Redirigir al login
            response = redirect('core:login')
            response.set_cookie('account_deleted', 'true', max_age=10)
            return response
            
        except Exception as e:
            # Log del error
            import logging
            logger = logging.getLogger('audit')
            logger.error(f"ERROR AL ELIMINAR CUENTA - Usuario: {username} - Error: {str(e)}", exc_info=True)
            
            messages.error(
                request, 
                f'❌ Error al eliminar la cuenta: {str(e)}. Por favor, contacta con soporte.'
            )
            return redirect('core:settings')
