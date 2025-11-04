"""
Vistas para cumplimiento GDPR
Incluye exportación de datos, gestión de consentimientos y derechos del usuario
"""
import json
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from app.core.models import (
    ConsentimientoGDPR, 
    AuditoriaAcceso,
    Nino
)
from app.games.models import Evaluacion, SesionJuego, PruebaCognitiva


@login_required
def exportar_datos_usuario(request):
    """
    Exporta todos los datos personales del usuario en formato JSON
    Cumplimiento: Artículo 20 GDPR (Derecho a la portabilidad de datos)
    """
    usuario = request.user
    
    # Registrar la exportación en auditoría
    AuditoriaAcceso.registrar(
        usuario=usuario,
        accion='EXPORT',
        tabla_afectada='ExportacionCompleta',
        ip_address=request.META.get('REMOTE_ADDR', '0.0.0.0'),
        detalles={'tipo_exportacion': 'datos_completos'},
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
    )
    
    # Recopilar todos los datos del usuario
    datos_exportacion = {
        'informacion_exportacion': {
            'fecha_exportacion': datetime.now().isoformat(),
            'version_gdpr': '1.0',
            'formato': 'JSON',
            'usuario_id': usuario.id,
        },
        'datos_personales': {
            'username': usuario.username,
            'email': usuario.email,
            'nombres': usuario.nombres,
            'apellidos': usuario.apellidos,
            'especialidad': usuario.especialidad,
            'numero_licencia': usuario.numero_licencia,
            'rol': usuario.rol,
            'fecha_registro': usuario.fecha_registro.isoformat() if usuario.fecha_registro else None,
            'ultimo_acceso': usuario.ultimo_acceso.isoformat() if usuario.ultimo_acceso else None,
        },
        'ninos_asignados': [],
        'evaluaciones_realizadas': [],
        'validaciones_profesionales': [],
        'citas': [],
        'consentimientos': [],
        'historial_auditoria': []
    }
    
    # Niños asignados
    for nino in usuario.ninos.all():
        datos_exportacion['ninos_asignados'].append({
            'id': nino.id,
            'nombres': nino.nombres,
            'apellidos': nino.apellidos,
            'edad': nino.edad,
            'genero': nino.genero,
            'fecha_registro': nino.fecha_registro.isoformat(),
        })
    
    # Evaluaciones (a través de los niños asignados)
    evaluaciones = Evaluacion.objects.filter(nino__profesional=usuario)
    for evaluacion in evaluaciones:
        eval_data = {
            'id': evaluacion.id,
            'nino': evaluacion.nino.nombre_completo,
            'fecha_inicio': evaluacion.fecha_hora_inicio.isoformat(),
            'fecha_fin': evaluacion.fecha_hora_fin.isoformat() if evaluacion.fecha_hora_fin else None,
            'estado': evaluacion.estado,
            'precision_promedio': float(evaluacion.precision_promedio),
            'total_aciertos': evaluacion.total_aciertos,
            'total_errores': evaluacion.total_errores,
        }
        datos_exportacion['evaluaciones_realizadas'].append(eval_data)
    
    # Validaciones profesionales
    for validacion in usuario.validaciones.all():
        datos_exportacion['validaciones_profesionales'].append({
            'id': validacion.id,
            'fecha': validacion.fecha_validacion.isoformat(),
            'riesgo_confirmado': validacion.riesgo_confirmado,
            'indice_ajustado': float(validacion.indice_ajustado),
            'diagnostico_final': validacion.diagnostico_final,
        })
    
    # Citas
    for cita in usuario.citas.all():
        datos_exportacion['citas'].append({
            'id': cita.id,
            'nombre_paciente': cita.nombre_paciente,
            'fecha': cita.fecha.isoformat(),
            'hora': cita.hora.isoformat(),
            'completada': cita.completada,
        })
    
    # Consentimientos
    for consentimiento in usuario.consentimientos_gdpr.all():
        datos_exportacion['consentimientos'].append({
            'fecha': consentimiento.fecha_consentimiento.isoformat(),
            'acepta_terminos': consentimiento.acepta_terminos,
            'acepta_privacidad': consentimiento.acepta_privacidad,
            'acepta_tratamiento_datos': consentimiento.acepta_tratamiento_datos,
            'version_terminos': consentimiento.version_terminos,
            'consentimiento_activo': consentimiento.consentimiento_activo,
        })
    
    # Historial de auditoría (últimos 100 registros)
    for auditoria in usuario.auditorias.all()[:100]:
        datos_exportacion['historial_auditoria'].append({
            'fecha': auditoria.timestamp.isoformat(),
            'accion': auditoria.get_accion_display(),
            'tabla': auditoria.tabla_afectada,
            'ip': auditoria.ip_address,
            'exitoso': auditoria.exitoso,
        })
    
    # Crear respuesta JSON descargable
    response = HttpResponse(
        json.dumps(datos_exportacion, indent=2, ensure_ascii=False),
        content_type='application/json; charset=utf-8'
    )
    filename = f'dislexia_datos_{usuario.username}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    messages.success(
        request,
        '✅ Datos exportados exitosamente. El archivo contiene toda su información personal.'
    )
    
    return response


@login_required
def vista_consentimientos(request):
    """
    Vista para gestionar los consentimientos del usuario
    """
    # Obtener consentimiento actual
    consentimiento = ConsentimientoGDPR.objects.filter(
        usuario=request.user,
        consentimiento_activo=True
    ).first()
    
    context = {
        'consentimiento': consentimiento,
        'tiene_consentimiento': consentimiento is not None,
    }
    
    return render(request, 'gdpr/consentimientos.html', context)


@login_required
@require_http_methods(["POST"])
def revocar_consentimiento(request):
    """
    Revoca el consentimiento del usuario
    Cumplimiento: Artículo 7.3 GDPR (Derecho a retirar el consentimiento)
    """
    consentimiento = ConsentimientoGDPR.objects.filter(
        usuario=request.user,
        consentimiento_activo=True
    ).first()
    
    if consentimiento:
        consentimiento.revocar_consentimiento()
        
        # Registrar en auditoría
        AuditoriaAcceso.registrar(
            usuario=request.user,
            accion='CONSENT_REVOKED',
            tabla_afectada='ConsentimientoGDPR',
            registro_id=consentimiento.id,
            ip_address=request.META.get('REMOTE_ADDR', '0.0.0.0'),
            detalles={'tipo': 'revocacion_consentimiento'}
        )
        
        messages.warning(
            request,
            '⚠️ Su consentimiento ha sido revocado. Su cuenta será desactivada.'
        )
        
        # Desactivar la cuenta del usuario
        request.user.is_active = False
        request.user.save()
        
        # Cerrar sesión
        from django.contrib.auth import logout
        logout(request)
        
        return redirect('core:login')
    
    messages.error(request, 'No se encontró un consentimiento activo.')
    return redirect('core:settings')


@login_required
def historial_auditoria_usuario(request):
    """
    Muestra el historial de acceso del usuario a sus propios datos
    Cumplimiento: Transparencia GDPR
    """
    # Obtener auditorías del usuario (paginado)
    auditorias = AuditoriaAcceso.objects.filter(
        usuario=request.user
    ).order_by('-timestamp')[:50]  # Últimas 50
    
    context = {
        'auditorias': auditorias,
    }
    
    return render(request, 'gdpr/historial_auditoria.html', context)


def obtener_ip_cliente(request):
    """Función helper para obtener la IP real del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
    return ip
