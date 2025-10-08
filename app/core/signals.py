from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User
from datetime import date
import os

@receiver(post_migrate)
def crear_superusuario_inicial(sender, **kwargs):
    """
    Crea automáticamente un superusuario después de las migraciones
    Solo se ejecuta para la app 'core' y solo si no existe ningún superusuario
    """
    # Solo ejecutar para la app core (primera vez)
    if sender.name != 'app.core':
        return
    
    # Verificar si ya existe un superusuario
    if User.objects.filter(is_superuser=True).exists():
        print("👤 Ya existe un superusuario, omitiendo creación")
        return
    
    # Obtener credenciales del archivo .env o usar valores por defecto
    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@dislexia.com')
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    try:
        # Crear el superusuario
        superuser = User.objects.create_superuser(
            username=admin_username,
            email=admin_email,
            password=admin_password,
            first_name='Administrador',
            last_name='DislexIA'
        )
        
        print(f"✅ Superusuario creado exitosamente:")
        print(f"👤 Usuario: {admin_username}")
        print(f"📧 Email: {admin_email}")
        print(f"🔑 Contraseña: {admin_password}")
        print(f"🆔 ID: {superuser.id}")
        
    except Exception as e:
        print(f"❌ Error creando superusuario: {e}")
        print("🔧 Verifica las variables de entorno ADMIN_USERNAME, ADMIN_EMAIL y ADMIN_PASSWORD")

@receiver(post_migrate)
def crear_nino_ejemplo(sender, **kwargs):
    """
    Crea un niño de ejemplo para pruebas después de las migraciones
    Solo se ejecuta para la app 'core' y solo si no existe ningún niño
    """
    # Solo ejecutar para la app core
    if sender.name != 'app.core':
        return
    
    # Importar el modelo Nino aquí para evitar problemas de importación circular
    from .models import Nino
    
    # Verificar si ya existe al menos un niño
    if Nino.objects.exists():
        print("👶 Ya existen niños registrados, omitiendo creación de niño de ejemplo")
        return
    
    try:
        # Crear niño de ejemplo
        nino_ejemplo = Nino.objects.create(
            nombres="Javier Ramón",
            apellidos="Haro Valdez",
            fecha_nacimiento=date(2016, 5, 15),  # 9 años aproximadamente
            edad=9,
            idioma_nativo="Español",
            activo=True
        )
        
        print(f"✅ Niño de ejemplo creado exitosamente:")
        print(f"👶 Nombre: {nino_ejemplo.nombre_completo}")
        print(f"🎂 Edad: {nino_ejemplo.edad} años")
        print(f"🗣️ Idioma: {nino_ejemplo.idioma_nativo}")
        print(f"🆔 ID: {nino_ejemplo.id}")
        
    except Exception as e:
        print(f"❌ Error creando niño de ejemplo: {e}")
        print("🔧 Verifica que las migraciones se hayan ejecutado correctamente")
