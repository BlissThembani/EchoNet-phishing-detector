"""Inference API for the web page phishing classifier."""
import os
import secrets

from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader

from app.inference import FEATURES, predict
from app.schemas import Prediction, WebPageFeatures

app = FastAPI(title="Web Page Phishing Detection")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(key: str | None = Security(api_key_header)):
    """Only callers holding ML_API_KEY (the n8n workflow) may run predictions."""
    expected = os.environ.get("ML_API_KEY")
    if not expected:
        raise HTTPException(status_code=503, detail="ML_API_KEY is not configured")
    if not key or not secrets.compare_digest(key, expected):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.get("/")
def health():
    return {"status": "ok", "features": FEATURES}


@app.post("/predict", response_model=Prediction, dependencies=[Depends(require_api_key)])
def predict_one(features: WebPageFeatures):
    return predict([features.model_dump()])[0]


@app.post("/predict/batch", response_model=list[Prediction], dependencies=[Depends(require_api_key)])
def predict_batch(items: list[WebPageFeatures]):
    return predict([item.model_dump() for item in items])
