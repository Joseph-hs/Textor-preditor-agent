from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import json
import logging
from datetime import datetime

from models.predictor import TextPredictor
from utils.user_adapter import UserAdapter
from utils.corpus import load_corpus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Textor Predictor Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictionRequest(BaseModel):
    text: str
    user_id: str
    max_suggestions: int = 5

class PredictionResponse(BaseModel):
    suggestions: List[str]
    confidence: List[float]
    timestamp: str

class FeedbackRequest(BaseModel):
    text: str
    selected: str
    user_id: str

predictor = None
user_adapters = {}
corpus = None

@app.on_event("startup")
async def startup_event():
    global predictor, corpus
    logger.info("Iniciando Textor Predictor Agent...")
    corpus = load_corpus()
    logger.info(f"Corpus cargado: {len(corpus)} palabras")
    predictor = TextPredictor(corpus)
    logger.info("Modelo predictor inicializado")

@app.get("/")
async def root():
    return {"message": "Textor Predictor Agent - API", "version": "1.0.0", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    try:
        if request.user_id not in user_adapters:
            user_adapters[request.user_id] = UserAdapter(request.user_id)
        adapter = user_adapters[request.user_id]
        predictions = predictor.predict(text=request.text, max_suggestions=request.max_suggestions, user_adapter=adapter)
        suggestions = [p["word"] for p in predictions]
        confidence = [p["confidence"] for p in predictions]
        return PredictionResponse(suggestions=suggestions, confidence=confidence, timestamp=datetime.now().isoformat())
    except Exception as e:
        logger.error(f"Error en prediccion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/feedback")
async def feedback(request: FeedbackRequest):
    try:
        if request.user_id not in user_adapters:
            user_adapters[request.user_id] = UserAdapter(request.user_id)
        adapter = user_adapters[request.user_id]
        adapter.register_selection(request.text, request.selected)
        predictor.update_user_preferences(request.user_id, request.selected)
        logger.info(f"Feedback registrado para {request.user_id}")
        return {"status": "success", "message": "Feedback registrado", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Error en feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user-stats/{user_id}")
async def user_stats(user_id: str):
    try:
        if user_id not in user_adapters:
            user_adapters[user_id] = UserAdapter(user_id)
        adapter = user_adapters[user_id]
        stats = adapter.get_statistics()
        return {"user_id": user_id, "words_learned": stats["words_learned"], "total_predictions": stats["total_predictions"], "accuracy": stats["accuracy"], "last_update": stats["last_update"]}
    except Exception as e:
        logger.error(f"Error obteniendo estadisticas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)