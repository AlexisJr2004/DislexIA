from django.urls import path
from . import views
from .views import get_citas_dia, crear_cita, eliminar_cita, marcar_cita_completada, agregar_nino_ajax

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

    # Citas
    path('citas/dia/', get_citas_dia, name='get_citas_dia'),
    path('citas/crear/', crear_cita, name='crear_cita'),
    path('citas/<int:cita_id>/eliminar/', eliminar_cita, name='eliminar_cita'),
    path('citas/<int:cita_id>/completar/', marcar_cita_completada, name='marcar_cita_completada'),

    # Gestión de niños
    path('nino/<int:pk>/editar/', views.EditarNinoView.as_view(), name='editar_nino'),
    path('nino/<int:pk>/datos/', views.ObtenerDatosNinoView.as_view(), name='obtener_datos_nino'),
    path('lista-ninos/', views.ListaNinosView.as_view(), name='lista_ninos'),
    path('nino/<int:pk>/eliminar/', views.EliminarNinoView.as_view(), name='eliminar_nino'),
    path('nino/agregar/', agregar_nino_ajax, name='agregar_nino'),

    # API endpoints para citas
    path('api/citas/dia/', views.get_citas_dia, name='get_citas_dia'),
    path('api/citas/crear/', views.crear_cita, name='crear_cita'),
    path('api/citas/<int:cita_id>/eliminar/', views.eliminar_cita, name='eliminar_cita'),
    path('api/citas/<int:cita_id>/completar/', views.marcar_cita_completada, name='marcar_cita_completada'),

    # Reporte IA
    path('reporte-ia/<int:pk>/', views.ReporteIADetailView.as_view(), name='reporte_ia_detail'),

    # Validación Profesional
    path('validacion_profesional_create/<int:reporteia_id>/', views.ValidacionProfesionalCreateView.as_view(), name='validacion_profesional_create'),
    path('validacion_profesional_edit/<int:reporteia_id>/', views.ValidacionProfesionalUpdateView.as_view(), name='validacion_profesional_edit'),

    # API endpoint para notificaciones
    path('api/notificaciones/', views.get_notificaciones, name='get_notificaciones'),
]
