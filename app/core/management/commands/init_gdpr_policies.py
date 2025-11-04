"""
Comando para inicializar políticas de retención de datos GDPR
Uso: python manage.py init_gdpr_policies
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from app.core.models import PoliticaRetencionDatos


class Command(BaseCommand):
    help = 'Inicializa las políticas de retención de datos GDPR'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Iniciando configuración de políticas GDPR...'))
        
        # Obtener las políticas desde settings
        politicas_config = getattr(settings, 'DATA_RETENTION_POLICIES', {})
        
        if not politicas_config:
            self.stdout.write(self.style.WARNING('No se encontraron políticas en settings.DATA_RETENTION_POLICIES'))
            self.stdout.write(self.style.WARNING('Creando políticas por defecto...'))
            politicas_config = {
                'evaluacion': 1825,  # 5 años
                'reporte_ia': 1825,  # 5 años
                'sesion_juego': 1095,  # 3 años
                'cita': 730,  # 2 años
                'auditoria': 2555,  # 7 años
                'usuario_inactivo': 1095,  # 3 años
            }
        
        creadas = 0
        actualizadas = 0
        
        for tipo_dato, dias_retencion in politicas_config.items():
            try:
                # Intentar obtener la política existente
                politica, created = PoliticaRetencionDatos.objects.get_or_create(
                    tipo_dato=tipo_dato,
                    defaults={
                        'dias_retencion': dias_retencion,
                        'accion_al_vencer': 'anonimizar',
                        'activa': True
                    }
                )
                
                if created:
                    creadas += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Creada: {politica.get_tipo_dato_display()} - {dias_retencion} días'
                        )
                    )
                else:
                    # Actualizar días de retención si cambió
                    if politica.dias_retencion != dias_retencion:
                        politica.dias_retencion = dias_retencion
                        politica.save()
                        actualizadas += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f'🔄 Actualizada: {politica.get_tipo_dato_display()} - '
                                f'{dias_retencion} días'
                            )
                        )
                    else:
                        self.stdout.write(
                            f'⏭️  Ya existe: {politica.get_tipo_dato_display()}'
                        )
            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error con {tipo_dato}: {str(e)}')
                )
        
        self.stdout.write(self.style.SUCCESS(f'\n📊 Resumen:'))
        self.stdout.write(self.style.SUCCESS(f'   • Políticas creadas: {creadas}'))
        self.stdout.write(self.style.SUCCESS(f'   • Políticas actualizadas: {actualizadas}'))
        self.stdout.write(self.style.SUCCESS(f'   • Total en sistema: {PoliticaRetencionDatos.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('\n✅ Configuración GDPR completada'))
