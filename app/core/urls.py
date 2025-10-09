from django.urls import include, path
from . import views

app_name = 'core'

urlpatterns = [
    # Autenticación
    path('login/', views.ProfesionalLoginView.as_view(), name='login'),
    path('register/', views.ProfesionalRegisterView.as_view(), name='register'),
    path('logout/', views.ProfesionalLogoutView.as_view(), name='logout'),
    
    # Recuperación de contraseña
    path('password-reset/', views.ProfesionalPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.ProfesionalPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.ProfesionalPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', views.ProfesionalPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # Vistas protegidas
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('documents/', views.DocumentsView.as_view(), name='documents'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('support/', views.SupportView.as_view(), name='support'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='profile_update'),
    path('account/delete/', views.DeleteAccountView.as_view(), name='delete_account'),
]
