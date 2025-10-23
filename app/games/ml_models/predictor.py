"""
Predictor de Dislexia usando el modelo entrenado v2.2
CAMBIO: Umbrales de riesgo ajustados según el threshold del modelo (0.635)
"""

import json
import numpy as np
from pathlib import Path
import joblib

class DyslexiaPredictor:
    """
    Clase para realizar predicciones de dislexia basadas en evaluaciones cognitivas
    """
    
    _instance = None
    _model_loaded = False
    
    def __new__(cls):
        """Singleton pattern para cargar el modelo solo una vez"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializar el predictor (carga lazy del modelo)"""
        if not DyslexiaPredictor._model_loaded:
            self.model_dir = Path(__file__).parent / 'v2_2'
            self.model = None
            self.scaler = None
            self.features_list = None
            self.threshold = None
            
            # Intentar cargar el modelo
            try:
                self._load_model()
                DyslexiaPredictor._model_loaded = True
                print("✅ Modelo de dislexia cargado correctamente")
            except Exception as e:
                print(f"⚠️ Advertencia: No se pudo cargar el modelo: {e}")
                print("   El predictor funcionará en modo simulación")
    
    def _load_model(self):
        """Cargar el modelo y archivos auxiliares"""
        try:
            # Definir la función focal_loss_fixed ANTES de cargar el modelo
            def focal_loss_fixed(gamma=2.0, alpha=0.75):
                """Focal Loss personalizada para el modelo"""
                def focal_loss(y_true, y_pred):
                    import tensorflow as tf
                    epsilon = tf.keras.backend.epsilon()
                    y_pred = tf.clip_by_value(y_pred, epsilon, 1.0 - epsilon)
                    
                    # Calcular cross entropy
                    cross_entropy = -y_true * tf.math.log(y_pred)
                    
                    # Aplicar peso focal
                    weight = alpha * y_true * tf.pow(1 - y_pred, gamma)
                    loss = weight * cross_entropy
                    
                    return tf.reduce_mean(loss)
                return focal_loss
            
            # Cargar modelo de Keras/TensorFlow CON custom_objects
            import tensorflow as tf
            model_path = self.model_dir / 'dyslexia_model_v2_2.keras'
            
            if not model_path.exists():
                raise FileNotFoundError(f"No se encontró el modelo en {model_path}")
            
            self.model = tf.keras.models.load_model(
                str(model_path),
                custom_objects={'focal_loss_fixed': focal_loss_fixed()}
            )
            print(f"   ✓ Modelo cargado desde {model_path}")
            
        except Exception as e:
            raise Exception(f"Error al cargar modelo: {e}")
        
        try:
            # Cargar scaler
            scaler_path = self.model_dir / 'scaler.pkl'
            
            if not scaler_path.exists():
                raise FileNotFoundError(f"No se encontró el scaler en {scaler_path}")
            
            self.scaler = joblib.load(scaler_path)
            print(f"   ✓ Scaler cargado desde {scaler_path}")
            
        except Exception as e:
            raise Exception(f"Error al cargar scaler: {e}")
        
        try:
            # Cargar lista de features
            features_path = self.model_dir / 'features.json'
            
            if not features_path.exists():
                raise FileNotFoundError(f"No se encontró features.json en {features_path}")
            
            with open(features_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.features_list = data.get('features', data) if isinstance(data, dict) else data
            print(f"   ✓ Features cargadas: {len(self.features_list)} features")
            
        except Exception as e:
            raise Exception(f"Error al cargar features: {e}")
        
        try:
            # Cargar umbral óptimo
            threshold_path = self.model_dir / 'threshold.json'
            
            if not threshold_path.exists():
                print("   ⚠️ threshold.json no encontrado, usando umbral por defecto: 0.5")
                self.threshold = 0.5
            else:
                with open(threshold_path, 'r', encoding='utf-8') as f:
                    threshold_data = json.load(f)
                    self.threshold = threshold_data.get('optimal_threshold_f1', 0.5)
                print(f"   ✓ Umbral cargado: {self.threshold}")
                
        except Exception as e:
            print(f"   ⚠️ Error al cargar threshold, usando 0.5: {e}")
            self.threshold = 0.5
    
    def predict(self, features_dict):
        """
        Realiza una predicción de dislexia basada en las features proporcionadas
        
        Args:
            features_dict (dict): Diccionario con las 196 features
        
        Returns:
            dict: Resultado de la predicción
        """
        
        # Validar que tengamos el modelo cargado
        if self.model is None or self.scaler is None or self.features_list is None:
            print("⚠️ Modelo no disponible, generando predicción simulada")
            return self._generate_mock_prediction(features_dict)
        
        try:
            # === PASO 1: Ordenar features según el orden del modelo ===
            feature_values = []
            for feature_name in self.features_list:
                value = features_dict.get(feature_name, 0)
                feature_values.append(value)
            
            print(f"\n📊 Features preparadas: {len(feature_values)} valores")
            
            # === PASO 2: Convertir a numpy array ===
            X = np.array([feature_values])
            
            # === PASO 3: Escalar con el scaler ===
            X_scaled = self.scaler.transform(X)
            print(f"   ✓ Features escaladas")
            
            # === PASO 4: Realizar predicción ===
            probabilidad_raw = self.model.predict(X_scaled, verbose=0)[0][0]
            probabilidad = float(probabilidad_raw)
            
            print(f"   ✓ Predicción realizada: {probabilidad:.4f}")
            print(f"   ✓ Umbral del modelo: {self.threshold:.4f}")
            
            # === PASO 5: Aplicar umbral ===
            tiene_dislexia = probabilidad >= self.threshold
            
            # === PASO 6: Calcular confianza mejorada ===
            if probabilidad >= self.threshold:
                # Predice dislexia: confianza aumenta al acercarse a 1
                confianza = (probabilidad - self.threshold) / (1.0 - self.threshold)
            else:
                # Predice sin dislexia: confianza aumenta al acercarse a 0
                confianza = (self.threshold - probabilidad) / self.threshold

            # Normalizar a 0-1
            confianza = min(max(confianza, 0.0), 1.0)
            
            # === PASO 7: Determinar nivel de riesgo (AJUSTADO) ===
            # Ajustado para threshold = 0.635
            # 
            # RIESGO BAJO:   probabilidad < 0.35  (muy por debajo del threshold)
            # RIESGO MEDIO:  0.35 ≤ probabilidad < 0.75  (cerca del threshold o ligeramente arriba)
            # RIESGO ALTO:   probabilidad ≥ 0.75  (significativamente arriba del threshold)
            
            if probabilidad < 0.35:
                nivel_riesgo = 'BAJO'
            elif probabilidad < 0.75:
                nivel_riesgo = 'MEDIO'
            else:
                nivel_riesgo = 'ALTO'
            
            print(f"   ✓ Nivel de riesgo determinado: {nivel_riesgo}")
            print(f"      (probabilidad: {probabilidad:.4f}, rangos: <0.35=BAJO, 0.35-0.75=MEDIO, ≥0.75=ALTO)")
            
            # === PASO 8: Generar recomendación ===
            recomendacion = self._generar_recomendacion(
                tiene_dislexia, 
                probabilidad, 
                nivel_riesgo
            )
            
            # === PASO 9: Construir resultado ===
            resultado = {
                'tiene_dislexia': tiene_dislexia,
                'probabilidad': probabilidad,
                'probabilidad_porcentaje': round(probabilidad * 100, 2),
                'confianza': confianza,
                'confianza_porcentaje': round(confianza * 100, 2),
                'nivel_riesgo': nivel_riesgo,
                'clasificacion': 'Dislexia Detectada' if tiene_dislexia else 'Sin Dislexia',
                'umbral_utilizado': self.threshold,
                'recomendacion': recomendacion,
                'disclaimer': self._get_disclaimer()
            }
            
            print(f"✅ Predicción completada:")
            print(f"   - Clasificación: {resultado['clasificacion']}")
            print(f"   - Probabilidad: {resultado['probabilidad_porcentaje']:.2f}%")
            print(f"   - Nivel de riesgo: {resultado['nivel_riesgo']}")
            print(f"   - Confianza: {resultado['confianza_porcentaje']:.2f}%")
            
            return resultado
            
        except Exception as e:
            print(f"❌ Error durante la predicción: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'error': True,
                'mensaje': f'Error al realizar la predicción: {str(e)}',
                'tiene_dislexia': None,
                'probabilidad': None
            }
    
    def _generar_recomendacion(self, tiene_dislexia, probabilidad, nivel_riesgo):
        """
        Genera recomendaciones personalizadas según el resultado
        """
        if tiene_dislexia:
            if nivel_riesgo == 'ALTO':
                return (
                    "Se recomienda encarecidamente una evaluación neuropsicológica completa "
                    "por parte de un profesional especializado. Los indicadores sugieren una "
                    "alta probabilidad de dislexia que requiere atención profesional inmediata "
                    "para desarrollar un plan de intervención personalizado."
                )
            elif nivel_riesgo == 'MEDIO':
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
        """
        Retorna el disclaimer legal/médico
        """
        return (
            "IMPORTANTE: Este análisis es una herramienta de apoyo basada en inteligencia artificial "
            "y NO constituye un diagnóstico médico oficial. Los resultados deben ser interpretados "
            "por un profesional de la salud calificado (neuropsicólogo, psicólogo educativo o "
            "especialista en dislexia). Este sistema tiene una precisión aproximada del 86% según "
            "validaciones con datasets de referencia, pero puede variar según el caso individual. "
            "Siempre consulte con un profesional antes de tomar decisiones sobre el tratamiento."
        )
    
    def _generate_mock_prediction(self, features_dict):
        """
        Genera una predicción simulada cuando el modelo no está disponible
        """
        # Calcular un "score" simple basado en accuracy promedio
        total_accuracy = 0
        count = 0
        
        for i in range(1, 33):
            accuracy_key = f'Accuracy{i}'
            if accuracy_key in features_dict:
                total_accuracy += features_dict[accuracy_key]
                count += 1
        
        accuracy_promedio = total_accuracy / count if count > 0 else 80.0
        
        # Simular probabilidad inversa a la accuracy
        probabilidad = max(0.0, min(1.0, (100 - accuracy_promedio) / 100))
        
        tiene_dislexia = probabilidad >= 0.5
        
        if probabilidad < 0.35:
            nivel_riesgo = 'BAJO'
        elif probabilidad < 0.75:
            nivel_riesgo = 'MEDIO'
        else:
            nivel_riesgo = 'ALTO'
        
        return {
            'tiene_dislexia': tiene_dislexia,
            'probabilidad': probabilidad,
            'probabilidad_porcentaje': round(probabilidad * 100, 2),
            'confianza': 0.6,
            'confianza_porcentaje': 60.0,
            'nivel_riesgo': nivel_riesgo,
            'clasificacion': 'Dislexia Detectada' if tiene_dislexia else 'Sin Dislexia',
            'umbral_utilizado': 0.5,
            'recomendacion': f'PREDICCIÓN SIMULADA (accuracy promedio: {accuracy_promedio:.1f}%). ' + 
                           self._generar_recomendacion(tiene_dislexia, probabilidad, nivel_riesgo),
            'disclaimer': 'MODO SIMULACIÓN: El modelo real no está disponible. Esta es una predicción de prueba.',
            'simulacion': True
        }
    
    def get_model_info(self):
        """
        Retorna información sobre el modelo cargado
        """
        if self.model is None:
            return {
                'modelo_cargado': False,
                'modo': 'simulación'
            }
        
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


# === FUNCIÓN PRINCIPAL PARA USAR DESDE LAS VISTAS ===
def predecir_dislexia_desde_evaluacion(evaluacion_id):
    """
    Función de alto nivel para realizar predicción completa desde una evaluación
    
    Args:
        evaluacion_id (int): ID de la evaluación completada
    
    Returns:
        dict: Resultado completo con predicción y metadata
    """
    from .utils import (
        preparar_features_desde_evaluacion, 
        validar_features,
        obtener_resumen_evaluacion
    )
    
    print("="*80)
    print(f"🧠 INICIANDO PREDICCIÓN DE DISLEXIA - Evaluación #{evaluacion_id}")
    print("="*80)
    
    try:
        # === PASO 1: Obtener resumen ===
        resumen = obtener_resumen_evaluacion(evaluacion_id)
        if not resumen:
            return {
                'success': False,
                'error': f'No se encontró la evaluación con ID {evaluacion_id}'
            }
        
        print(f"\n📋 Evaluación: {resumen['nino']['nombre']} ({resumen['nino']['edad']} años)")
        print(f"   Sesiones completadas: {resumen['sesiones']['completadas']}/32")
        print(f"   Accuracy promedio: {resumen['metricas']['accuracy_promedio']}%")
        
        # === PASO 2: Preparar features ===
        print("\n🔄 Preparando features...")
        features = preparar_features_desde_evaluacion(evaluacion_id)
        
        # === PASO 3: Validar features ===
        print("\n✔️ Validando features...")
        es_valido, errores = validar_features(features)
        
        if not es_valido:
            print(f"❌ Validación fallida: {len(errores)} errores")
            for error in errores[:5]:
                print(f"   - {error}")
            
            return {
                'success': False,
                'error': 'Features inválidas',
                'errores_validacion': errores
            }
        
        print("✅ Features validadas correctamente")
        
        # === PASO 4: Realizar predicción ===
        print("\n🤖 Realizando predicción con modelo IA...")
        predictor = DyslexiaPredictor()
        resultado = predictor.predict(features)
        
        # === PASO 5: Combinar resultado con metadata ===
        resultado_completo = {
            'success': True,
            'evaluacion': resumen,
            'prediccion': resultado,
            'modelo_info': predictor.get_model_info()
        }
        
        print("\n" + "="*80)
        print("✅ PREDICCIÓN COMPLETADA EXITOSAMENTE")
        print("="*80)
        
        return resultado_completo
        
    except Exception as e:
        print(f"\n❌ ERROR durante la predicción: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }