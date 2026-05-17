"""Patch to fix smurf_service.py decision_function issue"""

import sys
from pathlib import Path

# Monkey-patch the smurf_service module
def patch_smurf_service():
    try:
        from api.services import smurf_service
        import functools
        import numpy as np
        
        # Get original function
        _original_predict = smurf_service.predict_smurf_anomaly
        
        # Create wrapper that fixes the issue
        @functools.wraps(_original_predict)
        def predict_smurf_anomaly_fixed(features):
            model, scaler = smurf_service._load_smurf_bundle()
            raw_vector = np.array([[getattr(features, name) for name in smurf_service.SMURF_FEATURE_ORDER]], dtype=float)
            scaled = scaler.transform(raw_vector)
            
            predicted_label = int(model.predict(scaled)[0])
            
            # Use predict_proba instead of decision_function
            try:
                proba = model.predict_proba(scaled)[0]
                anomaly_score = float(proba[1] if len(proba) > 1 else proba[0])
            except:
                anomaly_score = 0.5
            
            is_smurf_anomaly = predicted_label == 1
            
            return is_smurf_anomaly, anomaly_score, predicted_label
        
        # Replace function
        smurf_service.predict_smurf_anomaly = predict_smurf_anomaly_fixed
        print("[PATCH] Fixed smurf_service.predict_smurf_anomaly")
        return True
    except Exception as e:
        print(f"[PATCH] Error patching smurf_service: {e}")
        return False

if __name__ == "__main__":
    patch_smurf_service()
