"""
Constantes globales de la aplicación DislexIA
Este archivo contiene constantes que pueden ser reutilizadas en toda la aplicación
"""

# Constantes de dificultad (común para diferentes módulos)
DIFICULTAD_CHOICES = [
    ('facil', 'Fácil'),
    ('medio', 'Medio'),
    ('dificil', 'Difícil'),
]

# Constantes de estado (común para diferentes módulos)
ESTADO_CHOICES = [
    ('en_proceso', 'En Proceso'),
    ('completada', 'Completada'),
    ('interrumpida', 'Interrumpida'),
]

# Constantes de colores para temas (común para diferentes módulos)
COLOR_CHOICES = [
    ('purple', 'Morado'),
    ('blue', 'Azul'),
    ('green', 'Verde'),
    ('orange', 'Naranja'),
    ('red', 'Rojo'),
    ('pink', 'Rosa'),
    ('indigo', 'Índigo'),
    ('teal', 'Verde Azulado'),
]

# Mapeo de colores para gradientes CSS
COLOR_GRADIENTE_MAP = {
    'purple': {
        'inicio': 'purple-500',
        'fin': 'purple-600'
    },
    'blue': {
        'inicio': 'blue-500',
        'fin': 'blue-600'
    },
    'green': {
        'inicio': 'green-500',
        'fin': 'green-600'
    },
    'orange': {
        'inicio': 'orange-500',
        'fin': 'orange-600'
    },
    'red': {
        'inicio': 'red-500',
        'fin': 'red-600'
    },
    'pink': {
        'inicio': 'pink-500',
        'fin': 'pink-600'
    },
    'indigo': {
        'inicio': 'indigo-500',
        'fin': 'indigo-600'
    },
    'teal': {
        'inicio': 'teal-500',
        'fin': 'teal-600'
    },
}
