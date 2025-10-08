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
            'descripcion': 'Observa la imagen y selecciona la palabra que la describe correctamente entre varias opciones. Evalúa reconocimiento visual y ortografía.',
            'categoria': 'reconocimiento_visual',
            'dificultad': 'facil',
            'color_tema': 'green',
            'duracion_estimada_minutos': 8,
            'puntuacion_promedio': 4.6,
            'orden_visualizacion': 1,
            'slug': 'selecciona-la-palabra-correcta',  # Slug se auto-genera, pero lo mantenemos para compatibilidad
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
            'nombre': 'Ordenar Palabras',
            'descripcion': 'Organiza las palabras en el orden correcto para formar oraciones coherentes. Desarrolla gramática y sintaxis.',
            'categoria': 'lectura_comprension',
            'dificultad': 'dificil',
            'color_tema': 'orange',
            'duracion_estimada_minutos': 20,
            'puntuacion_promedio': 4.9,
            'orden_visualizacion': 7,
        }
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
            
            # Crear archivo JSON de configuración si no existe
            if not juego.archivo_configuracion_existe():
                try:
                    juego.crear_archivo_configuracion_template()
                    print(f'📄 Archivo JSON creado: {juego.archivo_configuracion}')
                except Exception as e:
                    print(f'❌ Error creando JSON para {juego.nombre}: {e}')
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
                
            # Verificar si necesita archivo JSON
            if not juego.archivo_configuracion_existe():
                try:
                    juego.crear_archivo_configuracion_template()
                    print(f'📄 Archivo JSON creado para juego existente: {juego.archivo_configuracion}')
                except Exception as e:
                    print(f'❌ Error creando JSON para {juego.nombre}: {e}')
    
    if created_count > 0 or updated_count > 0:
        total_juegos = Juego.objects.filter(activo=True).count()
        print(f'\n🎮 Juegos inicializados: {created_count} creados, {updated_count} actualizados')
        print(f'📊 Total de juegos activos: {total_juegos}')
