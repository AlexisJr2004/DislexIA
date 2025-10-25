from django.urls import path
from app.games.views import (
    api_views,
    game_views,
    nino_views,
    results_views,
    session_views
)

app_name = 'games'

urlpatterns = [
    # Lista de juegos
    path('game-list/', game_views.GameListView.as_view(), name='game_list'),
    # Lista de sesión de juegos
    path('session-list/', session_views.GameSessionListView.as_view(), name='session_list'),
    # Inicializar evaluación IA completa (todos los juegos)
    path('ia/init/', session_views.InitSequentialEvaluationView.as_view(), name='init_sequential_evaluation'),
    # Inicializar juego (crear sesión)
    path('init/<slug:juego_slug>/', game_views.InitGameView.as_view(), name='init_game'),
    # Jugar juego (sesión específica)
    path('play/<str:url_sesion>/', game_views.PlayGameView.as_view(), name='play_game'),
    # APIs del juego
    path('api/question-response/', api_views.save_question_response, name='save_question_response'),
    path('api/level-complete/', api_views.save_level_complete, name='save_level_complete'),
    path('api/finish/<str:url_sesion>/', session_views.finish_game_session, name='finish_game_session'),
    # Endpoint AJAX para crear niño y asociarlo al profesional
    path('api/crear-nino/', nino_views.crear_nino_ajax, name='crear_nino_ajax'),
    # Endpoint para asignar un niño existente a un juego
    path('asignar-nino/', api_views.asignar_nino, name='asignar_nino'),
    # Resultados de evaluación secuencial
    path('results/<int:evaluacion_id>/', results_views.SequentialResultsView.as_view(), name='sequential_results'),
    # Eliminar evaluación
    path('evaluacion/delete/<int:evaluacion_id>/', session_views.delete_evaluacion, name='delete_evaluacion'),
    # Finalizar juegos
    path('individual/finish/<str:url_sesion>/', session_views.finish_individual_game, name='finish_individual_game'),
    path('evaluation/finish/<str:url_sesion>/', session_views.finish_evaluation_game, name='finish_evaluation_game'),
    # Ejecutar comando populate_sessions
    path('ejecutar-populate-sessions/', session_views.ejecutar_populate_sessions, name='ejecutar_populate_sessions'),
]
