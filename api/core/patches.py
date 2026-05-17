"""
Monkey-patch for XGBClassifier compatibility issues
"""
import sys

def apply_patches():
    """Apply runtime patches for compatibility issues"""
    
    # Patch smurf_service to use predict_proba instead of decision_function
    try:
        # Force re-import to get fresh module
        if 'api.services.smurf_service' in sys.modules:
            del sys.modules['api.services.smurf_service']
        
        from api.services import smurf_service
        import functools
        import numpy as np
        
        # Store original for reference
        _original_predict = smurf_service.predict_smurf_anomaly
        
        @functools.wraps(_original_predict)
        def predict_smurf_anomaly_patched(features):
            """Patched version that works with XGBClassifier"""
            model, scaler = smurf_service._load_smurf_bundle()
            raw_vector = np.array([[getattr(features, name) for name in smurf_service.SMURF_FEATURE_ORDER]], dtype=float)
            scaled = scaler.transform(raw_vector)
            
            predicted_label = int(model.predict(scaled)[0])
            
            # Use predict_proba instead of non-existent decision_function
            try:
                proba = model.predict_proba(scaled)[0]
                # Get probability of the positive class (anomaly = 1)
                anomaly_score = float(proba[1] if len(proba) > 1 else proba[0])
            except Exception:
                anomaly_score = 0.5
            
            is_smurf_anomaly = predicted_label == 1
            return is_smurf_anomaly, anomaly_score, predicted_label
        
        smurf_service.predict_smurf_anomaly = predict_smurf_anomaly_patched
        print("[RUNTIME PATCH] Applied smurf_service.predict_smurf_anomaly fix")
    except ImportError:
        pass  # Module not yet imported, will be patched on first import
    except Exception as e:
        print(f"[RUNTIME PATCH] Warning: Could not patch smurf_service: {e}")

# Apply patches on import
apply_patches()
