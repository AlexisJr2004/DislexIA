from django.urls import path
from . import views

app_name = 'games'

urlpatterns = [
    # Lista de juegos
    path('game-list/', views.GameListView.as_view(), name='game_list'),
    # Inicializar juego (crear sesión)
    path('init/<slug:juego_slug>/', views.InitGameView.as_view(), name='init_game'),
    # Jugar juego (sesión específica)
    path('play/<str:url_sesion>/', views.PlayGameView.as_view(), name='play_game'),
    # API para finalizar sesión
    path('api/finish/<str:url_sesion>/', views.finish_game_session, name='finish_game_session'),
]
