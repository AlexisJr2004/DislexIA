from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps

@receiver(post_migrate)
def crear_juegos_iniciales(sender, **kwargs):
    """
    Crea automáticamente los juegos iniciales después de las migraciones
    Solo se ejecuta para la app 'games'
    """
    # Solo ejecutar para la app games
    if sender.name != 'app.games':
        return
    
    # Importar el modelo después de que las migraciones se hayan ejecutado
    try:
        Juego = apps.get_model('games', 'Juego')
    except LookupError:
        # El modelo no existe aún, salir silenciosamente
        return
    
    juegos_iniciales = [
        {
            'nombre': 'Selecciona la Palabra Correcta',
            'descripcion': 'Observa la imagen y selecciona la palabra que la describe correctamente entre varias opciones.',
            'categoria': 'reconocimiento_visual',
            'dificultad': 'facil',
            'color_tema': 'green',
            'duracion_estimada_minutos': 8,
            'puntuacion_promedio': 4.6,
            'orden_visualizacion': 1,
        },
        {
            'nombre': 'Escribe el Nombre del Objeto',
            'descripcion': 'Ve la imagen y escribe correctamente el nombre del objeto que observas.',
            'categoria': 'escritura_ortografia',
            'dificultad': 'medio',
            'color_tema': 'blue',
            'duracion_estimada_minutos': 12,
            'puntuacion_promedio': 4.3,
            'orden_visualizacion': 2,
        },
        {
            'nombre': 'Completa la Palabra',
            'descripcion': 'Selecciona la letra correcta para completar la palabra mostrada.',
            'categoria': 'escritura_ortografia',
            'dificultad': 'facil',
            'color_tema': 'purple',
            'duracion_estimada_minutos': 10,
            'puntuacion_promedio': 4.5,
            'orden_visualizacion': 3,
        },
        {
            'nombre': 'Palabra que Escuches',
            'descripcion': 'Escucha atentamente y selecciona la palabra correcta entre las opciones disponibles.',
            'categoria': 'comprension_auditiva',
            'dificultad': 'medio',
            'color_tema': 'orange',
            'duracion_estimada_minutos': 15,
            'puntuacion_promedio': 4.4,
            'orden_visualizacion': 4,
        },
        {
            'nombre': 'Encuentra el Error',
            'descripcion': 'Identifica y marca el error oculto en las palabras presentadas.',
            'categoria': 'lectura_comprension',
            'dificultad': 'dificil',
            'color_tema': 'red',
            'duracion_estimada_minutos': 18,
            'puntuacion_promedio': 4.2,
            'orden_visualizacion': 5,
        },
        {
            'nombre': 'Buscar Palabras',
            'descripcion': 'Encuentra palabras ocultas en una sopa de letras. Perfecto para mejorar la concentración y el reconocimiento visual.',
            'categoria': 'memoria_concentracion',
            'dificultad': 'medio',
            'color_tema': 'teal',
            'duracion_estimada_minutos': 15,
            'puntuacion_promedio': 4.6,
            'orden_visualizacion': 6,
        },
        {
            'nombre': 'Ordenar Palabras',
            'descripcion': 'Organiza las palabras en el orden correcto para formar oraciones coherentes. Desarrolla gramática y sintaxis.',
            'categoria': 'lectura_comprension',
            'dificultad': 'dificil',
            'color_tema': 'orange',
            'duracion_estimada_minutos': 20,
            'puntuacion_promedio': 4.9,
            'orden_visualizacion': 7,
        },
        {
            'nombre': 'Quiz Interactivo',
            'descripcion': 'Pon a prueba tus conocimientos con preguntas de opción múltiple. Ideal para practicar comprensión lectora y memoria.',
            'categoria': 'lectura_comprension',
            'dificultad': 'facil',
            'color_tema': 'indigo',
            'duracion_estimada_minutos': 10,
            'puntuacion_promedio': 4.8,
            'orden_visualizacion': 8,
        },
    ]
    
    created_count = 0
    updated_count = 0
    
    for juego_data in juegos_iniciales:
        juego, created = Juego.objects.get_or_create(
            nombre=juego_data['nombre'],
            defaults=juego_data
        )
        
        if created:
            created_count += 1
            print(f'✅ Juego creado: {juego.nombre}')
        else:
            # Actualizar campos si el juego ya existe (excepto tipo_juego que es único)
            updated = False
            for field, value in juego_data.items():
                if field != 'nombre' and getattr(juego, field) != value:
                    setattr(juego, field, value)
                    updated = True
            
            if updated:
                juego.save()
                updated_count += 1
                print(f'🔄 Juego actualizado: {juego.nombre}')
    
    if created_count > 0 or updated_count > 0:
        total_juegos = Juego.objects.filter(activo=True).count()
        print(f'\n🎮 Juegos inicializados: {created_count} creados, {updated_count} actualizados')
        print(f'📊 Total de juegos activos: {total_juegos}')
