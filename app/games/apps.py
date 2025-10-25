from django.apps import AppConfig


class GamesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.games'
    
    def ready(self):
        """Importar signals cuando la app esté lista"""
        import app.games.signals
        
        """Pre-cargar modelo al iniciar Django"""
        from app.games.ml_models.predictor import _load_model_once
        try:
            _load_model_once()
            print("✅ Modelo de IA pre-cargado al iniciar servidor")
        except Exception as e:
            print(f"⚠️ No se pudo pre-cargar modelo: {e}")