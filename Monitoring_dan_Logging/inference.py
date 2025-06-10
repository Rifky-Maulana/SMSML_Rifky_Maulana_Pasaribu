import requests
import json
import time
import random
from prometheus_client import Counter, Histogram

# Setup metrics
prediction_requests = Counter('inference_requests_total', 'Total inference requests')
inference_duration = Histogram('inference_duration_seconds', 'Inference request duration')

def make_prediction(data):
    """Make prediction to MLflow served model"""
    url = "http://localhost:8080/invocations"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    with inference_duration.time():
        try:
            response = requests.post(url, json=data, headers=headers)
            prediction_requests.inc()
            
            if response.status_code == 200:
                result = response.json()
                print(f"Prediction successful: {result}")
                return result
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error making prediction: {e}")
            return None

def generate_sample_data():
    """Generate sample penguin data for prediction"""
    # Sample data berdasarkan features yang digunakan dalam model
    sample_data = {
        "inputs": [{
            "bill_length_mm": random.uniform(35, 60),
            "bill_depth_mm": random.uniform(13, 22),
            "flipper_length_mm": random.uniform(170, 230),
            "body_mass_g": random.uniform(2700, 6300),
            "island_encoded": random.randint(0, 2),
            "sex_encoded": random.randint(0, 1)
        }]
    }
    return sample_data

def main():
    """Main function untuk testing inference"""
    print("Starting inference testing...")
    print("Make sure MLflow model server is running on port 8080")
    
    # Test dengan beberapa sample data
    for i in range(5):
        print(f"\n--- Test {i+1} ---")
        sample_data = generate_sample_data()
        print(f"Input data: {sample_data}")
        
        result = make_prediction(sample_data)
        
        if result:
            print(f"Prediction result: {result}")
        else:
            print("Prediction failed")
        
        time.sleep(2)  # Wait 2 seconds between requests

if __name__ == "__main__":
    main()