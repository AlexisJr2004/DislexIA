from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, CreateView, UpdateView
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from app.core.models import ValidacionProfesional, ReporteIA
from app.core.forms.forms_report import ValidacionProfesionalForm
try:
    from ..utils.pdf_utils import render_to_pdf # <-- Importar la nueva utilidad
except ImportError:
    render_to_pdf = None  # Temporal para permitir migraciones
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
    """
    Vista para generar y descargar un PDF combinado del reporte de IA y las estadísticas.
    """
    
    # 1. Obtener el reporte de IA
    reporte = get_object_or_404(
        ReporteIA, 
        pk=pk, 
        evaluacion__nino__profesional=request.user
    )
    
    # 2. Obtener los objetos relacionados
    main_session = reporte.evaluacion 
    nino = main_session.nino
    
    # --- PASO 3: OBTENER ESTADÍSTICAS (¡CONSULTA ACTUALIZADA!) ---
    # Agrupamos las PruebasCognitivas por juego y calculamos los totales.
    statistics = main_session.pruebas_cognitivas.all() \
        .values(
            'juego__nombre', 
            'juego__dificultad', 
            'juego__color_tema'  # Para el color del header de la tarjeta
        ) \
        .annotate(
            total_aciertos=Sum('aciertos'),
            total_errores=Sum('errores'),
            total_puntaje=Sum('puntaje'),
            total_clics=Sum('clics'),
            avg_precision=Avg('precision'),
            veces_jugado=Count('id')  # Contar cuántas pruebas de este juego se hicieron
        ).order_by('juego__nombre')
    
    # 4. Preparar el contexto para la plantilla PDF
    context = {
        'reporte': reporte,
        'game_session': main_session, # Pasamos la 'Evaluacion' como 'game_session'
        'nino': nino,
        'evaluations': statistics, # Pasamos las estadísticas agrupadas
    }

    # Verificar que el nombre de la plantilla sea una cadena válida
    if not isinstance('report/reporte_pdf_template.html', str):
        raise ValueError("El nombre de la plantilla debe ser una cadena válida.")
    template_src = 'report/reporte_pdf_template.html'
    # 5. Renderizar el PDF
    print("Context for PDF generation:", context)  # Debugging line
    return render_to_pdf(request, template_src, context)

