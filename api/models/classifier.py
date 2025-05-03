import pandas as pd
import os
import logging
from sklearn.cluster import KMeans
import joblib

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def train_clustering_model(n_clusters=2):
    """Train a K-Means clustering model using sklearn."""
    try:
        input_file = os.path.join("data", "processed", "customers_processed.csv")
        processed_dir = os.path.join("data", "processed")
        if not os.path.exists(processed_dir):
            logger.error(f"Directory {processed_dir} does not exist. Run ETL pipeline to create it.")
            raise FileNotFoundError(f"Directory {processed_dir} does not exist. Run ETL pipeline first.")
        if not os.path.exists(input_file):
            logger.error(f"File {input_file} not found. Run ETL pipeline to generate it.")
            raise FileNotFoundError(f"File {input_file} not found. Run ETL pipeline first.")
        
        df = pd.read_csv(input_file)
        if df.empty:
            logger.error(f"File {input_file} is empty.")
            raise ValueError(f"File {input_file} is empty.")
        if "total_spent" not in df.columns:
            logger.error(f"File {input_file} missing required column: total_spent")
            raise ValueError(f"File {input_file} missing required column: total_spent")
        
        X = df[["total_spent"]].values
        
        model = KMeans(n_clusters=n_clusters, random_state=42)
        model.fit(X)
        
        output_file = os.path.join("api", "models", "cluster_model.pkl")
        joblib.dump(model, output_file)
        logger.info(f"K-Means model trained and saved as {output_file}")
        
        df["cluster"] = model.labels_
        df.to_csv(input_file, index=False)
        logger.info(f"Updated {input_file} with cluster labels")
    except Exception as e:
        logger.error(f"Error in train_clustering_model: {e}")
        raise

def predict_cluster(features):
    """Predict cluster for given features."""
    try:
        model_file = os.path.join("api", "models", "cluster_model.pkl")
        model = joblib.load(model_file)
        prediction = model.predict([[features]])
        logger.info(f"Predicted cluster: {prediction[0]}")
        return int(prediction[0])
    except Exception as e:
        logger.error(f"Error in predict_cluster: {e}")
        raise

if __name__ == "__main__":
    train_clustering_model()