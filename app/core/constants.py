"""
Constantes específicas del módulo core
Este archivo contiene constantes relacionadas con niños, profesionales y reportes
"""

# Opciones de género para niños
GENERO_CHOICES = [
    ('Masculino', 'Masculino'),
    ('Femenino', 'Femenino'),
    ('Otro', 'Otro'),
]

# Opciones de roles para profesionales
ROL_CHOICES = [
    ('administrador', 'Administrador'),
    ('profesional', 'Profesional'),
    ('docente', 'Docente'),
]

# Opciones de clasificación de riesgo para reportes IA
CLASIFICACION_RIESGO_CHOICES = [
    ('Bajo', 'Bajo'),
    ('Medio', 'Medio'),
    ('Alto', 'Alto'),
]

# Validadores para campos numéricos
EDAD_MIN = 6
EDAD_MAX = 12
INDICE_RIESGO_MIN = 0.00
INDICE_RIESGO_MAX = 100.00
CONFIANZA_MIN = 0
CONFIANZA_MAX = 100

# Valores por defecto
DEFAULTS = {
    'profesional_rol': 'profesional',
    'nino_activo': True,
    'profesional_activo': True,
    'requiere_seguimiento': False,
}
