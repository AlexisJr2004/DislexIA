from django.urls import path
from . import views

app_name = 'games'

urlpatterns = [
    path('games/buscar-palabras/', views.BuscarPalabrasView.as_view(), name='buscar_palabras'),
    path('games/ordenar-palabras/', views.OrdenarPalabrasView.as_view(), name='ordenar_palabras'),
    path('games/quiz-interactivo/', views.QuizInteractivoView.as_view(), name='quiz_interactivo'),
]
