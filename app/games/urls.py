from django.urls import path
from . import views

app_name = 'games'

urlpatterns = [
    path('game-list/', views.GameListView.as_view(), name='game_list'),
    
    # Juegos existentes
    path('buscar-palabras/', views.BuscarPalabrasView.as_view(), name='buscar_palabras'),
    path('ordenar-palabras/', views.OrdenarPalabrasView.as_view(), name='ordenar_palabras'),
    path('quiz-interactivo/', views.QuizInteractivoView.as_view(), name='quiz_interactivo'),
    
    # Nuevos juegos
    path('seleccionar-palabra-imagen/', views.SeleccionarPalabraImagenView.as_view(), name='seleccionar_palabra_imagen'),
    path('escribir-nombre-objeto/', views.EscribirNombreObjetoView.as_view(), name='escribir_nombre_objeto'),
    path('completar-palabra-letra/', views.CompletarPalabraLetraView.as_view(), name='completar_palabra_letra'),
    path('seleccionar-palabra-audio/', views.SeleccionarPalabraAudioView.as_view(), name='seleccionar_palabra_audio'),
    path('encontrar-error-palabra/', views.EncontrarErrorPalabraView.as_view(), name='encontrar_error_palabra'),
]
