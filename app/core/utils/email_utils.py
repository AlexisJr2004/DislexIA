from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

def enviar_correo_cita_doctor(doctor, cita):
    """
    Envía un correo al doctor con los detalles de la cita agendada
    """
    asunto = f'Nueva cita agendada - {cita.nombre_paciente}'
    
    contexto = {
        'doctor_nombre': doctor.nombre_completo,
        'paciente_nombre': cita.nombre_paciente,
        'fecha': cita.fecha.strftime('%d/%m/%Y'),
        'hora': cita.hora.strftime('%H:%M'),
        'notas': cita.notas or 'Sin notas adicionales',
    }
    
    mensaje_html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Nueva Cita Agendada - DislexIA</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 80px 20px;">
            <tr>
                <td align="center">
                    <!-- Contenedor principal con sombra elegante -->
                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; background: linear-gradient(to bottom, #ffffff 0%, #fefefe 100%); border-radius: 20px; overflow: hidden; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08), 0 0 1px rgba(0, 0, 0, 0.05);">
                        
                        <!-- Header sofisticado -->
                        <tr>
                            <td style="padding: 60px 50px 40px 50px; text-align: center; background: linear-gradient(135deg, #ffffff 0%, #fafbfc 100%); position: relative;">
                                <!-- Línea decorativa superior -->
                                <div style="width: 60px; height: 3px; background: linear-gradient(90deg, #8b5cf6 0%, #a78bfa 100%); margin: 0 auto 32px auto; border-radius: 2px;"></div>
                                
                                <!-- Logo con efecto elegante -->
                                <div style="margin-bottom: 24px; position: relative; display: inline-block;">
                                    <div style="background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%); border-radius: 16px; padding: 16px; display: inline-block; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);">
                                        <img src="https://i.ibb.co/gLZkzkVs/Copilot-20251009-015607-removebg-preview.png" alt="DislexIA" style="width: 56px; height: 56px; display: block;">
                                    </div>
                                </div>
                                
                                <!-- Título elegante -->
                                <h1 style="color: #1a1a1a; margin: 0; font-size: 32px; font-weight: 700; letter-spacing: -1px; line-height: 1.2;">
                                    DislexIA
                                </h1>
                                <p style="color: #6b7280; margin: 8px 0 0 0; font-size: 14px; font-weight: 500; letter-spacing: 0.5px; text-transform: uppercase;">
                                    Tu neuropsicólogo amigo
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Contenido principal elegante -->
                        <tr>
                            <td style="padding: 50px 50px 60px 50px;">
                                <!-- Título de sección -->
                                <div style="text-align: center; margin-bottom: 40px;">
                                    <h2 style="color: #1a1a1a; font-size: 26px; margin: 0 0 12px 0; font-weight: 600; letter-spacing: -0.5px;">
                                        🗓️ Nueva Cita Agendada
                                    </h2>
                                    <div style="width: 40px; height: 2px; background: linear-gradient(90deg, #8b5cf6 0%, #a78bfa 100%); margin: 0 auto; border-radius: 2px;"></div>
                                </div>
                                
                                <!-- Saludo personalizado -->
                                <p style="color: #374151; font-size: 16px; line-height: 1.7; margin: 0 0 32px 0; text-align: center;">
                                    Hola <strong style="color: #1a1a1a;">{contexto['doctor_nombre']}</strong>,
                                </p>
                                
                                <p style="color: #6b7280; font-size: 15px; line-height: 1.8; margin: 0 0 36px 0;">
                                    Se ha agendado una nueva cita en tu calendario. A continuación encontrarás los detalles completos de la sesión programada.
                                </p>
                                
                                <!-- Detalles de la cita con estilo sofisticado -->
                                <div style="background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%); padding: 32px; border-radius: 16px; border-left: 4px solid #8b5cf6; margin-bottom: 36px; box-shadow: 0 4px 12px rgba(139, 92, 246, 0.08);">
                                    <h3 style="color: #5b21b6; font-size: 18px; margin: 0 0 24px 0; font-weight: 600; letter-spacing: -0.3px; text-align: center;">
                                        📋 Detalles de la Cita
                                    </h3>
                                    
                                    <div style="background: white; padding: 16px; border-radius: 10px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);">
                                        <p style="color: #8b5cf6; font-size: 13px; margin: 0 0 6px 0; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                                            👤 Paciente
                                        </p>
                                        <p style="color: #1a1a1a; font-size: 16px; margin: 0; font-weight: 500;">
                                            {contexto['paciente_nombre']}
                                        </p>
                                    </div>
                                    
                                    <div style="background: white; padding: 16px; border-radius: 10px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);">
                                        <p style="color: #8b5cf6; font-size: 13px; margin: 0 0 6px 0; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                                            📅 Fecha
                                        </p>
                                        <p style="color: #1a1a1a; font-size: 16px; margin: 0; font-weight: 500;">
                                            {contexto['fecha']}
                                        </p>
                                    </div>
                                    
                                    <div style="background: white; padding: 16px; border-radius: 10px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);">
                                        <p style="color: #8b5cf6; font-size: 13px; margin: 0 0 6px 0; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                                            ⏰ Hora
                                        </p>
                                        <p style="color: #1a1a1a; font-size: 16px; margin: 0; font-weight: 500;">
                                            {contexto['hora']}
                                        </p>
                                    </div>
                                    
                                    <div style="background: white; padding: 16px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);">
                                        <p style="color: #8b5cf6; font-size: 13px; margin: 0 0 6px 0; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                                            📝 Notas
                                        </p>
                                        <p style="color: #6b7280; font-size: 15px; margin: 0; line-height: 1.6;">
                                            {contexto['notas']}
                                        </p>
                                    </div>
                                </div>
                                
                                <!-- Recordatorio con estilo -->
                                <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); padding: 20px; border-radius: 12px; border-left: 4px solid #f59e0b; margin-bottom: 32px;">
                                    <p style="color: #92400e; font-size: 14px; margin: 0 0 8px 0; font-weight: 600; letter-spacing: -0.2px;">
                                        💡 Recordatorio
                                    </p>
                                    <p style="color: #b45309; font-size: 14px; margin: 0; line-height: 1.7;">
                                        Recuerda preparar el material necesario para la sesión y revisar el historial del paciente.
                                    </p>
                                </div>
                                
                                <!-- Separador decorativo -->
                                <div style="height: 1px; background: linear-gradient(90deg, transparent 0%, #e5e7eb 50%, transparent 100%); margin: 40px 0;"></div>
                                
                                <p style="color: #6b7280; font-size: 14px; margin: 0; text-align: center; line-height: 1.7;">
                                    Si tienes alguna pregunta o necesitas realizar cambios, accede a tu panel administrativo.
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Footer sofisticado -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #fafbfc 0%, #f8f9fa 100%); padding: 40px 50px; text-align: center; border-top: 1px solid #e5e7eb;">
                                <p style="color: #6b7280; font-size: 15px; margin: 0 0 20px 0; font-weight: 500; letter-spacing: -0.2px;">
                                    Cordialmente,
                                </p>
                                <p style="color: #1a1a1a; font-size: 16px; margin: 0 0 8px 0; font-weight: 600; letter-spacing: -0.3px;">
                                    Equipo DislexIA
                                </p>
                                
                                <!-- Línea decorativa inferior -->
                                <div style="width: 40px; height: 2px; background: linear-gradient(90deg, #8b5cf6 0%, #a78bfa 100%); margin: 24px auto 20px auto; border-radius: 2px;"></div>
                                
                                <p style="color: #9ca3af; font-size: 12px; margin: 0; letter-spacing: 0.3px;">
                                    © 2025 DislexIA · Todos los derechos reservados
                                </p>
                            </td>
                        </tr>
                    </table>
                    
                    <!-- Nota legal elegante -->
                    <p style="color: #adb5bd; font-size: 12px; text-align: center; margin: 32px 0 0 0; max-width: 560px; line-height: 1.6; letter-spacing: 0.2px;">
                        Este es un mensaje automatizado. Por favor, no responda a este correo electrónico.
                    </p>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    mensaje_texto = strip_tags(mensaje_html)
    
    try:
        send_mail(
            asunto,
            mensaje_texto,
            settings.DEFAULT_FROM_EMAIL,
            [doctor.email],
            html_message=mensaje_html,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error al enviar correo al doctor: {e}")
        return False


def enviar_correo_cita_padres(email_padres, cita, doctor):
    """
    Envía un correo a los padres con la confirmación de la cita
    """
    asunto = f'Confirmación de cita - {cita.nombre_paciente}'
    
    contexto = {
        'paciente_nombre': cita.nombre_paciente,
        'doctor_nombre': doctor.nombre_completo,
        'fecha': cita.fecha.strftime('%d/%m/%Y'),
        'hora': cita.hora.strftime('%H:%M'),
        'notas': cita.notas or 'Sin notas adicionales',
    }
    
    mensaje_html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Confirmación de Cita - DislexIA</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 80px 20px;">
            <tr>
                <td align="center">
                    <!-- Contenedor principal con sombra elegante -->
                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; background: linear-gradient(to bottom, #ffffff 0%, #fefefe 100%); border-radius: 20px; overflow: hidden; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08), 0 0 1px rgba(0, 0, 0, 0.05);">
                        
                        <!-- Header sofisticado -->
                        <tr>
                            <td style="padding: 60px 50px 40px 50px; text-align: center; background: linear-gradient(135deg, #ffffff 0%, #fafbfc 100%); position: relative;">
                                <!-- Línea decorativa superior -->
                                <div style="width: 60px; height: 3px; background: linear-gradient(90deg, #8b5cf6 0%, #a78bfa 100%); margin: 0 auto 32px auto; border-radius: 2px;"></div>
                                
                                <!-- Logo con efecto elegante -->
                                <div style="margin-bottom: 24px; position: relative; display: inline-block;">
                                    <div style="background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%); border-radius: 16px; padding: 16px; display: inline-block; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);">
                                        <img src="https://i.ibb.co/gLZkzkVs/Copilot-20251009-015607-removebg-preview.png" alt="DislexIA" style="width: 56px; height: 56px; display: block;">
                                    </div>
                                </div>
                                
                                <!-- Título elegante -->
                                <h1 style="color: #1a1a1a; margin: 0; font-size: 32px; font-weight: 700; letter-spacing: -1px; line-height: 1.2;">
                                    DislexIA
                                </h1>
                                <p style="color: #6b7280; margin: 8px 0 0 0; font-size: 14px; font-weight: 500; letter-spacing: 0.5px; text-transform: uppercase;">
                                    Tu neuropsicólogo amigo
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Contenido principal elegante -->
                        <tr>
                            <td style="padding: 50px 50px 60px 50px;">
                                <!-- Título de sección -->
                                <div style="text-align: center; margin-bottom: 40px;">
                                    <h2 style="color: #1a1a1a; font-size: 26px; margin: 0 0 12px 0; font-weight: 600; letter-spacing: -0.5px;">
                                        ✅ Cita Confirmada
                                    </h2>
                                    <div style="width: 40px; height: 2px; background: linear-gradient(90deg, #8b5cf6 0%, #a78bfa 100%); margin: 0 auto; border-radius: 2px;"></div>
                                </div>
                                
                                <!-- Saludo personalizado -->
                                <p style="color: #374151; font-size: 16px; line-height: 1.7; margin: 0 0 32px 0; text-align: center;">
                                    Estimados padres de <strong style="color: #1a1a1a;">{contexto['paciente_nombre']}</strong>,
                                </p>
                                
                                <p style="color: #6b7280; font-size: 15px; line-height: 1.8; margin: 0 0 36px 0;">
                                    Su cita ha sido agendada exitosamente en nuestro sistema. A continuación encontrará todos los detalles importantes de la consulta programada.
                                </p>
                                
                                <!-- Detalles de la cita con estilo sofisticado -->
                                <div style="background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%); padding: 32px; border-radius: 16px; border: 2px solid #8b5cf6; margin-bottom: 36px; box-shadow: 0 4px 12px rgba(139, 92, 246, 0.08);">
                                    <h3 style="color: #5b21b6; font-size: 18px; margin: 0 0 24px 0; font-weight: 600; letter-spacing: -0.3px; text-align: center;">
                                        📋 Información de la Cita
                                    </h3>
                                    
                                    <div style="background: white; padding: 16px; border-radius: 10px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);">
                                        <p style="color: #8b5cf6; font-size: 13px; margin: 0 0 6px 0; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                                            👨‍⚕️ Doctor
                                        </p>
                                        <p style="color: #1a1a1a; font-size: 16px; margin: 0; font-weight: 500;">
                                            {contexto['doctor_nombre']}
                                        </p>
                                    </div>
                                    
                                    <div style="background: white; padding: 16px; border-radius: 10px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);">
                                        <p style="color: #8b5cf6; font-size: 13px; margin: 0 0 6px 0; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                                            👦 Paciente
                                        </p>
                                        <p style="color: #1a1a1a; font-size: 16px; margin: 0; font-weight: 500;">
                                            {contexto['paciente_nombre']}
                                        </p>
                                    </div>
                                    
                                    <div style="background: white; padding: 16px; border-radius: 10px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);">
                                        <p style="color: #8b5cf6; font-size: 13px; margin: 0 0 6px 0; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                                            📅 Fecha
                                        </p>
                                        <p style="color: #1a1a1a; font-size: 16px; margin: 0; font-weight: 500;">
                                            {contexto['fecha']}
                                        </p>
                                    </div>
                                    
                                    <div style="background: white; padding: 16px; border-radius: 10px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);">
                                        <p style="color: #8b5cf6; font-size: 13px; margin: 0 0 6px 0; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                                            ⏰ Hora
                                        </p>
                                        <p style="color: #1a1a1a; font-size: 16px; margin: 0; font-weight: 500;">
                                            {contexto['hora']}
                                        </p>
                                    </div>
                                    
                                    <div style="background: white; padding: 16px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);">
                                        <p style="color: #8b5cf6; font-size: 13px; margin: 0 0 6px 0; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                                            📝 Notas
                                        </p>
                                        <p style="color: #6b7280; font-size: 15px; margin: 0; line-height: 1.6;">
                                            {contexto['notas']}
                                        </p>
                                    </div>
                                </div>
                                
                                <!-- Recordatorio importante con estilo -->
                                <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); padding: 20px; border-radius: 12px; border-left: 4px solid #f59e0b; margin-bottom: 32px;">
                                    <p style="color: #92400e; font-size: 14px; margin: 0 0 8px 0; font-weight: 600; letter-spacing: -0.2px;">
                                        ⏰ Recordatorio Importante
                                    </p>
                                    <p style="color: #b45309; font-size: 14px; margin: 0; line-height: 1.7;">
                                        Por favor, llegue 10 minutos antes de la hora programada. Recibirá un recordatorio automático 30 minutos antes de su cita.
                                    </p>
                                </div>
                                
                                <!-- Información adicional -->
                                <div style="background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); padding: 20px; border-radius: 12px; border-left: 4px solid #3b82f6; margin-bottom: 32px;">
                                    <p style="color: #1e40af; font-size: 14px; margin: 0 0 8px 0; font-weight: 600; letter-spacing: -0.2px;">
                                        📞 Contacto
                                    </p>
                                    <p style="color: #1e3a8a; font-size: 14px; margin: 0; line-height: 1.7;">
                                        Si necesita reprogramar o cancelar la cita, por favor contáctenos con anticipación. Estamos disponibles para ayudarle.
                                    </p>
                                </div>
                                
                                <!-- Separador decorativo -->
                                <div style="height: 1px; background: linear-gradient(90deg, transparent 0%, #e5e7eb 50%, transparent 100%); margin: 40px 0;"></div>
                                
                                <p style="color: #6b7280; font-size: 14px; margin: 0; text-align: center; line-height: 1.7;">
                                    Agradecemos su confianza en nuestro equipo profesional.
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Footer sofisticado -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #fafbfc 0%, #f8f9fa 100%); padding: 40px 50px; text-align: center; border-top: 1px solid #e5e7eb;">
                                <p style="color: #6b7280; font-size: 15px; margin: 0 0 20px 0; font-weight: 500; letter-spacing: -0.2px;">
                                    Cordialmente,
                                </p>
                                <p style="color: #1a1a1a; font-size: 16px; margin: 0 0 8px 0; font-weight: 600; letter-spacing: -0.3px;">
                                    Equipo DislexIA
                                </p>
                                
                                <!-- Línea decorativa inferior -->
                                <div style="width: 40px; height: 2px; background: linear-gradient(90deg, #8b5cf6 0%, #a78bfa 100%); margin: 24px auto 20px auto; border-radius: 2px;"></div>
                                
                                <p style="color: #9ca3af; font-size: 12px; margin: 0; letter-spacing: 0.3px;">
                                    © 2025 DislexIA · Todos los derechos reservados
                                </p>
                            </td>
                        </tr>
                    </table>
                    
                    <!-- Nota legal elegante -->
                    <p style="color: #adb5bd; font-size: 12px; text-align: center; margin: 32px 0 0 0; max-width: 560px; line-height: 1.6; letter-spacing: 0.2px;">
                        Este es un mensaje automatizado. Por favor, no responda a este correo electrónico.
                    </p>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    mensaje_texto = strip_tags(mensaje_html)
    
    try:
        send_mail(
            asunto,
            mensaje_texto,
            settings.DEFAULT_FROM_EMAIL,
            [email_padres],
            html_message=mensaje_html,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error al enviar correo a los padres: {e}")
        return False
