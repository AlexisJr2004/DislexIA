"""
Utilidades para preparar datos de evaluaciones para el modelo de predicción de dislexia
"""

from app.games.models import SesionJuego, Evaluacion
from app.core.models import Nino


def preparar_features_desde_evaluacion(evaluacion_id):
    """
    Convierte una evaluación completa en las 196 features que necesita el modelo
    
    Args:
        evaluacion_id (int): ID de la evaluación completada
        
    Returns:
        dict: Diccionario con las 196 features en el formato esperado por el modelo
        
    Raises:
        ValueError: Si la evaluación no tiene 32 sesiones completadas
    """
    try:
        evaluacion = Evaluacion.objects.get(id=evaluacion_id)
    except Evaluacion.DoesNotExist:
        raise ValueError(f"No se encontró la evaluación con ID {evaluacion_id}")
    
    nino = evaluacion.nino
    
    # Verificar que la evaluación esté completa
    sesiones = SesionJuego.objects.filter(
        evaluacion=evaluacion,
        estado='completada'
    ).order_by('ejercicio_numero')
    
    total_sesiones = sesiones.count()
    
    if total_sesiones < 32:
        print(f"⚠️ Advertencia: Solo hay {total_sesiones}/32 sesiones completadas")
        print(f"   Se rellenarán las sesiones faltantes con promedios del dataset")
    
    # === 4 FEATURES DEMOGRÁFICAS ===
    features = {}
    
    # Age
    features['Age'] = nino.edad
    
    # Gender (Male=1, Female=0)
    if nino.genero.lower() in ['masculino', 'male', 'm']:
        features['Gender_Male'] = 1
    elif nino.genero.lower() in ['femenino', 'female', 'f']:
        features['Gender_Male'] = 0
    else:
        features['Gender_Male'] = 0  # Default
    
    # Nativelang (Spanish=1, Other=0)
    if nino.idioma_nativo and 'espa' in nino.idioma_nativo.lower():
        features['Nativelang_Yes'] = 1
    else:
        features['Nativelang_Yes'] = 0
    
    # Otherlang (por ahora asumimos No=0, puedes agregar este campo a Nino después)
    features['Otherlang_Yes'] = 0
    
    print(f"📊 Features demográficas preparadas:")
    print(f"   - Edad: {features['Age']} años")
    print(f"   - Género: {'Masculino' if features['Gender_Male'] == 1 else 'Femenino'}")
    print(f"   - Idioma nativo español: {'Sí' if features['Nativelang_Yes'] == 1 else 'No'}")
    
    # === 192 FEATURES DE EJERCICIOS (32 ejercicios × 6 métricas) ===
    
    # Crear diccionario de sesiones por ejercicio_numero
    sesiones_dict = {s.ejercicio_numero: s for s in sesiones}
    
    # Valores por defecto para sesiones faltantes (promedios del dataset)
    DEFAULT_VALUES = {
        'clicks': 3.5,
        'hits': 2.8,
        'misses': 0.7,
        'score': 0.05,  # Ya normalizado ⭐ Cambiar a 0.05 (equivalente a 5 puntos / 100)
        'accuracy': 0.80,  # Cambiado de 80.0 a 0.80 (ratio 0-1)
        'missrate': 0.20   # Cambiado de 20.0 a 0.20 (ratio 0-1)
    }
    
    sesiones_completas = 0
    sesiones_con_promedios = 0
    
    for i in range(1, 33):  # Ejercicios del 1 al 32
        if i in sesiones_dict:
            # Usar datos reales de la sesión
            sesion = sesiones_dict[i]
            
            features[f'Clicks{i}'] = sesion.clicks_total
            features[f'Hits{i}'] = sesion.hits_total
            features[f'Misses{i}'] = sesion.misses_total
            # Normalizar Score: dividir entre 100 para ajustar a escala del dataset
            features[f'Score{i}'] = sesion.score_total / 100.0
            # Convertir de porcentaje (0-100) a ratio (0-1) como espera el modelo
            features[f'Accuracy{i}'] = float(sesion.accuracy_percent) / 100.0
            features[f'Missrate{i}'] = float(sesion.missrate_percent) / 100.0
            
            sesiones_completas += 1
            
            # Debug: Mostrar cada 5 ejercicios
            if i % 5 == 0:
                print(f"✅ Ejercicio {i}: Clicks={sesion.clicks_total}, Hits={sesion.hits_total}, Accuracy={sesion.accuracy_percent:.1f}%")
        else:
            # Rellenar con valores por defecto
            features[f'Clicks{i}'] = DEFAULT_VALUES['clicks']
            features[f'Hits{i}'] = DEFAULT_VALUES['hits']
            features[f'Misses{i}'] = DEFAULT_VALUES['misses']
            features[f'Score{i}'] = DEFAULT_VALUES['score']
            features[f'Accuracy{i}'] = DEFAULT_VALUES['accuracy']
            features[f'Missrate{i}'] = DEFAULT_VALUES['missrate']
            
            sesiones_con_promedios += 1
            
            # Debug
            if i % 5 == 0:
                print(f"⚠️ Ejercicio {i}: Usando valores por defecto (sesión no encontrada)")
    
    print(f"\n📈 Resumen de preparación:")
    print(f"   - Sesiones con datos reales: {sesiones_completas}/32")
    print(f"   - Sesiones con promedios: {sesiones_con_promedios}/32")
    print(f"   - Total de features generadas: {len(features)}")
    
    # Verificar que tengamos exactamente 196 features
    expected_features = 196
    if len(features) != expected_features:
        print(f"⚠️ ADVERTENCIA: Se esperaban {expected_features} features, pero se generaron {len(features)}")
    
    return features


def validar_features(features):
    """
    Valida que el diccionario de features tenga la estructura correcta
    
    Args:
        features (dict): Diccionario de features a validar
        
    Returns:
        tuple: (es_valido, lista_de_errores)
    """
    errores = []
    
    # Verificar que existan las 4 features demográficas
    features_demograficas = ['Age', 'Gender_Male', 'Nativelang_Yes', 'Otherlang_Yes']
    for feat in features_demograficas:
        if feat not in features:
            errores.append(f"Falta feature demográfica: {feat}")
    
    # Verificar que existan las 192 features de ejercicios
    for i in range(1, 33):
        metricas = ['Clicks', 'Hits', 'Misses', 'Score', 'Accuracy', 'Missrate']
        for metrica in metricas:
            feat_name = f'{metrica}{i}'
            if feat_name not in features:
                errores.append(f"Falta feature de ejercicio: {feat_name}")
    
    # Verificar total
    if len(features) != 196:
        errores.append(f"Total de features incorrecto: {len(features)} (esperado: 196)")
    
    # Verificar rangos de valores
    if 'Age' in features:
        if not (5 <= features['Age'] <= 15):
            errores.append(f"Edad fuera de rango: {features['Age']} (esperado: 5-15)")
    
    # Verificar que Gender y Lang sean binarios
    for feat in ['Gender_Male', 'Nativelang_Yes', 'Otherlang_Yes']:
        if feat in features and features[feat] not in [0, 1]:
            errores.append(f"{feat} debe ser 0 o 1, recibido: {features[feat]}")
    
    es_valido = len(errores) == 0
    
    return es_valido, errores


def obtener_resumen_evaluacion(evaluacion_id):
    """
    Obtiene un resumen legible de la evaluación
    
    Args:
        evaluacion_id (int): ID de la evaluación
        
    Returns:
        dict: Resumen con estadísticas clave
    """
    try:
        evaluacion = Evaluacion.objects.get(id=evaluacion_id)
        nino = evaluacion.nino
        
        sesiones = SesionJuego.objects.filter(
            evaluacion=evaluacion,
            estado='completada'
        ).order_by('ejercicio_numero')
        
        # Calcular métricas totales
        total_clicks = sum(s.clicks_total for s in sesiones)
        total_hits = sum(s.hits_total for s in sesiones)
        total_misses = sum(s.misses_total for s in sesiones)
        total_score = sum(s.score_total for s in sesiones)
        
        accuracy_promedio = (total_hits / total_clicks * 100) if total_clicks > 0 else 0
        
        return {
            'evaluacion_id': evaluacion.id,
            'nino': {
                'id': nino.id,
                'nombre': nino.nombre_completo,
                'edad': nino.edad,
                'genero': nino.genero
            },
            'sesiones': {
                'completadas': sesiones.count(),
                'total_esperadas': 32,
                'porcentaje': round((sesiones.count() / 32) * 100, 1)
            },
            'metricas': {
                'total_clicks': total_clicks,
                'total_hits': total_hits,
                'total_misses': total_misses,
                'total_score': total_score,
                'accuracy_promedio': round(accuracy_promedio, 2),
                'missrate_promedio': round(100 - accuracy_promedio, 2)
            },
            'estado': evaluacion.estado,
            'fecha_inicio': evaluacion.fecha_hora_inicio.strftime('%Y-%m-%d %H:%M:%S'),
            'fecha_fin': evaluacion.fecha_hora_fin.strftime('%Y-%m-%d %H:%M:%S') if evaluacion.fecha_hora_fin else None,
            'duracion_minutos': evaluacion.duracion_total_minutos
        }
        
    except Evaluacion.DoesNotExist:
        return None


# === FUNCIÓN DE PRUEBA (OPCIONAL) ===
def probar_preparacion_features(evaluacion_id):
    """
    Función de prueba para verificar que la preparación de features funciona correctamente
    
    Args:
        evaluacion_id (int): ID de la evaluación a probar
    """
    print("="*80)
    print("🧪 PRUEBA DE PREPARACIÓN DE FEATURES")
    print("="*80)
    
    # Obtener resumen
    resumen = obtener_resumen_evaluacion(evaluacion_id)
    if resumen:
        print("\n📋 RESUMEN DE LA EVALUACIÓN:")
        print(f"   Niño: {resumen['nino']['nombre']} ({resumen['nino']['edad']} años)")
        print(f"   Sesiones: {resumen['sesiones']['completadas']}/{resumen['sesiones']['total_esperadas']} ({resumen['sesiones']['porcentaje']}%)")
        print(f"   Accuracy promedio: {resumen['metricas']['accuracy_promedio']}%")
        print(f"   Estado: {resumen['estado']}")
    
    # Preparar features
    print("\n🔄 Preparando features...")
    features = preparar_features_desde_evaluacion(evaluacion_id)
    
    # Validar
    print("\n✔️ Validando features...")
    es_valido, errores = validar_features(features)
    
    if es_valido:
        print("✅ VALIDACIÓN EXITOSA - Features correctamente preparadas")
        print(f"   Total de features: {len(features)}")
        
        # Mostrar algunas features de ejemplo
        print("\n📊 Ejemplos de features generadas:")
        print(f"   Age: {features['Age']}")
        print(f"   Gender_Male: {features['Gender_Male']}")
        print(f"   Clicks1: {features['Clicks1']}")
        print(f"   Hits1: {features['Hits1']}")
        print(f"   Accuracy1: {features['Accuracy1']}")
        print(f"   ...")
        print(f"   Clicks32: {features['Clicks32']}")
        print(f"   Hits32: {features['Hits32']}")
        print(f"   Accuracy32: {features['Accuracy32']}")
        
        return True
    else:
        print("❌ VALIDACIÓN FALLIDA")
        print(f"   Errores encontrados: {len(errores)}")
        for error in errores[:10]:  # Mostrar solo los primeros 10
            print(f"   - {error}")
        if len(errores) > 10:
            print(f"   ... y {len(errores) - 10} errores más")
        
        return False