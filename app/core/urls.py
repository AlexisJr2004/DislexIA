from django.urls import path
from django.views.generic import TemplateView
from app.core.views import (
    views_auth,
    views_profile,
    views_calendar,
    views_nino,
    views_report,
    views_misc,
    views_admin,
    views_gdpr,
)

app_name = 'core'

urlpatterns = [
    # Autenticación
    path('login/', views_auth.ProfesionalLoginView.as_view(), name='login'),
    path('register/', views_auth.ProfesionalRegisterView.as_view(), name='register'),
    path('logout/', views_auth.ProfesionalLogoutView.as_view(), name='logout'),

    # Recuperación de contraseña
    path('password-reset/', views_auth.ProfesionalPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views_auth.ProfesionalPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', views_auth.ProfesionalPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', views_auth.ProfesionalPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # Vistas protegidas
    path('calendar/', views_calendar.CalendarView.as_view(), name='calendar'),
    path('documents/', views_misc.DocumentsView.as_view(), name='documents'),
    path('settings/', views_misc.SettingsView.as_view(), name='settings'),
    path('support/', views_misc.SupportView.as_view(), name='support'),
    path('profile/', views_profile.ProfileView.as_view(), name='profile'),
    path('profile/update/', views_profile.ProfileUpdateView.as_view(), name='profile_update'),
    path('account/delete/', views_profile.DeleteAccountView.as_view(), name='delete_account'),

    # Gestión de niños
    # path('nino/<int:pk>/editar/', views.EditarNinoView.as_view(), name='editar_nino'),
    # path('nino/<int:pk>/datos/', views.ObtenerDatosNinoView.as_view(), name='obtener_datos_nino'),
    # path('lista-ninos/', views.ListaNinosView.as_view(), name='lista_ninos'),
    # path('eliminar-nino/<int:pk>/', views.EliminarNinoView.as_view(), name='eliminar_nino'),
    # Citas
    path('citas/dia/', views_calendar.get_citas_dia, name='get_citas_dia'),
    path('citas/crear/', views_calendar.crear_cita, name='crear_cita'),
    path('citas/<int:cita_id>/eliminar/', views_calendar.eliminar_cita, name='eliminar_cita'),
    path('citas/<int:cita_id>/completar/', views_calendar.marcar_cita_completada, name='marcar_cita_completada'),

    # Gestión de niños
    path('nino/<int:pk>/editar/', views_nino.EditarNinoView.as_view(), name='editar_nino'),
    path('nino/<int:pk>/datos/', views_nino.ObtenerDatosNinoView.as_view(), name='obtener_datos_nino'),
    path('lista-ninos/', views_nino.ListaNinosView.as_view(), name='lista_ninos'),
    path('nino/<int:pk>/eliminar/', views_nino.EliminarNinoView.as_view(), name='eliminar_nino'),
    path('nino/agregar/', views_nino.agregar_nino_ajax, name='agregar_nino'),

    # API endpoints para citas
    path('api/citas/dia/', views_calendar.get_citas_dia, name='get_citas_dia'),
    path('api/citas/crear/', views_calendar.crear_cita, name='crear_cita'),
    path('api/citas/<int:cita_id>/eliminar/', views_calendar.eliminar_cita, name='eliminar_cita'),
    path('api/citas/<int:cita_id>/completar/', views_calendar.marcar_cita_completada, name='marcar_cita_completada'),

    # Reporte IA
    path('reporte-ia/<int:pk>/', views_report.ReporteIADetailView.as_view(), name='reporte_ia_detail'),

    # Reporte PDF
    path('reporte/ia/<int:pk>/pdf/', views_report.generar_reporte_pdf, name='generar_reporte_pdf'),

    # Validación Profesional
    path('validacion_profesional_create/<int:reporteia_id>/', views_report.ValidacionProfesionalCreateView.as_view(), name='validacion_profesional_create'),
    path('validacion_profesional_edit/<int:reporteia_id>/', views_report.ValidacionProfesionalUpdateView.as_view(), name='validacion_profesional_edit'),

    # API endpoint para notificaciones
    path('api/notificaciones/', views_misc.get_notificaciones, name='get_notificaciones'),
    
    # Historial de evaluaciones por niño
    path('nino/<int:pk>/historico/', views_nino.HistorialNinoView.as_view(), name='historico_nino'),
    
    # Toggle estado de niño (profesional)
    path('nino/<int:pk>/toggle-status/', views_nino.toggle_nino_status, name='toggle_nino_status'),
    
    # Gestión de usuarios (solo administradores)
    path('administracion/usuarios/', views_admin.GestionUsuariosView.as_view(), name='gestion_usuarios'),
    path('administracion/usuarios/<int:pk>/toggle-status/', views_admin.toggle_usuario_status, name='toggle_usuario_status'),
    
    # Gestión de niños admin (solo administradores)
    path('administracion/ninos/', views_admin.GestionNinosAdminView.as_view(), name='gestion_ninos_admin'),
    path('administracion/ninos/<int:pk>/toggle-status/', views_admin.toggle_nino_status_admin, name='toggle_nino_status_admin'),
    
    # ============================================
    # RUTAS GDPR - Cumplimiento Legal
    # ============================================
    
    # Documentos legales
    path('legal/privacy-policy/', TemplateView.as_view(template_name='legal/privacy_policy.html'), name='privacy_policy'),
    path('legal/terms-conditions/', TemplateView.as_view(template_name='legal/terms_conditions.html'), name='terms_conditions'),
    
    # Derechos del usuario GDPR
    path('exportar-datos/', views_gdpr.exportar_datos_usuario, name='exportar_datos'),
    path('consentimientos/', views_gdpr.vista_consentimientos, name='consentimientos'),
    path('consentimientos/revocar/', views_gdpr.revocar_consentimiento, name='revocar_consentimiento'),
    path('historial-auditoria/', views_gdpr.historial_auditoria_usuario, name='historial_auditoria'),
]
