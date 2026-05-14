from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict
import json
import logging
from datetime import datetime

from models.predictor import TextPredictor
from utils.user_adapter import UserAdapter
from utils.corpus import load_corpus

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Textor Predictor Agent",
    description="Agente inteligente de predicción de texto en español",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos de datos
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

class UserStatsResponse(BaseModel):
    user_id: str
    words_learned: int
    total_predictions: int
    accuracy: float
    last_update: str

# Instancias globales
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
    return {
        "message": "Textor Predictor Agent - API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Obtiene predicciones de palabras basadas en el texto ingresado.
    
    Args:
        request: Contiene el texto, user_id y número máximo de sugerencias
    
    Returns:
        PredictionResponse con sugerencias y confianza
    """
    try:
        # Obtener o crear adaptador de usuario
        if request.user_id not in user_adapters:
            user_adapters[request.user_id] = UserAdapter(request.user_id)
        
        adapter = user_adapters[request.user_id]
        
        # Obtener predicciones del modelo
        predictions = predictor.predict(
            text=request.text,
            max_suggestions=request.max_suggestions,
            user_adapter=adapter
        )
        
        # Separar sugerencias y confianza
        suggestions = [p["word"] for p in predictions]
        confidence = [p["confidence"] for p in predictions]
        
        response = PredictionResponse(
            suggestions=suggestions,
            confidence=confidence,
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"Predicción para usuario {request.user_id}: {len(suggestions)} sugerencias")
        return response
        
    except Exception as e:
        logger.error(f"Error en predicción: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/feedback")
async def feedback(request: FeedbackRequest):
    """
    Registra retroalimentación del usuario para mejorar predicciones.
    """
    try:
        if request.user_id not in user_adapters:
            user_adapters[request.user_id] = UserAdapter(request.user_id)
        
        adapter = user_adapters[request.user_id]
        adapter.register_selection(request.text, request.selected)
        
        # El modelo LSTM se reentrenará periódicamente con esta información
        predictor.update_user_preferences(request.user_id, request.selected)
        
        logger.info(f"Feedback registrado para {request.user_id}: '{request.selected}'")
        return {
            "status": "success",
            "message": "Feedback registrado",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error en feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user-stats/{user_id}", response_model=UserStatsResponse)
async def user_stats(user_id: str):
    """
    Obtiene estadísticas de un usuario específico.
    """
    try:
        if user_id not in user_adapters:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        adapter = user_adapters[user_id]
        stats = adapter.get_statistics()
        
        return UserStatsResponse(
            user_id=user_id,
            words_learned=stats["words_learned"],
            total_predictions=stats["total_predictions"],
            accuracy=stats["accuracy"],
            last_update=stats["last_update"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/user/{user_id}")
async def delete_user(user_id: str):
    """
    Elimina datos de un usuario.
    """
    if user_id in user_adapters:
        del user_adapters[user_id]
        logger.info(f"Usuario {user_id} eliminado")
    
    return {"status": "success", "message": f"Usuario {user_id} eliminado"}

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket para predicción en tiempo real (opcional para futuras mejoras).
    """
    await websocket.accept()
    
    if user_id not in user_adapters:
        user_adapters[user_id] = UserAdapter(user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            predictions = predictor.predict(
                text=message.get("text", ""),
                max_suggestions=message.get("max_suggestions", 5),
                user_adapter=user_adapters[user_id]
            )
            
            await websocket.send_json({
                "suggestions": [p["word"] for p in predictions],
                "confidence": [p["confidence"] for p in predictions]
            })
            
    except Exception as e:
        logger.error(f"Error en WebSocket: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)