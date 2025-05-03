# ETL, Visualization, and API Demo with Pandas, SQLite, and scikit-learn

This repository showcases a data pipeline using **Pandas** for ETL, **SQLite** for data storage, **Apache ECharts** for visualization, **FastAPI** for the backend, and **scikit-learn** for clustering.

## Setup
1. Clone the repo:
   ```bash
   git clone https://github.com/pjlau/fastapi_etl_ml
   cd fastapi_etl_ml
2. Install dependencies: `pip install -r api/requirements.txt`
3. Run the ETL pipeline: `python data/scripts/etl_pipeline.py`
4. Train the clustering model: `python api/models/classifier.py`
5. Start the FastAPI server: `uvicorn api.main:app --host 0.0.0.0 --port 8000`
6. Access the dashboard at `http://localhost:8000`


## Components
- **Pandas ETL**: `data/scripts/etl_pipeline.py` creates a temporary SQLite table, transforms data, and loads it into a permanent table.
- **SQLite**: Stores processed data (`data/database.db`).
- **Apache ECharts**: Interactive visualizations (`visualization/static/js/charts.js`).
- **FastAPI**: Serves data and predictions (`api/main.py`).
- **scikit-learn**: K-Means clustering model (`api/models/classifier.py`).

## Running the ETL Pipeline
- The ETL pipeline runs automatically during the Docker build (`RUN python data/scripts/etl_pipeline.py`), creating a temporary SQLite table with sample data.
- Locally: `python data/scripts/etl_pipeline.py`

## Training the Clustering Model
- Run `python api/models/classifier.py` after the ETL pipeline generates `data/processed/customers_processed.csv`.
- In Docker: `docker-compose exec api python api/models/classifier.py`

## Notes
- The ETL pipeline uses a temporary SQLite table with sample data, eliminating the need for external CSV files.
- The dashboard displays a bar chart of customer spending, and the API supports clustering predictions.
