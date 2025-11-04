"""
Middleware para auditoría de accesos GDPR
Registra automáticamente acciones sobre datos personales
"""
import logging
from django.utils.deprecation import MiddlewareMixin
from app.core.models import AuditoriaAcceso

logger = logging.getLogger('audit')


def get_client_ip(request):
    """Obtiene la IP real del cliente considerando proxies"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
    return ip


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware para auditoría automática de operaciones sensibles
    Registra accesos a datos personales según GDPR Art. 30
    """
    
    # Rutas que deben ser auditadas
    AUDIT_PATHS = [
        '/profile/',
        '/settings/',
        '/nino/',
        '/evaluacion/',
        '/reporte/',
        '/exportar-datos/',
        '/admin/',
    ]
    
    # Métodos HTTP que implican modificación de datos
    MODIFICATION_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
    
    def process_request(self, request):
        """Procesa la solicitud antes de llegar a la vista"""
        # Guardar la IP y user agent en el request para uso posterior
        request.client_ip = get_client_ip(request)
        request.user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        return None
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """Procesa la vista antes de ejecutarla"""
        # Solo auditar si el usuario está autenticado
        if not request.user.is_authenticated:
            return None
        
        # Verificar si la ruta debe ser auditada
        path = request.path
        should_audit = any(audit_path in path for audit_path in self.AUDIT_PATHS)
        
        if should_audit:
            # Determinar el tipo de acción
            if request.method == 'GET':
                accion = 'READ'
            elif request.method == 'POST':
                accion = 'CREATE'
            elif request.method in ['PUT', 'PATCH']:
                accion = 'UPDATE'
            elif request.method == 'DELETE':
                accion = 'DELETE'
            else:
                accion = 'READ'
            
            # Intentar extraer información de la ruta
            tabla_afectada = self._extract_model_from_path(path)
            registro_id = self._extract_id_from_kwargs(view_kwargs)
            
            # Registrar la auditoría de manera asíncrona (no bloquear la request)
            try:
                AuditoriaAcceso.registrar(
                    usuario=request.user,
                    accion=accion,
                    tabla_afectada=tabla_afectada,
                    registro_id=registro_id,
                    ip_address=request.client_ip,
                    detalles={
                        'path': path,
                        'method': request.method,
                        'view': view_func.__name__,
                    },
                    user_agent=request.user_agent
                )
                
                # Log adicional en archivo
                logger.info(
                    f"AUDIT: {request.user.username} - {accion} - {tabla_afectada} - "
                    f"ID:{registro_id} - IP:{request.client_ip}"
                )
            except Exception as e:
                # No bloquear la request si falla el logging
                logger.error(f"Error en auditoría: {str(e)}")
        
        return None
    
    def _extract_model_from_path(self, path):
        """Extrae el nombre del modelo de la ruta"""
        if '/nino/' in path:
            return 'Nino'
        elif '/evaluacion/' in path:
            return 'Evaluacion'
        elif '/reporte/' in path:
            return 'ReporteIA'
        elif '/profile/' in path:
            return 'Profesional'
        elif '/settings/' in path:
            return 'Profesional'
        elif '/exportar-datos/' in path:
            return 'ExportacionDatos'
        elif '/admin/' in path:
            return 'Admin'
        else:
            return 'Unknown'
    
    def _extract_id_from_kwargs(self, view_kwargs):
        """Extrae el ID del registro de los kwargs de la vista"""
        # Buscar posibles nombres de parámetros ID
        id_params = ['pk', 'id', 'nino_id', 'evaluacion_id', 'reporte_id']
        for param in id_params:
            if param in view_kwargs:
                try:
                    return int(view_kwargs[param])
                except (ValueError, TypeError):
                    pass
        return None


class LoginAuditMiddleware(MiddlewareMixin):
    """
    Middleware específico para auditar eventos de autenticación
    """
    
    def process_request(self, request):
        """Audita intentos de login"""
        if request.path == '/login/' and request.method == 'POST':
            username = request.POST.get('username', '')
            ip_address = get_client_ip(request)
            
            # El éxito/fallo se determinará después en process_response
            request.login_attempt = {
                'username': username,
                'ip_address': ip_address,
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500]
            }
        
        return None
    
    def process_response(self, request, response):
        """Registra el resultado del intento de login"""
        if hasattr(request, 'login_attempt'):
            attempt = request.login_attempt
            
            # Determinar si fue exitoso basándose en el código de respuesta
            exitoso = response.status_code == 302  # Redirect indica éxito
            accion = 'LOGIN' if exitoso else 'LOGIN_FAILED'
            
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                
                # Intentar obtener el usuario
                usuario = None
                if exitoso and request.user.is_authenticated:
                    usuario = request.user
                else:
                    # Para fallos, intentar obtener el usuario por username
                    try:
                        usuario = User.objects.get(username=attempt['username'])
                    except User.DoesNotExist:
                        pass
                
                AuditoriaAcceso.registrar(
                    usuario=usuario,
                    accion=accion,
                    tabla_afectada='Auth',
                    ip_address=attempt['ip_address'],
                    exitoso=exitoso,
                    mensaje_error='' if exitoso else 'Credenciales inválidas',
                    user_agent=attempt['user_agent'],
                    detalles={'username_attempt': attempt['username']}
                )
                
                logger.info(
                    f"AUTH: {'SUCCESS' if exitoso else 'FAILED'} - "
                    f"{attempt['username']} - IP:{attempt['ip_address']}"
                )
            except Exception as e:
                logger.error(f"Error en auditoría de login: {str(e)}")
        
        return response
