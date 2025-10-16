# app/ml_models/predictor.py

import os
import json
import joblib
import numpy as np
from pathlib import Path
from django.conf import settings
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras import backend as K


class DyslexiaPredictor:
    """
    Predictor de dislexia usando modelo entrenado v2.2
    """
    
    _instance = None  # Singleton para evitar cargar el modelo múltiples veces
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DyslexiaPredictor, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Ruta al directorio del modelo
        self.model_dir = Path(settings.BASE_DIR) / 'app' / 'ml_models' / 'v2_2'
        
        # Cargar modelo
        print("🔄 Cargando modelo de dislexia...")
        self.model = load_model(
            str(self.model_dir / 'dyslexia_model_v2_2.keras'),
            custom_objects={'focal_loss_fixed': self._focal_loss()}
        )
        
        # Cargar scaler
        self.scaler = joblib.load(str(self.model_dir / 'scaler.pkl'))
        
        # Cargar features
        with open(self.model_dir / 'features.json', 'r', encoding='utf-8') as f:
            self.features = json.load(f)['features']
        
        # Cargar threshold
        with open(self.model_dir / 'threshold.json', 'r', encoding='utf-8') as f:
            self.threshold = json.load(f)['optimal_threshold_f1']
        
        self._initialized = True
        print(f"✅ Modelo cargado exitosamente")
        print(f"   • Features: {len(self.features)}")
        print(f"   • Umbral: {self.threshold:.4f}")
    
    def _focal_loss(self, gamma=2.0, alpha=0.75):
        """Define Focal Loss para el modelo"""
        def focal_loss_fixed(y_true, y_pred):
            epsilon = K.epsilon()
            y_pred = K.clip(y_pred, epsilon, 1.0 - epsilon)
            pt = tf.where(tf.equal(y_true, 1), y_pred, 1 - y_pred)
            return -K.mean(alpha * K.pow(1.0 - pt, gamma) * K.log(pt))
        return focal_loss_fixed
    
    def predict(self, session_data):
        """
        Realiza predicción de dislexia
        
        Args:
            session_data (dict): Diccionario con estructura:
                {
                    'age': int,
                    'gender': str ('Male' o 'Female'),
                    'native_language': str ('Yes' o 'No'),
                    'has_other_languages': str ('Yes' o 'No'),
                    'exercises': {
                        1: {'clicks': int, 'hits': int, 'misses': int, 
                            'score': float, 'accuracy': float, 'missrate': float},
                        ...
                        32: {...}
                    }
                }
        
        Returns:
            dict: Resultado de la predicción con estructura:
                {
                    'prediction': str ('Dislexia' o 'No Dislexia'),
                    'probability': float,
                    'confidence': str ('BAJA', 'MEDIA', 'ALTA'),
                    'risk_level': str ('BAJO', 'MEDIO', 'ALTO'),
                    'recommendation': str,
                    'disclaimer': str
                }
        """
        # Validar datos de entrada
        self._validate_input(session_data)
        
        # Preparar features
        feature_dict = self._prepare_features(session_data)
        
        # Crear array en orden correcto
        features_array = np.array([[feature_dict.get(f, 0) for f in self.features]])
        
        # Verificar valores faltantes
        if np.isnan(features_array).any():
            print("⚠️ Advertencia: Valores NaN detectados, reemplazando con 0")
            features_array = np.nan_to_num(features_array, nan=0.0)
        
        # Escalar
        features_scaled = self.scaler.transform(features_array)
        
        # Predecir
        prob = float(self.model.predict(features_scaled, verbose=0)[0][0])
        prediction = int(prob >= self.threshold)
        
        # Construir resultado
        return {
            'prediction': 'Dislexia' if prediction == 1 else 'No Dislexia',
            'probability': round(prob, 4),
            'confidence': self._calculate_confidence(prob),
            'risk_level': self._categorize_risk(prob),
            'recommendation': self._get_recommendation(prob),
            'disclaimer': 'Esta es una evaluación preliminar de screening. '
                         'No constituye un diagnóstico médico. '
                         'Se recomienda consulta con profesional especializado.'
        }
    
    def _validate_input(self, session_data):
        """Valida que los datos de entrada sean correctos"""
        required_keys = ['age', 'gender', 'native_language', 'has_other_languages', 'exercises']
        for key in required_keys:
            if key not in session_data:
                raise ValueError(f"Falta clave requerida: {key}")
        
        if not isinstance(session_data['exercises'], dict):
            raise ValueError("'exercises' debe ser un diccionario")
        
        # Validar que existan los 32 ejercicios
        expected_exercises = set(range(1, 33))
        provided_exercises = set(session_data['exercises'].keys())
        
        missing = expected_exercises - provided_exercises
        if missing:
            raise ValueError(f"Faltan ejercicios: {sorted(missing)}")
    
    def _prepare_features(self, session_data):
        """Prepara el diccionario de features para el modelo"""
        feature_dict = {}
        
        # 1. DEMOGRÁFICAS
        feature_dict['Age'] = session_data['age']
        feature_dict['Gender_Male'] = 1 if session_data['gender'] == 'Male' else 0
        feature_dict['Nativelang_Yes'] = 1 if session_data['native_language'] == 'Yes' else 0
        feature_dict['Otherlang_Yes'] = 1 if session_data['has_other_languages'] == 'Yes' else 0
        
        # 2. EJERCICIOS (1-32)
        metricas = ['Clicks', 'Hits', 'Misses', 'Score', 'Accuracy', 'Missrate']
        
        for ejercicio_num in range(1, 33):
            if ejercicio_num in session_data['exercises']:
                exercise_data = session_data['exercises'][ejercicio_num]
                
                for metrica in metricas:
                    feature_name = f"{metrica}{ejercicio_num}"
                    metrica_lower = metrica.lower()
                    
                    if metrica_lower in exercise_data:
                        feature_dict[feature_name] = exercise_data[metrica_lower]
                    else:
                        # Si falta la métrica, usar 0 como fallback
                        feature_dict[feature_name] = 0
        
        return feature_dict
    
    def _calculate_confidence(self, prob):
        """Calcula nivel de confianza basado en distancia al umbral"""
        distance = abs(prob - self.threshold)
        
        if distance < 0.05:
            return 'BAJA'
        elif distance < 0.15:
            return 'MEDIA'
        else:
            return 'ALTA'
    
    def _categorize_risk(self, prob):
        """Categoriza nivel de riesgo"""
        if prob < 0.3:
            return 'BAJO'
        elif prob < 0.6:
            return 'MEDIO'
        else:
            return 'ALTO'
    
    def _get_recommendation(self, prob):
        """Genera recomendación según probabilidad"""
        if prob >= 0.7:
            return ('Se recomienda evaluación profesional inmediata con psicopedagogo '
                   'o especialista en dificultades de aprendizaje.')
        elif prob >= 0.5:
            return ('Se sugiere monitoreo continuo y actividades de refuerzo en '
                   'lectoescritura. Considerar evaluación profesional.')
        else:
            return ('Continuar con actividades de estimulación regulares. '
                   'Mantener seguimiento del desarrollo académico.')


# Instancia global del predictor (se carga una sola vez)
predictor = DyslexiaPredictor()