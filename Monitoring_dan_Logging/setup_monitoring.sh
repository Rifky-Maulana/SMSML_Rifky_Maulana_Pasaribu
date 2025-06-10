#!/bin/bash

echo "Setting up MLOps Monitoring Pipeline..."

# Install required packages
echo "Installing required packages..."
pip install prometheus-client psutil requests

# Start Prometheus and Grafana
echo "Starting Prometheus and Grafana..."
docker-compose up -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 10

# Check if services are running
echo "Checking services..."
curl -s http://localhost:9090 > /dev/null && echo "✓ Prometheus is running on http://localhost:9090" || echo "✗ Prometheus failed to start"
curl -s http://localhost:3000 > /dev/null && echo "✓ Grafana is running on http://localhost:3000" || echo "✗ Grafana failed to start"

echo ""
echo "Next steps:"
echo "1. Start MLflow model server: mlflow models serve -m 'models:/random_forest_penguins/latest' -p 8080"
echo "2. Start metrics exporter: python prometheus_exporter.py"
echo "3. Configure Grafana dashboard at http://localhost:3000 (admin/admin)"
echo "4. Add Prometheus data source: http://prometheus:9090"
echo ""
echo "For monitoring, access:"
echo "- Prometheus: http://localhost:9090"
echo "- Grafana: http://localhost:3000"
echo "- Metrics endpoint: http://localhost:8000/metrics"