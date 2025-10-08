"""
Constantes específicas del módulo de juegos
Este archivo contiene constantes relacionadas con los juegos cognitivos
"""

# Categorías principales de juegos (globales y flexibles)
CATEGORIAS_JUEGO_CHOICES = [
    ('reconocimiento_visual', 'Reconocimiento Visual'),
    ('comprension_auditiva', 'Comprensión Auditiva'),
    ('escritura_ortografia', 'Escritura y Ortografía'),
    ('lectura_comprension', 'Lectura y Comprensión'),
    ('memoria_concentracion', 'Memoria y Concentración'),
    ('logica_razonamiento', 'Lógica y Razonamiento'),
    ('coordinacion_motora', 'Coordinación Motora'),
]

# Valores por defecto para juegos
JUEGO_DEFAULTS = {
    'categoria': 'reconocimiento_visual',
    'dificultad': 'medio',
    'color_tema': 'purple',
    'duracion_estimada_minutos': 10,
    'puntuacion_promedio': 4.5,
    'activo': True,
    'orden_visualizacion': 0,
    'total_jugadas': 0,
    'total_completados': 0,
}

# Validadores para campos numéricos
PUNTUACION_MIN = 1.0
PUNTUACION_MAX = 5.0
PRECISION_MIN = 0.00
PRECISION_MAX = 100.00
