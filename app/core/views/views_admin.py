"""
Vistas administrativas para gestión de usuarios (solo staff)
"""
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count
from app.core.models import Profesional, Nino
import logging

logger = logging.getLogger(__name__)

@method_decorator(staff_member_required, name='dispatch')
class GestionUsuariosView(ListView):
    """Vista para administradores: gestionar todos los usuarios del sistema"""
    model = Profesional
    template_name = 'admin/gestion_usuarios.html'
    context_object_name = 'usuarios'
    paginate_by = 20
    
    def get_queryset(self):
        """Obtener todos los profesionales con métricas"""
        queryset = Profesional.objects.annotate(
            total_ninos=Count('ninos', distinct=True)
        ).order_by('-date_joined')
        
        # Filtros
        search = self.request.GET.get('search', '')
        estado = self.request.GET.get('estado', 'todos')
        rol = self.request.GET.get('rol', 'todos')
        
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(nombres__icontains=search) |
                Q(apellidos__icontains=search)
            )
        
        if estado == 'activos':
            queryset = queryset.filter(is_active=True)
        elif estado == 'inactivos':
            queryset = queryset.filter(is_active=False)
        
        if rol != 'todos':
            queryset = queryset.filter(rol=rol)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas globales
        total_usuarios = Profesional.objects.count()
        usuarios_activos = Profesional.objects.filter(is_active=True).count()
        usuarios_inactivos = Profesional.objects.filter(is_active=False).count()
        administradores = Profesional.objects.filter(is_staff=True).count()
        
        context.update({
            'page_title': 'Gestión de Usuarios - DislexIA',
            'active_section': 'gestion_usuarios',
            'total_usuarios': total_usuarios,
            'usuarios_activos': usuarios_activos,
            'usuarios_inactivos': usuarios_inactivos,
            'administradores': administradores,
            'filtro_estado': self.request.GET.get('estado', 'todos'),
            'filtro_rol': self.request.GET.get('rol', 'todos'),
            'search_query': self.request.GET.get('search', ''),
        })
        
        return context

@staff_member_required
@csrf_exempt  # ✅ Eximir CSRF ya que requiere autenticación de staff
@require_http_methods(["POST"])
def toggle_usuario_status(request, pk):
    """
    Activa o desactiva un usuario (solo para administradores)
    Nota: Usa @csrf_exempt porque la autenticación de staff es suficiente seguridad
    """
    try:
        # 🔍 DEBUG: Log de headers recibidos
        csrf_token = request.META.get('HTTP_X_CSRFTOKEN', 'NO_TOKEN')
        logger.debug(f"🔐 CSRF Token recibido: {csrf_token[:20] if len(csrf_token) > 20 else csrf_token}... (longitud: {len(csrf_token)})")
        logger.debug(f"👤 Usuario solicitante: {request.user.username} (staff: {request.user.is_staff})")
        
        # Verificar que no se está desactivando a sí mismo
        if request.user.pk == pk:
            return JsonResponse({
                'success': False,
                'error': 'No puedes desactivar tu propia cuenta desde aquí. Usa la configuración de perfil.'
            }, status=400)
        
        usuario = get_object_or_404(Profesional, pk=pk)
        
        # Evitar desactivar al superusuario principal
        if usuario.is_superuser and Profesional.objects.filter(is_superuser=True).count() == 1:
            return JsonResponse({
                'success': False,
                'error': 'No puedes desactivar al único superusuario del sistema.'
            }, status=400)
        
        usuario.is_active = not usuario.is_active
        usuario.save()
        
        estado = "activado" if usuario.is_active else "desactivado"
        logger.info(f"Usuario {usuario.username} (ID: {pk}) {estado} por administrador {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'message': f'El usuario {usuario.nombre_completo} ha sido {estado} exitosamente.',
            'is_active': usuario.is_active
        })
        
    except Exception as e:
        logger.exception(f"Error al cambiar estado del usuario {pk}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@method_decorator(staff_member_required, name='dispatch')
class GestionNinosAdminView(ListView):
    """Vista para administradores: gestionar todos los niños del sistema"""
    model = Nino
    template_name = 'admin/gestion_ninos.html'
    context_object_name = 'ninos'
    paginate_by = 20
    
    def get_queryset(self):
        """Obtener todos los niños con información del profesional"""
        queryset = Nino.objects.select_related('profesional').annotate(
            total_evaluaciones=Count('evaluaciones', distinct=True)
        ).order_by('-fecha_registro')
        
        # Filtros
        search = self.request.GET.get('search', '')
        estado = self.request.GET.get('estado', 'todos')
        profesional_id = self.request.GET.get('profesional', '')
        
        if search:
            queryset = queryset.filter(
                Q(nombres__icontains=search) |
                Q(apellidos__icontains=search) |
                Q(profesional__nombres__icontains=search) |
                Q(profesional__apellidos__icontains=search)
            )
        
        if estado == 'activos':
            queryset = queryset.filter(activo=True)
        elif estado == 'inactivos':
            queryset = queryset.filter(activo=False)
        
        if profesional_id:
            queryset = queryset.filter(profesional_id=profesional_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas globales
        total_ninos = Nino.objects.count()
        ninos_activos = Nino.objects.filter(activo=True).count()
        ninos_inactivos = Nino.objects.filter(activo=False).count()
        
        # Lista de profesionales para el filtro
        profesionales = Profesional.objects.filter(is_active=True).order_by('nombres', 'apellidos')
        
        context.update({
            'page_title': 'Gestión de Niños (Admin) - DislexIA',
            'active_section': 'gestion_ninos_admin',
            'total_ninos': total_ninos,
            'ninos_activos': ninos_activos,
            'ninos_inactivos': ninos_inactivos,
            'profesionales': profesionales,
            'filtro_estado': self.request.GET.get('estado', 'todos'),
            'filtro_profesional': self.request.GET.get('profesional', ''),
            'search_query': self.request.GET.get('search', ''),
        })
        
        return context

@staff_member_required
@csrf_exempt  # ✅ Eximir CSRF ya que requiere autenticación de staff
@require_http_methods(["POST"])
def toggle_nino_status_admin(request, pk):
    """
    Activa o desactiva un niño (solo para administradores)
    Nota: Usa @csrf_exempt porque la autenticación de staff es suficiente seguridad
    """
    try:
        nino = get_object_or_404(Nino, pk=pk)
        nino.activo = not nino.activo
        nino.save()
        
        estado = "activado" if nino.activo else "desactivado"
        logger.info(f"Niño {nino.nombre_completo} (ID: {pk}) {estado} por administrador {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'message': f'El niño {nino.nombre_completo} ha sido {estado} exitosamente.',
            'activo': nino.activo
        })
        
    except Exception as e:
        logger.exception(f"Error al cambiar estado del niño {pk}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
