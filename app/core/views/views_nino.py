from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import UpdateView, ListView, DeleteView
from django.views.decorators.http import require_http_methods
from app.core.models import Nino
from app.core.forms.forms_profile import NinoForm
import logging

logger = logging.getLogger(__name__)

@method_decorator(login_required, name='dispatch')
class EditarNinoView(UpdateView):
    """Vista para editar los datos de un niño asociado a un profesional"""
    model = Nino
    form_class = NinoForm
    template_name = 'nino/editar_nino.html'
    success_url = reverse_lazy('core:lista_ninos')

    def get_object(self, queryset=None):
        """Asegurarse de que el profesional solo pueda editar sus propios niños."""
        return get_object_or_404(Nino, pk=self.kwargs['pk'], profesional=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'El niño ha sido actualizado exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Hubo un error al actualizar el niño. Por favor, verifica los datos ingresados.')
        return super().form_invalid(form)

    def get_initial(self):
        """Asegurar que los valores iniciales incluyan la fecha de nacimiento."""
        initial = super().get_initial()
        nino = self.get_object()
        initial['fecha_nacimiento'] = nino.fecha_nacimiento.strftime('%Y-%m-%d')
        return initial

@method_decorator(login_required, name='dispatch')
class ObtenerDatosNinoView(View):
    """Vista para obtener datos de un niño en formato JSON"""
    
    def get(self, request, pk):
        """Devuelve los datos de un niño en formato JSON."""
        try:
            nino = Nino.objects.get(pk=pk, profesional=request.user)
            return JsonResponse({
                'success': True,
                'nino': {
                    'id': nino.id,
                    'nombres': nino.nombres,
                    'apellidos': nino.apellidos,
                    'fecha_nacimiento': nino.fecha_nacimiento.strftime('%Y-%m-%d'),
                    'edad': nino.edad,
                    'genero': nino.genero,
                    'idioma_nativo': nino.idioma_nativo,
                    'imagen': nino.imagen.url if nino.imagen else None,
                }
            })
        except Nino.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Niño no encontrado.'}, status=404)

@method_decorator(login_required, name='dispatch')
class ListaNinosView(ListView):
    """Vista para listar todos los niños asociados al profesional"""
    model = Nino
    template_name = 'nino/lista_ninos.html'
    context_object_name = 'ninos'
    
    def get_queryset(self):
        """Filtrar solo los niños del profesional actual"""
        return Nino.objects.filter(profesional=self.request.user).order_by('-fecha_registro')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Lista de Niños - DislexIA',
            'active_section': 'lista_ninos',
        })
        return context

@method_decorator(login_required, name='dispatch')
class EliminarNinoView(DeleteView):
    """Vista para eliminar un niño con confirmación"""
    model = Nino
    template_name = 'nino/confirmar_eliminar_nino.html'
    success_url = reverse_lazy('core:lista_ninos')
    
    def get_object(self, queryset=None):
        """Asegurarse de que el profesional solo pueda eliminar sus propios niños."""
        return get_object_or_404(Nino, pk=self.kwargs['pk'], profesional=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        """Personalizar el mensaje de éxito"""
        nino = self.get_object()
        nombre_completo = nino.nombre_completo
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, f'El niño {nombre_completo} ha sido eliminado exitosamente.')
        return response

@login_required
@require_http_methods(["POST"])
def agregar_nino_ajax(request):
    """Agregar un niño mediante AJAX"""
    try:
        logger.info(f"=== Iniciando agregar_nino_ajax para usuario {request.user} ===")
        logger.info(f"POST data: {request.POST}")
        logger.info(f"FILES: {request.FILES}")
        
        form = NinoForm(request.POST, request.FILES)
        
        if form.is_valid():
            nino = form.save(commit=False)
            nino.profesional = request.user
            nino.save()
            
            logger.info(f"Niño guardado exitosamente: {nino.id} - {nino.nombre_completo}")
            
            # Formatear fecha de nacimiento
            from datetime import datetime
            fecha_formatted = nino.fecha_nacimiento.strftime('%d/%m/%Y')
            
            return JsonResponse({
                'success': True,
                'message': f'El niño {nino.nombre_completo} ha sido agregado exitosamente.',
                'nino': {
                    'id': nino.id,
                    'nombres': nino.nombres,
                    'apellidos': nino.apellidos,
                    'nombre_completo': nino.nombre_completo,
                    'edad': nino.edad,
                    'genero': nino.genero,
                    'idioma_nativo': nino.idioma_nativo,
                    'fecha_nacimiento_formatted': fecha_formatted,
                    'imagen_url': nino.imagen.url if nino.imagen else None
                }
            })
        else:
            logger.error(f"Errores de validación del formulario: {form.errors}")
            logger.error(f"Errores por campo: {dict(form.errors)}")
            
            return JsonResponse({
                'success': False,
                'error': 'Error de validación. Por favor revisa los campos.',
                'errors': dict(form.errors)
            }, status=400)
            
    except Exception as e:
        logger.exception(f"Error inesperado en agregar_nino_ajax: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Error del servidor: {str(e)}'
        }, status=500)
