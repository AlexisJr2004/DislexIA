"""
Middleware de seguridad para timeout de sesión
"""
import logging
from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class SessionTimeoutMiddleware(MiddlewareMixin):
    """
    Middleware para cerrar sesión automáticamente después de 30 minutos de inactividad.
    
    Funciona registrando la última actividad del usuario en la sesión y comparándola
    con el tiempo actual. Si han pasado más de 30 minutos, cierra la sesión.
    """
    
    # Timeout en segundos (30 minutos = 1800 segundos)
    TIMEOUT = 1800
    
    def process_request(self, request):
        """Verifica la inactividad del usuario"""
        # Solo aplicar a usuarios autenticados
        if request.user.is_authenticated:
            # Obtener el timestamp de última actividad
            last_activity = request.session.get('last_activity')
            
            if last_activity:
                # Calcular tiempo transcurrido
                now = timezone.now().timestamp()
                elapsed_time = now - last_activity
                
                # Si han pasado más de 30 minutos, cerrar sesión
                if elapsed_time > self.TIMEOUT:
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
        
        return None
