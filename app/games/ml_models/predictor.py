"""
Predictor de Dislexia usando el modelo entrenado v2.2
OPTIMIZADO: Singleton verdadero con threading.Lock
"""

import json
import numpy as np
from pathlib import Path
import joblib
import threading

# CACHE GLOBAL CON LOCK PARA THREAD-SAFETY
_MODEL_LOCK = threading.Lock()
_GLOBAL_MODEL_CACHE = {
    'model': None,
    'scaler': None,
    'features_list': None,
    'threshold': None,
    'loaded': False,
    'pid': None  # Para detectar si cambiamos de proceso
}


def _get_current_pid():
    """Obtiene el PID del proceso actual"""
    import os
    return os.getpid()


def _load_model_once():
    """
    Carga el modelo UNA SOLA VEZ por proceso usando lock
    Thread-safe y process-aware
    """
    global _GLOBAL_MODEL_CACHE
    
    current_pid = _get_current_pid()
    
    # Verificar si ya está cargado EN ESTE PROCESO
    with _MODEL_LOCK:
        if _GLOBAL_MODEL_CACHE['loaded'] and _GLOBAL_MODEL_CACHE['pid'] == current_pid:
            print(f"⚡ Modelo ya cargado en cache (PID: {current_pid})")
            return _GLOBAL_MODEL_CACHE
        
        # Si el PID cambió, necesitamos recargar (nuevo proceso)
        if _GLOBAL_MODEL_CACHE['pid'] and _GLOBAL_MODEL_CACHE['pid'] != current_pid:
            print(f"🔄 Nuevo proceso detectado (PID: {current_pid}), recargando modelo...")
            _GLOBAL_MODEL_CACHE['loaded'] = False
        
        print(f"🔄 Cargando modelo (PID: {current_pid})...")
        
        try:
            model_dir = Path(__file__).parent / 'v2_2'
            
            # === 1. CARGAR MODELO KERAS ===
            def focal_loss_fixed(gamma=2.0, alpha=0.75):
                def focal_loss(y_true, y_pred):
                    import tensorflow as tf
                    epsilon = tf.keras.backend.epsilon()
                    y_pred = tf.clip_by_value(y_pred, epsilon, 1.0 - epsilon)
                    cross_entropy = -y_true * tf.math.log(y_pred)
                    weight = alpha * y_true * tf.pow(1 - y_pred, gamma)
                    loss = weight * cross_entropy
                    return tf.reduce_mean(loss)
                return focal_loss
            
            # Suprimir warnings de TensorFlow (opcional)
            import os
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
            
            import tensorflow as tf
            model_path = model_dir / 'dyslexia_model_v2_2.keras'
            
            if not model_path.exists():
                raise FileNotFoundError(f"Modelo no encontrado: {model_path}")
            
            _GLOBAL_MODEL_CACHE['model'] = tf.keras.models.load_model(
                str(model_path),
                custom_objects={'focal_loss_fixed': focal_loss_fixed()}
            )
            print(f"   ✓ Modelo cargado")
            
            # === 2. CARGAR SCALER ===
            scaler_path = model_dir / 'scaler.pkl'
            if not scaler_path.exists():
                raise FileNotFoundError(f"Scaler no encontrado: {scaler_path}")
            
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                _GLOBAL_MODEL_CACHE['scaler'] = joblib.load(scaler_path)
            print(f"   ✓ Scaler cargado")
            
            # === 3. CARGAR FEATURES ===
            features_path = model_dir / 'features.json'
            if not features_path.exists():
                raise FileNotFoundError(f"Features no encontradas: {features_path}")
            
            with open(features_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                _GLOBAL_MODEL_CACHE['features_list'] = data.get('features', data) if isinstance(data, dict) else data
            print(f"   ✓ Features: {len(_GLOBAL_MODEL_CACHE['features_list'])}")
            
            # === 4. CARGAR THRESHOLD ===
            threshold_path = model_dir / 'threshold.json'
            if threshold_path.exists():
                with open(threshold_path, 'r', encoding='utf-8') as f:
                    threshold_data = json.load(f)
                    _GLOBAL_MODEL_CACHE['threshold'] = threshold_data.get('optimal_threshold_f1', 0.5)
            else:
                _GLOBAL_MODEL_CACHE['threshold'] = 0.5
            print(f"   ✓ Umbral: {_GLOBAL_MODEL_CACHE['threshold']}")
            
            # Marcar como cargado para ESTE proceso
            _GLOBAL_MODEL_CACHE['loaded'] = True
            _GLOBAL_MODEL_CACHE['pid'] = current_pid
            print(f"✅ Modelo cacheado (PID: {current_pid})\n")
            
            return _GLOBAL_MODEL_CACHE
            
        except Exception as e:
            print(f"❌ Error al cargar modelo: {e}")
            _GLOBAL_MODEL_CACHE['loaded'] = False
            _GLOBAL_MODEL_CACHE['pid'] = None
            raise


class DyslexiaPredictor:
    """
    Predictor optimizado con cache global thread-safe
    """
    
    def __init__(self):
        """Inicializar predictor (sin cargar modelo)"""
        self.model = None
        self.scaler = None
        self.features_list = None
        self.threshold = None
    
    def _ensure_model_loaded(self):
        """Asegurar que el modelo esté cargado (lazy loading con lock)"""
        global _GLOBAL_MODEL_CACHE
        
        current_pid = _get_current_pid()
        
        # Fast path: si ya está cargado en este proceso, solo asignar referencias
        if _GLOBAL_MODEL_CACHE['loaded'] and _GLOBAL_MODEL_CACHE['pid'] == current_pid:
            if self.model is None:  # Solo asignar si no lo hemos hecho ya
                self.model = _GLOBAL_MODEL_CACHE['model']
                self.scaler = _GLOBAL_MODEL_CACHE['scaler']
                self.features_list = _GLOBAL_MODEL_CACHE['features_list']
                self.threshold = _GLOBAL_MODEL_CACHE['threshold']
            return
        
        # Slow path: necesitamos cargar
        cache = _load_model_once()
        self.model = cache['model']
        self.scaler = cache['scaler']
        self.features_list = cache['features_list']
        self.threshold = cache['threshold']
    
    def predict(self, features_dict):
        """
        Realiza predicción de dislexia
        
        Args:
            features_dict (dict): 196 features
        
        Returns:
            dict: Resultado de predicción
        """
        # Cargar modelo si no está disponible
        self._ensure_model_loaded()
        
        # Validar que el modelo esté cargado
        if self.model is None or self.scaler is None:
            print("⚠️ Modelo no disponible, generando predicción simulada")
            return self._generate_mock_prediction(features_dict)
        
        try:
            # === PREPARAR FEATURES ===
            feature_values = [features_dict.get(name, 0) for name in self.features_list]
            X = np.array([feature_values])
            
            # Suprimir warning de feature names
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                X_scaled = self.scaler.transform(X)
            
            # === PREDICCIÓN (con verbose=0 para silenciar logs) ===
            probabilidad = float(self.model.predict(X_scaled, verbose=0)[0][0])
            tiene_dislexia = probabilidad >= self.threshold
            
            # === CALCULAR CONFIANZA ===
            if probabilidad >= self.threshold:
                confianza = (probabilidad - self.threshold) / (1.0 - self.threshold)
            else:
                confianza = (self.threshold - probabilidad) / self.threshold
            
            confianza = min(max(confianza, 0.0), 1.0)
            
            # === GENERAR RECOMENDACIÓN ===
            recomendacion = self._generar_recomendacion(tiene_dislexia, probabilidad)
            
            # === RESULTADO ===
            return {
                'tiene_dislexia': tiene_dislexia,
                'probabilidad': probabilidad,
                'probabilidad_porcentaje': round(probabilidad * 100, 2),
                'confianza': confianza,
                'confianza_porcentaje': round(confianza * 100, 2),
                'clasificacion': 'Dislexia Detectada' if tiene_dislexia else 'Sin Dislexia',
                'umbral_utilizado': self.threshold,
                'recomendacion': recomendacion,
                'disclaimer': self._get_disclaimer()
            }
            
        except Exception as e:
            print(f"❌ Error durante predicción: {e}")
            import traceback
            traceback.print_exc()
            return {
                'error': True,
                'mensaje': f'Error al realizar predicción: {str(e)}',
                'tiene_dislexia': None,
                'probabilidad': None
            }
    
    def _generar_recomendacion(self, tiene_dislexia, probabilidad):
        """Genera recomendaciones personalizadas"""
        if tiene_dislexia:
            if probabilidad >= 0.75:
                return (
                    "Se recomienda encarecidamente una evaluación neuropsicológica completa "
                    "por parte de un profesional especializado. Los indicadores sugieren una "
                    "alta probabilidad de dislexia que requiere atención profesional inmediata "
                    "para desarrollar un plan de intervención personalizado."
                )
            elif probabilidad >= 0.35:
                return (
                    "Se sugiere realizar una evaluación profesional más detallada. "
                    "Los resultados indican indicadores de dislexia que deberían ser "
                    "confirmados por un especialista. Considere programar una consulta "
                    "con un neuropsicólogo para obtener un diagnóstico preciso."
                )
            else:
                return (
                    "Aunque los indicadores sugieren la presencia de dislexia, la probabilidad "
                    "es relativamente baja. Se recomienda mantener seguimiento del desarrollo "
                    "cognitivo y considerar una evaluación profesional si las dificultades persisten."
                )
        else:
            if probabilidad < 0.2:
                return (
                    "Los resultados no indican signos significativos de dislexia. "
                    "El desempeño en las evaluaciones cognitivas se encuentra dentro "
                    "de los rangos esperados. Se recomienda continuar con el seguimiento "
                    "regular del desarrollo académico."
                )
            else:
                return (
                    "Aunque no se detectó dislexia, algunos indicadores están cerca del umbral. "
                    "Se recomienda mantener seguimiento y considerar reforzar las áreas "
                    "que mostraron un desempeño ligeramente por debajo del promedio."
                )
    
    def _get_disclaimer(self):
        """Disclaimer legal/médico"""
        return (
            "IMPORTANTE: Este análisis es una herramienta de apoyo basada en inteligencia artificial "
            "y NO constituye un diagnóstico médico oficial. Los resultados deben ser interpretados "
            "por un profesional de la salud calificado (neuropsicólogo, psicólogo educativo o "
            "especialista en dislexia). Este sistema tiene una precisión aproximada del 86% según "
            "validaciones con datasets de referencia, pero puede variar según el caso individual. "
            "Siempre consulte con un profesional antes de tomar decisiones sobre el tratamiento."
        )
    
    def _generate_mock_prediction(self, features_dict):
        """Genera predicción simulada cuando el modelo no está disponible"""
        total_accuracy = sum(features_dict.get(f'Accuracy{i}', 0.8) for i in range(1, 33)) / 32
        probabilidad = max(0.0, min(1.0, 1.0 - total_accuracy))
        tiene_dislexia = probabilidad >= 0.5
        
        return {
            'tiene_dislexia': tiene_dislexia,
            'probabilidad': probabilidad,
            'probabilidad_porcentaje': round(probabilidad * 100, 2),
            'confianza': 0.6,
            'confianza_porcentaje': 60.0,
            'clasificacion': 'Dislexia Detectada' if tiene_dislexia else 'Sin Dislexia',
            'umbral_utilizado': 0.5,
            'recomendacion': f'PREDICCIÓN SIMULADA (accuracy: {total_accuracy*100:.1f}%). ' + \
                           self._generar_recomendacion(tiene_dislexia, probabilidad),
            'disclaimer': 'MODO SIMULACIÓN: Modelo no disponible.',
            'simulacion': True
        }
    
    def get_model_info(self):
        """Información del modelo"""
        self._ensure_model_loaded()
        
        if self.model is None:
            return {'modelo_cargado': False, 'modo': 'simulación'}
        
        return {
            'modelo_cargado': True,
            'modo': 'producción',
            'version': 'v2.2',
            'total_features': len(self.features_list) if self.features_list else 0,
            'umbral': self.threshold,
            'arquitectura': 'Deep Feedforward Neural Network',
            'metricas': {
                'roc_auc': 0.8210,
                'precision': 0.4167,
                'recall': 0.6019,
                'f1_score': 0.4924,
                'accuracy': 0.8671
            }
        }


# ===================================================================
# FUNCIÓN PRINCIPAL
# ===================================================================
def predecir_dislexia_desde_evaluacion(evaluacion_id):
    """
    Función de alto nivel para predicción desde evaluación
    
    Args:
        evaluacion_id (int): ID de evaluación
    
    Returns:
        dict: Resultado completo
    """
    from .utils import (
        preparar_features_desde_evaluacion, 
        validar_features,
        obtener_resumen_evaluacion
    )
    
    print("="*80)
    print(f"🧠 INICIANDO PREDICCIÓN - Evaluación #{evaluacion_id}")
    print("="*80)
    
    try:
        # === PASO 1: Resumen ===
        resumen = obtener_resumen_evaluacion(evaluacion_id)
        if not resumen:
            return {'success': False, 'error': f'Evaluación {evaluacion_id} no encontrada'}
        
        print(f"\n📋 Evaluación: {resumen['nino']['nombre']} ({resumen['nino']['edad']} años)")
        print(f"   Sesiones: {resumen['sesiones']['completadas']}/32")
        print(f"   Accuracy: {resumen['metricas']['accuracy_promedio']}%")
        
        precision_promedio = resumen['metricas']['accuracy_promedio']
        
        # === PASO 2: Preparar features ===
        print("\n🔄 Preparando features...")
        features = preparar_features_desde_evaluacion(evaluacion_id)
        
        # === PASO 3: Validar ===
        print("\n✔️ Validando features...")
        es_valido, errores = validar_features(features)
        if not es_valido:
            print(f"❌ Validación fallida: {len(errores)} errores")
            return {'success': False, 'error': 'Features inválidas', 'errores': errores}
        
        print("✅ Features validadas")
        
        # === PASO 4: Predicción ===
        print("\n🤖 Realizando predicción...")
        predictor = DyslexiaPredictor()
        resultado = predictor.predict(features)
        
        # === PASO 5: Clasificación por accuracy ===
        if precision_promedio < 60:
            tiene_dislexia = True
            clasificacion = 'Dislexia Detectada'
            clasificacion_riesgo = 'alto'
            recomendacion = (
                "Se recomienda encarecidamente una evaluación neuropsicológica completa "
                "por parte de un profesional especializado. Los indicadores sugieren una "
                "alta probabilidad de dislexia que requiere atención profesional inmediata."
            )
        elif precision_promedio < 80:
            tiene_dislexia = True
            clasificacion = 'Riesgo Medio de Dislexia'
            clasificacion_riesgo = 'medio'
            recomendacion = (
                "Se sugiere realizar una evaluación profesional más detallada. "
                "Los resultados indican indicadores de dislexia que deberían ser "
                "confirmados por un especialista."
            )
        else:
            tiene_dislexia = False
            clasificacion = 'Sin Dislexia'
            clasificacion_riesgo = 'bajo'
            recomendacion = (
                "Los resultados no indican signos significativos de dislexia. "
                "El desempeño se encuentra dentro de los rangos esperados."
            )
        
        resultado['tiene_dislexia'] = tiene_dislexia
        resultado['clasificacion'] = clasificacion
        resultado['clasificacion_riesgo'] = clasificacion_riesgo
        resultado['recomendacion'] = recomendacion
        resultado['precision_promedio'] = precision_promedio
        
        resultado_completo = {
            'success': True,
            'evaluacion': resumen,
            'prediccion': resultado,
            'modelo_info': predictor.get_model_info()
        }
        
        print("\n" + "="*80)
        print("✅ PREDICCIÓN COMPLETADA")
        print("="*80)
        
        return resultado_completo
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e), 'traceback': traceback.format_exc()}