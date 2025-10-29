from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, CreateView, UpdateView
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from app.core.models import ValidacionProfesional, ReporteIA
from app.core.forms.forms_report import ValidacionProfesionalForm
from ..utils.pdf_utils import render_to_pdf # <-- Importar la nueva utilidad
from app.games.models import Evaluacion # <-- Importar Evaluation
from django.db.models import Avg, Sum, Count # ¡Importa Avg, Sum, Count!

@method_decorator(login_required, name='dispatch')
class ReporteIADetailView(TemplateView):
    """Vista para mostrar el detalle del reporte IA de un niño"""
    template_name = 'report/reporte_ia_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reporte_id = self.kwargs.get('pk')
        
        try:
            # Corrección: filtrar por evaluacion__nino__profesional
            reporte = ReporteIA.objects.get(id=reporte_id, evaluacion__nino__profesional=self.request.user)
            context['reporte'] = reporte
            context['page_title'] = f'Reporte IA - {reporte.evaluacion.nino.nombre_completo}'
        except ReporteIA.DoesNotExist:
            messages.error(self.request, 'El reporte solicitado no existe o no tienes permiso para verlo.')
            context['reporte'] = None
        
        return context
    
@method_decorator(login_required, name='dispatch')
class ValidacionProfesionalCreateView(CreateView):
    """Vista para crear una validación profesional asociada a un reporte IA"""
    model = ValidacionProfesional
    form_class = ValidacionProfesionalForm
    template_name = 'report/validacion_profesional_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.reporteia_id = self.kwargs.get('reporteia_id')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        reporte = get_object_or_404(ReporteIA, id=self.reporteia_id, evaluacion__nino__profesional=self.request.user)
        form.instance.profesional = self.request.user
        form.instance.ReporteIA = reporte
        messages.success(self.request, 'Validación profesional creada exitosamente.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('core:reporte_ia_detail', kwargs={'pk': self.reporteia_id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Validar Reporte IA - DislexIA'
        context['reporteia_id'] = self.reporteia_id
        return context

@method_decorator(login_required, name='dispatch')
class ValidacionProfesionalUpdateView(UpdateView):
    """Vista para actualizar una validación profesional asociada a un reporte IA"""
    model = ValidacionProfesional
    form_class = ValidacionProfesionalForm
    template_name = 'report/validacion_profesional_form.html'
    
    def get_object(self, queryset=None):
        reporte = get_object_or_404(ReporteIA, id=self.kwargs.get('reporteia_id'), evaluacion__nino__profesional=self.request.user)
        return get_object_or_404(ValidacionProfesional, ReporteIA=reporte, profesional=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Validación profesional actualizada exitosamente.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('core:reporte_ia_detail', kwargs={'pk': self.kwargs.get('reporteia_id')})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Actualizar Validación de Reporte IA - DislexIA'
        context['reporteia_id'] = self.kwargs.get('reporteia_id')
        return context

# --- Esta es la función en la que nos enfocamos ---
@login_required
def generar_reporte_pdf(request, pk):
    try:
        reporte = get_object_or_404(
            ReporteIA, 
            pk=pk, 
            evaluacion__nino__profesional=request.user
        )
        
        main_session = reporte.evaluacion 
        nino = main_session.nino
        
        statistics = main_session.pruebas_cognitivas.all() \
            .values(
                'juego__nombre', 
                'juego__dificultad', 
                'juego__color_tema'
            ) \
            .annotate(
                total_aciertos=Sum('aciertos'),
                total_errores=Sum('errores'),
                total_puntaje=Sum('puntaje'),
                total_clics=Sum('clics'),
                avg_precision=Avg('precision'),
                veces_jugado=Count('id')
            ).order_by('juego__nombre')
        
        # DEBUG: Ver datos
        for stat in statistics:
            print(f"Juego: {stat['juego__nombre']}, Precisión: {stat['avg_precision']}")
        
        context = {
            'reporte': reporte,
            'game_session': main_session,
            'nino': nino,
            'evaluations': statistics,
        }
        
        template_src = 'report/reporte_pdf_template.html'
        return render_to_pdf(request, template_src, context)
        
    except Exception as e:
        import traceback
        print("ERROR EN GENERAR PDF:")
        print(traceback.format_exc())
        return HttpResponse(f"Error: {str(e)}", status=500)