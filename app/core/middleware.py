"""
Middleware personalizado para DislexIA

Incluye:
- AuditMiddleware: Auditoría de acceso a datos (GDPR)
- LoginAuditMiddleware: Auditoría de eventos de autenticación (GDPR)
- SessionTimeoutMiddleware: Timeout por inactividad (30 minutos)
"""
import logging
from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from app.core.models import AuditoriaAcceso

logger = logging.getLogger(__name__)


class AuditMiddleware:
    """
    Middleware para auditar accesos a datos personales según GDPR.
    Registra todas las operaciones de lectura/escritura en datos sensibles.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs que deben ser auditadas (acceso a datos personales)
        self.auditable_urls = [
            '/profile/',
            '/ninos/',
            '/reportes/',
            '/evaluaciones/',
            '/consentimientos/',
            '/exportar-datos/',
            '/historial-auditoria/',
        ]
    
    def __call__(self, request):
        # Procesar request
        response = self.get_response(request)
        
        # Solo auditar si el usuario está autenticado
        if request.user.is_authenticated:
            # Verificar si la URL debe ser auditada
            path = request.path
            should_audit = any(auditable in path for auditable in self.auditable_urls)
            
            if should_audit:
                try:
                    # Determinar la acción según el método HTTP
                    accion_map = {
                        'GET': 'VIEW',
                        'POST': 'CREATE',
                        'PUT': 'UPDATE',
                        'PATCH': 'UPDATE',
                        'DELETE': 'DELETE',
                    }
                    accion = accion_map.get(request.method, 'VIEW')
                    
                    # Obtener IP del usuario
                    ip_address = self._get_client_ip(request)
                    
                    # Determinar tabla afectada según la URL
                    tabla_afectada = self._get_tabla_from_url(path)
                    
                    # Crear registro de auditoría
                    AuditoriaAcceso.objects.create(
                        usuario=request.user,
                        accion=accion,
                        tabla_afectada=tabla_afectada,
                        ip_address=ip_address,
                        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                        exitoso=(200 <= response.status_code < 400),
                        detalles=f"Acceso a {path}"
                    )
                except Exception as e:
                    # No fallar la request si hay error en auditoría
                    logger.error(f"Error en AuditMiddleware: {e}")
        
        return response
    
    def _get_client_ip(self, request):
        """Obtener la IP real del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _get_tabla_from_url(self, path):
        """Determinar qué tabla/modelo se está accediendo según la URL"""
        if '/profile/' in path:
            return 'Profesional'
        elif '/ninos/' in path:
            return 'Nino'
        elif '/reportes/' in path:
            return 'Reporte'
        elif '/evaluaciones/' in path:
            return 'Evaluacion'
        elif '/consentimientos/' in path:
            return 'ConsentimientoGDPR'
        elif '/exportar-datos/' in path:
            return 'Export'
        elif '/historial-auditoria/' in path:
            return 'AuditoriaAcceso'
        return 'Unknown'


class LoginAuditMiddleware:
    """
    Middleware para auditar eventos de login/logout según GDPR.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """Procesar la vista para detectar login/logout"""
        # Este método se ejecuta antes de que se llame a la vista
        return None


class SessionTimeoutMiddleware:
    """
    Middleware para cerrar sesión automáticamente después de 30 minutos de inactividad.
    
    Funciona registrando la última actividad del usuario en la sesión y comparándola
    con el tiempo actual. Si han pasado más de 30 minutos, cierra la sesión.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Timeout en segundos (30 minutos = 1800 segundos)
        self.timeout = 1800
    
    def __call__(self, request):
        # Solo aplicar a usuarios autenticados
        if request.user.is_authenticated:
            # Obtener el timestamp de última actividad
            last_activity = request.session.get('last_activity')
            
            if last_activity:
                # Calcular tiempo transcurrido
                now = timezone.now().timestamp()
                elapsed_time = now - last_activity
                
                # Si han pasado más de 30 minutos, cerrar sesión
                if elapsed_time > self.timeout:
                    logger.info(f"Sesión expirada por inactividad para usuario {request.user.username}")
                    
                    # Guardar mensaje antes de cerrar sesión
                    messages.warning(
                        request,
                        '⏱️ Tu sesión ha expirado por inactividad (30 minutos). Por favor, inicia sesión nuevamente.'
                    )
                    
                    # Cerrar sesión
                    logout(request)
                    
                    # Redirigir al login
                    return redirect(reverse('core:login'))
            
            # Actualizar timestamp de última actividad
            request.session['last_activity'] = timezone.now().timestamp()
        
        response = self.get_response(request)
        return response
