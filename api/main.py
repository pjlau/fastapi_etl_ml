import sys
import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.requests import Request
import pandas as pd
from pandas.errors import DatabaseError

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Add api/ directory to sys.path for robust imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
try:
    from db_connect import get_db_connection
except ImportError as e:
    logger.error(f"Error importing db_connect: {e}")
    raise

from models.classifier import predict_cluster

app = FastAPI()
app.mount("/static", StaticFiles(directory="visualization/static"), name="static")
templates = Jinja2Templates(directory="visualization/templates")

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    logger.info("Serving dashboard")
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/data")
async def get_data():
    logger.info("Handling GET /api/data request")
    conn = get_db_connection()
    if conn is None:
        logger.error("Failed to connect to SQLite database")
        raise HTTPException(status_code=500, detail="Failed to connect to SQLite database")
    try:
        df = pd.read_sql("SELECT name, total_spent FROM customers", conn)
        conn.close()
        logger.info(f"Queried {len(df)} rows from customers table")
        if df.empty:
            logger.warning("No data found in customers table")
            return {"names": [], "total_spent": []}
        return {"names": df["name"].tolist(), "total_spent": df["total_spent"].tolist()}
    except DatabaseError as e:
        conn.close()
        logger.error(f"Database error in get_data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Database table 'customers' not found. Ensure ETL pipeline ran successfully.")
    except Exception as e:
        conn.close()
        logger.error(f"Unexpected error in get_data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/api/predict")
async def predict(data: dict):
    logger.info("Handling POST /api/predict request")
    features = data.get("total_spent")
    if not isinstance(features, (int, float)):
        logger.error(f"Invalid total_spent value: {features}")
        raise HTTPException(status_code=400, detail="Invalid total_spent value")
    try:
        cluster = predict_cluster(features)
        logger.info(f"Predicted cluster: {cluster}")
        return {"cluster": cluster}
    except Exception as e:
        logger.error(f"Error in predict: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")