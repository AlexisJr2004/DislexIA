from django.urls import path
from . import views

app_name = 'games'

urlpatterns = [
    # Lista de juegos
    path('game-list/', views.GameListView.as_view(), name='game_list'),
    # Lista de sesión de juegos 
    path('session-list/', views.GameSessionListView.as_view(), name='session_list'),
    # Inicializar juego (crear sesión)
    path('init/<slug:juego_slug>/', views.InitGameView.as_view(), name='init_game'),
    # Jugar juego (sesión específica)
    path('play/<str:url_sesion>/', views.PlayGameView.as_view(), name='play_game'),
    # APIs del juego
    path('api/question-response/', views.save_question_response, name='save_question_response'),
    path('api/level-complete/', views.save_level_complete, name='save_level_complete'),
    path('api/finish/<str:url_sesion>/', views.finish_game_session, name='finish_game_session'),
    # Endpoint AJAX para crear niño y asociarlo al profesional
    path('api/crear-nino/', views.crear_nino_ajax, name='crear_nino_ajax'),
    # Endpoint para asignar un niño existente a un juego
    path('asignar-nino/', views.asignar_nino, name='asignar_nino'),
]
