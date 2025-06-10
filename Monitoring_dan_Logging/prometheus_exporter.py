import time
import requests
import psutil
import logging
from prometheus_client import start_http_server, Gauge, Counter, Histogram
import threading

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
model_predictions_total = Counter('model_predictions_total', 'Total number of model predictions')
model_prediction_latency = Histogram('model_prediction_latency_seconds', 'Model prediction latency')
model_health_status = Gauge('model_health_status', 'Model server health status (1=healthy, 0=unhealthy)')
system_cpu_usage = Gauge('system_cpu_usage_percent', 'System CPU usage percentage')
system_memory_usage = Gauge('system_memory_usage_percent', 'System memory usage percentage')
system_disk_usage = Gauge('system_disk_usage_percent', 'System disk usage percentage')

class ModelMonitor:
    def __init__(self, model_url="http://localhost:8080"):
        self.model_url = model_url
        self.is_running = True
        
    def collect_system_metrics(self):
        """Collect system metrics"""
        while self.is_running:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                system_cpu_usage.set(cpu_percent)
                
                # Memory usage
                memory = psutil.virtual_memory()
                system_memory_usage.set(memory.percent)
                
                # Disk usage (Windows compatible)
                try:
                    disk = psutil.disk_usage('C:')  # Windows
                except:
                    disk = psutil.disk_usage('/')   # Linux/Mac
                disk_percent = (disk.used / disk.total) * 100
                system_disk_usage.set(disk_percent)
                
                logger.info(f"System metrics - CPU: {cpu_percent}%, Memory: {memory.percent}%, Disk: {disk_percent:.1f}%")
                
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
            
            time.sleep(10)
    
    def check_model_health(self):
        """Check model server health"""
        try:
            response = requests.get(f"{self.model_url}/health", timeout=5)
            if response.status_code == 200:
                model_health_status.set(1)
                return True
            else:
                model_health_status.set(0)
                return False
        except:
            model_health_status.set(0)
            return False
    
    def test_model_endpoint(self):
        """Test model endpoint and collect metrics"""
        while self.is_running:
            try:
                # Check health first
                if not self.check_model_health():
                    logger.warning("Model server is not healthy")
                    time.sleep(30)
                    continue
                
                # Sample data for testing
                test_data = {
                    "dataframe_split": {
                        "columns": ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", 
                                  "body_mass_g", "island_encoded", "sex_encoded"],
                        "data": [[39.1, 18.7, 181.0, 3750.0, 0, 1]]
                    }
                }
                
                start_time = time.time()
                
                response = requests.post(
                    f"{self.model_url}/invocations",
                    json=test_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                
                end_time = time.time()
                latency = end_time - start_time
                
                if response.status_code == 200:
                    model_predictions_total.inc()
                    model_prediction_latency.observe(latency)
                    logger.info(f"Model prediction successful - Latency: {latency:.3f}s")
                else:
                    logger.warning(f"Model prediction failed - Status: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Error testing model endpoint: {e}")
                model_health_status.set(0)
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
            
            time.sleep(30)  # Test every 30 seconds
    
    def start_monitoring(self):
        """Start monitoring threads"""
        logger.info("Starting model monitoring...")
        
        # Start system metrics collection thread
        system_thread = threading.Thread(target=self.collect_system_metrics)
        system_thread.daemon = True
        system_thread.start()
        
        # Start model testing thread
        model_thread = threading.Thread(target=self.test_model_endpoint)
        model_thread.daemon = True
        model_thread.start()
        
        return system_thread, model_thread

def main():
    # Start Prometheus metrics server
    start_http_server(8000)
    logger.info("Prometheus metrics server started on port 8000")
    logger.info("Access metrics at: http://localhost:8000/metrics")
    
    # Initialize monitor
    monitor = ModelMonitor()
    
    # Start monitoring
    monitor.start_monitoring()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down monitor...")
        monitor.is_running = False

if __name__ == "__main__":
    main()