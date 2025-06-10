import mlflow
import mlflow.sklearn
from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load model
model_name = "random_forest_penguins"
model_version = "latest"
model = None

def load_model():
    global model
    try:
        model_uri = f"models:/{model_name}/{model_version}"
        model = mlflow.sklearn.load_model(model_uri)
        logger.info(f"Model {model_name} loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return False

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "model_loaded": model is not None})

@app.route('/invocations', methods=['POST'])
def predict():
    try:
        if model is None:
            return jsonify({"error": "Model not loaded"}), 500
        
        data = request.json
        
        # Handle dataframe_split format (MLflow standard)
        if 'dataframe_split' in data:
            df = pd.DataFrame(
                data['dataframe_split']['data'], 
                columns=data['dataframe_split']['columns']
            )
        else:
            df = pd.DataFrame(data)
        
        # Make prediction
        predictions = model.predict(df)
        
        # Convert numpy types to native Python types for JSON serialization
        if isinstance(predictions, np.ndarray):
            predictions = predictions.tolist()
        
        return jsonify({
            "predictions": predictions
        })
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({"error": str(e)}), 400

@app.route('/metrics', methods=['GET'])
def metrics():
    """Basic metrics endpoint for Prometheus"""
    return """# HELP model_health Model health status
# TYPE model_health gauge
model_health{model_name="random_forest_penguins"} 1
# HELP model_predictions_total Total number of predictions made
# TYPE model_predictions_total counter
model_predictions_total 0
"""

if __name__ == '__main__':
    # Set MLflow tracking URI
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns"))
    
    # Load model
    if load_model():
        logger.info("Starting Flask server on port 8080...")
        app.run(host='0.0.0.0', port=8080, debug=False)
    else:
        logger.error("Failed to load model. Exiting...")