import os
import json
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.utils import timezone
from django.contrib import messages
from app.games.models import Juego, SesionJuego, Evaluacion
from app.core.models import Profesional, Nino

@method_decorator(login_required, name='dispatch')
class GameListView(TemplateView):
    template_name = 'game_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener todos los juegos activos ordenados por su orden de visualización
        juegos = Juego.objects.filter(activo=True).order_by('orden_visualizacion', 'nombre')
        
        # Obtener el profesional actual directamente desde el usuario
        profesional = self.request.user

        # Obtener los niños asociados al profesional actual
        ninos = Nino.objects.filter(profesional=profesional)

        context.update({
            'page_title': 'Juegos - DislexIA',
            'active_section': 'games',
            'juegos': juegos,
            'ninos': ninos,
        })
        return context

@method_decorator(login_required, name='dispatch')
class InitGameView(TemplateView):
    """Vista para inicializar un juego y crear la sesión"""
    template_name = 'init_game.html'
    
    def get(self, request, *args, **kwargs):
        juego_slug = kwargs.get('juego_slug')
        
        # Obtener el juego
        juego = get_object_or_404(Juego, slug=juego_slug, activo=True)
        
        # Priorizar nino_id pasado por querystring
        nino = None
        nino_id = request.GET.get('nino_id')
        if nino_id:
            try:
                nino = Nino.objects.get(id=int(nino_id))
            except (Nino.DoesNotExist, ValueError):
                messages.error(request, "Niño no encontrado (nino_id inválido).")
                return redirect('games:game_list')

        # Si no se pasó nino_id, intentar usar el primer niño asociado al profesional
        if not nino:
            user = getattr(request, 'user', None)
            if user and user.is_authenticated and isinstance(user, Profesional):
                # intentar obtener un niño asociado a este profesional
                nino = Nino.objects.filter(profesional=user, activo=True).order_by('-fecha_registro').first()

        # Si aún no hay niño, usar por defecto id=1 (legacy) o pedir crear uno
        if not nino:
            try:
                nino = Nino.objects.get(id=1)
            except Nino.DoesNotExist:
                messages.error(request, "No se encontró un niño configurado. Por favor, configure al menos un niño antes de continuar.")
                return redirect('games:game_list')
        
        # Crear nueva evaluación
        evaluacion = Evaluacion.objects.create(
            nino=nino,
            fecha_hora_inicio=timezone.now(),
            estado='en_proceso'
        )
        
        # Crear nueva sesión de juego
        sesion = SesionJuego.crear_nueva_sesion(
            evaluacion=evaluacion,
            juego=juego,
            nivel=1  # Nivel por defecto
        )
        
        # Redirigir a la página del juego
        return redirect('games:play_game', url_sesion=sesion.url_sesion)

@method_decorator(login_required, name='dispatch')
class PlayGameView(TemplateView):
    """Vista para renderizar el contenido del juego"""
    template_name = 'play_game.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        url_sesion = kwargs.get('url_sesion')
        print(f"=== PlayGameView called with url_sesion: {url_sesion} ===")
        
        # Obtener la sesión
        sesion = get_object_or_404(SesionJuego, url_sesion=url_sesion)
        
        # ⭐ CASO 2: Al entrar al juego, registrar fecha_pausa para detectar salidas inesperadas
        # Si el usuario cierra el navegador sin hacer clic en "Salir", podremos calcular el tiempo pausado
        if sesion.estado == 'en_proceso' and not sesion.fecha_pausa:
            sesion.fecha_pausa = timezone.now()
            sesion.save(update_fields=['fecha_pausa'])
            print(f"⏸️ Registrado inicio de sesión para tracking: {sesion.fecha_pausa}")
        
        # Detectar si es evaluación secuencial de IA (tiene evaluacion Y ejercicio_numero)
        es_evaluacion_ia = sesion.evaluacion is not None and sesion.ejercicio_numero is not None

        # Verificar si el archivo de configuración existe
        if not sesion.juego.archivo_configuracion_existe():
            # Crear archivo template si no existe
            sesion.juego.crear_archivo_configuracion_template()
        
        # Leer el contenido del JSON
        game_config = None
        try:
            ruta_completa = os.path.join(settings.BASE_DIR, sesion.juego.ruta_archivo_configuracion)
            with open(ruta_completa, 'r', encoding='utf-8') as f:
                game_config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # Si hay error, crear archivo básico
            sesion.juego.crear_archivo_configuracion_template()
            # Intentar leer nuevamente
            try:
                with open(ruta_completa, 'r', encoding='utf-8') as f:
                    game_config = json.load(f)
            except:
                game_config = {"error": "No se pudo cargar la configuración del juego"}
        
        # Obtener todas las sesiones de esta evaluación ordenadas
        sesiones_evaluacion = SesionJuego.objects.filter(
            evaluacion=sesion.evaluacion
        ).select_related('juego').order_by('fecha_inicio')

        # Obtener todos los juegos activos ordenados
        juegos = Juego.objects.filter(activo=True).order_by('orden_visualizacion')

        # Agregar init_url a cada juego
        juegos_con_urls = []
        for juego in juegos:
            # Buscar si ya existe una sesión para este juego en la evaluación actual
            sesion_existente = sesiones_evaluacion.filter(juego=juego).first()
            if sesion_existente:
                # Usar la URL de la sesión existente
                init_url = f'/games/play/{sesion_existente.url_sesion}/'
            else:
                # Si no existe, crear nueva sesión (caso legacy)
                init_url = f'/games/init/{juego.slug}/?nino_id={sesion.evaluacion.nino.id}'
            
            juegos_con_urls.append({
                'id': juego.id,
                'slug': juego.slug,
                'nombre': juego.nombre,
                'init_url': init_url
            })
        
        context.update({
            'page_title': f'{sesion.juego.nombre} - DislexIA',
            'active_section': 'games',
            'sesion': sesion,
            'juego': sesion.juego,
            'evaluacion': sesion.evaluacion,
            'nino': sesion.evaluacion.nino,
            'game_config': game_config,
            'game_config_json': json.dumps(game_config, ensure_ascii=False, indent=2) if game_config else '{}',
            'juegos': juegos_con_urls,
            'juegos_json': json.dumps(juegos_con_urls, ensure_ascii=False),
            'es_evaluacion_ia': es_evaluacion_ia,
            'tiempo_pausado_segundos': sesion.tiempo_pausado_segundos,  # ⭐ NUEVO: Para ajustar el timer
        })
        
        print(f"=== PlayGameView returning template for game: {sesion.juego.nombre} ===")
        print(f"   Tiempo pausado acumulado: {sesion.tiempo_pausado_segundos}s")
        return context
