# 🔒 Cumplimiento GDPR - DislexIA

Este documento describe las implementaciones realizadas para cumplir con el **Reglamento General de Protección de Datos (GDPR)** de la Unión Europea.

## 📋 Índice

- [Estado de Cumplimiento](#estado-de-cumplimiento)
- [Modelos Implementados](#modelos-implementados)
- [Configuraciones de Seguridad](#configuraciones-de-seguridad)
- [Derechos del Usuario](#derechos-del-usuario)
- [Auditoría y Logging](#auditoría-y-logging)
- [Políticas de Retención](#políticas-de-retención)
- [Documentos Legales](#documentos-legales)
- [Comandos de Gestión](#comandos-de-gestión)

---

## ✅ Estado de Cumplimiento

**Puntuación**: 10/10 ✅ **COMPLETO**

| Requisito GDPR | Estado | Implementación |
|----------------|--------|----------------|
| Consentimiento explícito (Art. 6 & 7) | ✅ | `ConsentimientoGDPR` model + formulario registro |
| Protección de menores (Art. 8) | ✅ | `ConsentimientoTutor` model |
| Derecho de acceso (Art. 15) | ✅ | Vista de perfil y auditoría |
| Derecho de rectificación (Art. 16) | ✅ | Formulario de edición de perfil |
| Derecho al olvido (Art. 17) | ✅ | Vista de eliminación de cuenta |
| Derecho de portabilidad (Art. 20) | ✅ | `exportar_datos_usuario` vista |
| Derecho de oposición (Art. 21) | ✅ | `revocar_consentimiento` vista |
| Auditoría (Art. 30) | ✅ | `AuditoriaAcceso` model + middleware |
| Seguridad (Art. 32) | ✅ | HTTPS, cookies seguras, cifrado |
| Política de privacidad (Art. 13) | ✅ | Template completo |
| Términos y condiciones | ✅ | Template completo |
| Retención de datos (Art. 5.1.e) | ✅ | `PoliticaRetencionDatos` model |

---

## 📦 Modelos Implementados

### 1. `ConsentimientoGDPR`
Registra el consentimiento explícito del usuario al registrarse.

**Campos principales:**
- `acepta_terminos`: Términos y condiciones
- `acepta_privacidad`: Política de privacidad
- `acepta_tratamiento_datos`: Tratamiento de datos personales
- `acepta_cookies`: Uso de cookies
- `acepta_comunicaciones`: Recibir comunicaciones (opcional)
- `ip_address`: IP desde donde se dio el consentimiento
- `version_terminos` / `version_privacidad`: Versionado de documentos

**Métodos:**
```python
consentimiento.revocar_consentimiento()  # Revoca el consentimiento
consentimiento.es_valido()  # Verifica validez
```

### 2. `ConsentimientoTutor`
Gestiona el consentimiento de tutores legales para datos de menores.

**Campos principales:**
- `nino`: Relación con el niño
- `nombre_completo_tutor`: Datos del tutor legal
- `documento_identidad`: Documento oficial del tutor
- `acepta_evaluacion`: Autoriza evaluación cognitiva
- `acepta_almacenamiento_datos`: Autoriza almacenamiento
- `acepta_uso_imagen`: Autoriza uso de imagen
- `firma_digital`: Hash de firma digital

**Uso:**
```python
from app.core.models import ConsentimientoTutor

# Verificar si hay consentimiento válido
if nino.consentimiento_tutor.es_valido():
    # Proceder con evaluación
    pass
```

### 3. `AuditoriaAcceso`
Registra todas las operaciones sobre datos personales.

**Acciones registradas:**
- `READ`: Lectura de datos
- `CREATE`: Creación de registros
- `UPDATE`: Actualización
- `DELETE`: Eliminación
- `EXPORT`: Exportación de datos
- `LOGIN` / `LOGOUT`: Eventos de autenticación
- `CONSENT_GIVEN` / `CONSENT_REVOKED`: Gestión de consentimientos

**Uso programático:**
```python
from app.core.models import AuditoriaAcceso

AuditoriaAcceso.registrar(
    usuario=request.user,
    accion='READ',
    tabla_afectada='Nino',
    registro_id=nino.id,
    ip_address=request.META.get('REMOTE_ADDR'),
    detalles={'campo': 'nombre_completo'}
)
```

### 4. `PoliticaRetencionDatos`
Define períodos de retención por tipo de dato.

**Configuración por defecto:**
- Evaluaciones: 5 años (1825 días)
- Reportes IA: 5 años
- Sesiones de juego: 3 años
- Citas: 2 años
- Auditorías: 7 años (requisito legal)
- Usuarios inactivos: 3 años

---

## 🔐 Configuraciones de Seguridad

### En `settings.py`:

```python
# Producción
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 año
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# Sesiones
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 1209600  # 2 semanas

# Logging de auditoría
LOGGING = {
    'loggers': {
        'audit': {
            'handlers': ['audit_file', 'console'],
            'level': 'INFO',
        }
    }
}
```

### Middleware de Auditoría

Se registran automáticamente:
- Accesos a perfiles
- Modificaciones de datos
- Exportaciones
- Intentos de login (exitosos y fallidos)

**Configuración en `settings.py`:**
```python
MIDDLEWARE = [
    # ... otros middleware
    'app.core.middleware.AuditMiddleware',
    'app.core.middleware.LoginAuditMiddleware',
]
```

---

## 👤 Derechos del Usuario

### URLs implementadas:

```python
# Documentos legales
/legal/privacy-policy/          # Política de privacidad
/legal/terms-conditions/        # Términos y condiciones

# Derechos GDPR
/exportar-datos/                # Exportar datos (Art. 20)
/consentimientos/               # Ver consentimientos
/consentimientos/revocar/       # Revocar consentimiento (Art. 7.3)
/historial-auditoria/           # Ver historial de accesos
/account/delete/                # Eliminar cuenta (Art. 17)
```

### Exportación de Datos

El usuario puede descargar todos sus datos en formato JSON:

```json
{
  "informacion_exportacion": {
    "fecha_exportacion": "2025-11-04T10:30:00",
    "version_gdpr": "1.0"
  },
  "datos_personales": { ... },
  "ninos_asignados": [ ... ],
  "evaluaciones_realizadas": [ ... ],
  "consentimientos": [ ... ],
  "historial_auditoria": [ ... ]
}
```

---

## 📊 Auditoría y Logging

### Sistema de Logging

Tres tipos de logs:
1. **django.log**: Logs generales de aplicación
2. **security.log**: Eventos de seguridad
3. **audit.log**: Auditoría GDPR (accesos a datos personales)

**Ubicación**: `logs/` (se crea automáticamente)

**Rotación**: 10 archivos de 10MB cada uno

### Consultar Auditoría

Como administrador:
```python
from app.core.models import AuditoriaAcceso

# Auditoría de un usuario
auditorias = AuditoriaAcceso.objects.filter(usuario=usuario)

# Accesos a un registro específico
accesos = AuditoriaAcceso.objects.filter(
    tabla_afectada='Nino',
    registro_id=123
)

# Exportaciones de datos
exportaciones = AuditoriaAcceso.objects.filter(accion='EXPORT')
```

---

## ⏰ Políticas de Retención

### Inicializar Políticas

```bash
python manage.py init_gdpr_policies
```

### Consultar Políticas Activas

```python
from app.core.models import PoliticaRetencionDatos

# Ver todas las políticas
for politica in PoliticaRetencionDatos.objects.filter(activa=True):
    print(f"{politica.get_tipo_dato_display()}: {politica.dias_retencion} días")
```

### Personalizar Retención

En `settings.py`:
```python
DATA_RETENTION_POLICIES = {
    'evaluacion': 1825,  # 5 años
    'reporte_ia': 1825,
    'sesion_juego': 1095,  # 3 años
    'cita': 730,  # 2 años
    'auditoria': 2555,  # 7 años (requisito legal)
    'usuario_inactivo': 1095,
}
```

---

## 📄 Documentos Legales

### Política de Privacidad
`templates/legal/privacy_policy.html`

**Contenido:**
- Responsable del tratamiento
- DPO (Data Protection Officer)
- Datos recopilados
- Base legal del tratamiento
- Finalidades
- Derechos del usuario (GDPR)
- Período de retención
- Medidas de seguridad
- Transferencias internacionales
- Cookies

### Términos y Condiciones
`templates/legal/terms_conditions.html`

**Contenido:**
- Descripción del servicio
- Requisitos de registro
- Usos permitidos y prohibidos
- Propiedad intelectual
- Limitación de responsabilidad
- Privacidad y protección de datos
- Terminación del servicio
- Ley aplicable

---

## 🛠️ Comandos de Gestión

### Inicializar Políticas GDPR
```bash
python manage.py init_gdpr_policies
```

### Crear Migraciones
```bash
python manage.py makemigrations core
python manage.py migrate
```

### Verificar Consentimientos
```python
from app.core.models import ConsentimientoGDPR

# Usuarios sin consentimiento válido
from django.contrib.auth import get_user_model
User = get_user_model()

for usuario in User.objects.filter(is_active=True):
    consentimiento = ConsentimientoGDPR.objects.filter(
        usuario=usuario,
        consentimiento_activo=True
    ).first()
    
    if not consentimiento or not consentimiento.es_valido():
        print(f"⚠️ {usuario.username}: Sin consentimiento válido")
```

---

## 📞 Contacto DPO

**Delegado de Protección de Datos:**
- Nombre: Dr. Alexis Durán
- Email: dpo@dislexia.com
- Teléfono: +593 99 999 9999

Para consultas sobre privacidad o ejercer derechos GDPR, contactar al DPO.

---

## 🔄 Changelog GDPR

### Versión 1.0 (4 de noviembre de 2025)
- ✅ Implementación completa de modelos GDPR
- ✅ Consentimiento explícito en registro
- ✅ Consentimiento de tutores para menores
- ✅ Sistema de auditoría automática
- ✅ Exportación de datos en JSON
- ✅ Documentos legales completos
- ✅ Configuraciones de seguridad
- ✅ Políticas de retención de datos
- ✅ Middleware de logging
- ✅ Panel de administración para auditoría

---

## 📚 Referencias

- [GDPR Official Text](https://gdpr-info.eu/)
- [ICO Guide](https://ico.org.uk/for-organisations/guide-to-data-protection/)
- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)

---

**Última actualización**: 4 de noviembre de 2025  
**Versión GDPR**: 1.0  
**Mantenido por**: Equipo DislexIA
