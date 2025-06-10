# Serving model dengan MLflow
mlflow models serve -m "models:/random_forest_penguins/latest" -p 8080 --host 0.0.0.0
