# Textor Predictor Agent 

Un agente inteligente de predicción de texto en español que emplea una estrategia **híbrida multinivel** para brindar sugerencias precisas, rápidas y personalizadas. Diseñado específicamente para textos en español, adaptándose dinámicamente al estilo del usuario.

##  Visión General

**Textor Predictor** es una aplicación full-stack que predice la siguiente palabra mientras el usuario escribe, utilizando una arquitectura que combina tres modelos de machine learning con diferentes características:

```
Usuario escribe → Procesamiento → Predicción Híbrida → Sugerencias personalizadas
```

---

## Arquitectura General

### Stack Tecnológico

| Componente | Tecnología | Razón |
|-----------|-----------|-------|
| **Backend** | FastAPI (Python) | Async, rápido, tipos de datos nativos |
| **Frontend** | React + Vite | UI responsiva, actualizaciones en tiempo real |
| **ML** | Modelos custom (N-gramas, LSTM, Trie) | Control total, bajo overhead |
| **Deployment** | Docker Compose | Reproducibilidad, desarrollo consistent |

### Estructura del Proyecto

```
Textor-preditor-agent/
├── backend/
│   ├── app.py                 # FastAPI principal
│   ├── models/
│   │   ├── predictor.py       # Orquestador híbrido
│   │   ├── ngrams.py          # Modelo N-gramas
│   │   └── lstm_model.py      # Modelo LSTM
│   ├── utils/
│   │   ├── user_adapter.py    # Personalización de usuario
│   │   ├── trie.py            # Estructura Trie
│   │   ├── tokenizer.py       # Tokenización en español
│   │   └── corpus.py          # Carga de datos
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   └── styles/            # Diseño visual
│   └── Dockerfile
└── docker-compose.yml         # Orquestación de servicios
```

---

##  El Modelo Híbrido: La Decisión Clave

### ¿Por qué un enfoque híbrido y no un solo modelo?

La tarea de predicción de texto tiene **tres requisitos conflictivos**:

| Requisito | Trie | N-gramas | LSTM |
|-----------|------|----------|------|
| **Velocidad** | Excelente | Excelente | (lenta) |
| **Autocompletado** | Excelente |  Pobre |  No aplica |
| **Contexto Semántico** |  Nulo |  Limitado (3-5 palabras) |  Profundo |
| **Precisión General** |  Depende corpus |  Buena |  Muy buena |
| **Recursos** |  Mínimos |  Bajos |  Altos |

### Nuestra Solución: Ensemble Ponderado

En lugar de elegir un modelo, **combinamos los tres** con pesos inteligentes:

```python
# De models/predictor.py (líneas 70-110)

# 1️ TRIE: Autocompletado rápido (confianza: 0.7)
if last_token:
    trie_completions = self.trie.search_prefix(last_token)
    for word in trie_completions[:max_suggestions]:
        predictions[word] = {
            "word": word,
            "confidence": 0.7,  # Alto porque es muy específico
            "source": "trie"
        }

# 2️ N-GRAMAS: Patrón lingüístico (combina con peso 1.0)
ngram_predictions = self.ngram_model.predict_next(
    tokens[-3:],  # Últimas 3 palabras (trigrama)
    k=max_suggestions
)
# ... merge con promedio simple (50-50)

# 3️ LSTM: Contexto profundo (combina con peso 0.6)
lstm_predictions = self.lstm_model.predict_next(tokens, k=max_suggestions)
# ... merge con ponderación: 0.4 * anterior + 0.6 * LSTM
predictions[word]["confidence"] = \
    (predictions[word]["confidence"] * 0.4 + float(prob) * 0.6)
```

**¿Por qué estos pesos específicos?**

- **Trie (0.7)**: Rápido y preciso para completaciones directas, pero no entiende contexto
- **N-gramas (1.0)**: Captura patrones reales del corpus sin overhead computacional
- **LSTM (0.6)**: Recibe mayor peso porque entiende dependencias a largo plazo, pero es más computacionalmente costoso

---

##  Los Tres Modelos Explicados

### 1. **TRIE (Prefijo-árbol)**  - Velocidad e Inmediatez

```python
# De utils/trie.py - Búsqueda por prefijo
self.trie.search_prefix("gat")  
# Retorna: ["gato", "gatito", "gata", "gatería"]
```

#### ¿Cómo funciona?

Un Trie es una estructura de árbol donde cada nodo representa una letra:

```
         raíz
        /  |  \
       g   h   a
       |   |   |
       a   o   t
       |       |
       t    (terminal)
       |
       o (terminal)
```

#### Ventajas:
-  Búsqueda O(m) donde m es la longitud del prefijo
-  Perfecto para autocompletado
-  Sin overhead de ML

#### Limitaciones:
-  No entiende contexto ("gat" podría ser "gatillo" o "gato")
-  No aprende del corpus, solo estructura

#### Caso de uso en nuestra app:
```
Usuario escribe: "El g"
Trie responde inmediatamente: ["gato", "gente", "gobierno", "gala"]
```

---

### 2. **N-GRAMAS (Cadenas de Markov)**  - Patrón Lingüístico

```python
# De models/ngrams.py - Trigramas (3 palabras)
context = ["El", "gato"]
# Busca en corpus: "El gato ___"
# Predice: "maulló" (si es frecuente), "come", "duerme"
```

#### ¿Cómo funciona?

Los N-gramas construyen una tabla de probabilidades basada en frecuencias:

```
Trigrama: ("El", "gato", ???)
    ├─ "maulló" → 45% (45 veces en corpus)
    ├─ "come" → 25% (25 veces)
    ├─ "duerme" → 15% (15 veces)
    └─ "salta" → 15% (15 veces)
```

#### Ventajas:
-  Captura patrones reales del lenguaje español
-  Rápido (búsqueda en diccionario O(1))
-  No requiere entrenamiento ML pesado
-  Interpretable (puedes ver por qué predice algo)

#### Limitaciones:
-  Solo mira últimas 3 palabras (no contexto largo)
-  Si nunca ve "El gato X" en corpus, falla
-  No entiende significado

#### Implementación clave:

```python
def train(self, words: List[str]):
    padded_words = ["<START>"] * 2 + words + ["<END>"]
    
    # Crear todos los trigramas
    for i in range(len(padded_words) - 3 + 1):
        context = tuple(padded_words[i:i+2])  # ("El", "gato")
        next_word = padded_words[i+2]         # "maulló"
        self.ngrams[context][next_word] += 1  # Contar frecuencia
```

#### Caso de uso en nuestra app:
```
Usuario escribe: "El gato maulló y el"
N-grama mira: ["maulló", "y", "el"]
Predice (frecuencia en corpus español): ["perro", "gato", "ratón"]
```

---

### 3. **LSTM (Red Neuronal Recurrente)**  - Contexto Profundo

```python
# De models/lstm_model.py - Secuencias largas
tokens = ["El", "gato", "de", "mi", "vecina", "..."]
# LSTM procesa TODA la secuencia
# Entiende: "el gato" + contexto lejano = mejores predicciones
```

#### ¿Cómo funciona?

Una LSTM (Long Short-Term Memory) es una red neuronal que:
1. **Procesa secuencia completa** (no solo últimas 3 palabras)
2. **Mantiene "memoria"** de información importante (gates)
3. **Olvida** información irrelevante

```
Input: [El, gato, de, mi, vecina, que, es, muy]
         ↓
    [embedding layer]
         ↓
    [LSTM cell] → [LSTM cell] → [LSTM cell] → ... (recurrencia)
                        ↓
                   (hidden state: memoria contextual)
         ↓
    [output layer]
         ↓
    Predicción: ["blanca", "linda", "mala", ...]
```

#### Ventajas:
-  Entiende dependencias a largo plazo
-  Captura semántica ("vecina" → género femenino)
-  Mejor precisión con contexto complejo
-  Aprende patrones implícitos del español

#### Limitaciones:
-  Más lenta (forward pass O(n))
-  Requiere computación (GPU ideal)
-  Menos interpretable ("caja negra")
-  Requiere más datos de entrenamiento

#### Arquitectura en nuestro código:

```python
class LSTMModel:
    def __init__(self, vocab_size: int = 500, embedding_dim: int = 128):
        # vocab_size: 500 palabras más frecuentes
        # embedding_dim: Cada palabra = vector de 128 dimensiones
        
        self.embedding = Embedding(vocab_size, embedding_dim)
        self.lstm = LSTM(embedding_dim, hidden_size=256)
        self.dense = Dense(vocab_size, activation='softmax')
```

#### Caso de uso en nuestra app:
```
Usuario escribe: "La política de privacidad de nuestra empresa..."
LSTM lee TODO esto y predice: ["es", "será", "está", "está",...]
(vs N-grama que solo vería últimas 3 palabras)
```

---

##  Flujo de Predicción Paso a Paso

### Cuando el usuario escribe "El gat":

```
┌─────────────────────────────────────────────────────┐
│ 1. ENTRADA: "El gat"                               │
│    Usuario sigue escribiendo en tiempo real         │
└─────────────────────────────┬───────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────┐
│ 2. PREPROCESAMIENTO (utils/preprocessing.py)       │
│    - clean_text("El gat") → "el gat"              │
│    - Minúsculas, elimina puntuación               │
└─────────────────────────────┬───────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────┐
│ 3. TOKENIZACIÓN (utils/tokenizer.py)               │
│    - Separar en tokens: ["el", "gat"]             │
│    - Aplicar reglas de español (tildes, contracciones)
└─────────────────────────────┬───────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────┐
│ 4. PREDICCIÓN HÍBRIDA (models/predictor.py)        │
│                                                     │
│ 4a. TRIE - Autocompletado prefijo "gat"           │
│     ↓                                              │
│     Encuentra: ["gato", "gatito", "gatería"]      │
│     Confianza: 0.7                                │
│                                                     │
│ 4b. N-GRAMAS - Contexto últimas 3 palabras        │
│     Tokens: ["?", "el", "gat"]                    │
│     Busca en tabla: (?, "el", "gat")              │
│     Si no existe → retorna palabras frecuentes    │
│     Confianza: variable (0.3-0.9)                 │
│                                                     │
│ 4c. LSTM - Contexto completo                      │
���     Input: ["el", "gat"]                          │
│     Procesa con red neuronal                      │
│     Output: distribución de probabilidades        │
│     Confianza: variable (0.2-0.95)                │
│                                                     │
│ 4d. FUSIÓN DE RESULTADOS                          │
│     Combina los 3 modelos con pesos:              │
│     - Si aparece en TRIE: base 0.7                │
│     - Suma N-grama (promedio simple)              │
│     - Combina LSTM (pesa 60%)                     │
│                                                     │
│     Resultado final: {"gato": 0.82, "gatito": 0.71}
└─────────────────────────────┬───────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────┐
│ 5. PERSONALIZACIÓN (utils/user_adapter.py)        │
│                                                     │
│    if usuario_id en historial:                     │
│        - Si usuario usa frecuente "gatito" → +20% │
│        - Reajustar confianzas según preferencias  │
│                                                     │
│    Ejemplo: {"gatito": 0.85, "gato": 0.72}        │
└─────────────────────────────┬───────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────┐
│ 6. RANKING Y LIMITACIÓN                            │
│                                                     │
│    - Ordenar por confianza DESC                   │
│    - Tomar top 5                                  │
│                                                     │
│    RESPUESTA FINAL:                               │
│    [                                              │
│      {word: "gatito", confidence: 0.85},          │
│      {word: "gato", confidence: 0.72},            │
│      {word: "gatería", confidence: 0.61},         │
│      ...                                          │
│    ]                                              │
└─────────────────────────────┬───────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────┐
│ 7. FRONTEND MUESTRA LAS SUGERENCIAS                │
│                                                     │
│    Usuario ve:                                     │
│    [ gatito 85% ] [ gato 72% ] [ gatería 61% ]   │
│                                                     │
│    Hace click en "gatito"                          │
│    Texto actualizado: "El gatito"                  │
└─────────────────────────────────────────────────────┘
```

---

##  Adaptación de Usuario (UserAdapter)

### ¿Por qué es crucial?

No todos escriben igual. El sistema debe **aprender el estilo personal**:

```python
# De utils/user_adapter.py

class UserAdapter:
    def __init__(self, user_id: str):
        self.word_frequency = {}      # {palabra: frecuencia}
        self.selection_history = []   # Historial de selecciones
        self.total_predictions = 0
        self.correct_selections = 0
        self.last_update = datetime.now()
    
    def register_selection(self, context: str, selected_word: str):
        """Cuando usuario elige una sugerencia"""
        self.word_frequency[selected_word] += 1
        self.selection_history.append({
            "context": context,
            "selected": selected_word,
            "timestamp": datetime.now()
        })
```

### Ejemplo Real:

**Usuario A (Ingeniero):**
```
Escribe frecuentemente: "algoritmo", "código", "función", "variable"
Sugerencias personalizadas reflejan esto
```

**Usuario B (Poeta):**
```
Escribe frecuentemente: "corazón", "alma", "cielo", "eternidad"
Sugerencias completamente diferentes para mismo prefijo
```

### Implementación en predicción:

```python
def _apply_user_preferences(self, predictions: Dict, user_adapter):
    """Boost de confianza para palabras que usuario usa"""
    user_prefs = user_adapter.get_preferences()
    
    for word in predictions:
        if word in user_prefs:
            weight = user_prefs[word]["frequency"]
            # Si usuario ha usado 5 veces "gatito":
            # confidence *= (1 + 5 * 0.2) = 1 + 1.0 = 2x boost
            predictions[word]["confidence"] *= (1 + weight * 0.2)
```

---

##  Integración Backend-Frontend

### API REST (FastAPI)

```python
# backend/app.py

@app.post("/api/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    POST /api/predict
    
    Body:
    {
        "text": "El gat",
        "user_id": "joseph_123",
        "max_suggestions": 5
    }
    
    Response:
    {
        "suggestions": ["gatito", "gato", "gatería"],
        "confidence": [0.85, 0.72, 0.61],
        "timestamp": "2026-05-14T10:30:00"
    }
    """
```

### WebSocket para Tiempo Real

```javascript
// frontend/src/components/ChatInterface.jsx

const getPredictions = async (text) => {
    try {
        setIsLoading(true);
        const response = await api.predict(text, userId);
        
        // Mapear respuesta a componente
        setPredictions(response.suggestions.map((word, idx) => ({
            word,
            confidence: response.confidence[idx]
        })));
    } catch (error) {
        console.error('Error:', error);
    } finally {
        setIsLoading(false);
    }
};
```

### Feedback Loop (Aprendizaje Continuo)

```javascript
const handleSelectPrediction = (word) => {
    const newInput = currentInput + word + ' ';
    setCurrentInput(newInput);
    
    // Enviar feedback al backend
    api.sendFeedback(currentInput, word, userId)
        .catch(console.error);
    
    // Backend registra:
    // - Qué palabra eligió
    // - En qué contexto
    // - Actualiza UserAdapter
    // - Próximas predicciones son más precisas
};
```

---

##  Comparación con Otros Enfoques

### ¿Por qué NO usar solo...?

####  **Google Keyboard (RNN/Transformer puro)**
- **Ventaja**: Ultra-preciso, entiende contexto profundo
- **Desventaja**: Requiere GPU, millones de parámetros, latencia >100ms
- **Nuestro caso**: Menos recursos, debe correr en CPU

####  **Predicción por Diccionario Simple**
- **Ventaja**: Ultra-rápido
- **Desventaja**: No entiende contexto, baja precisión
- **Nuestro caso**: Necesitamos precisión razonable

####  **Solo LSTM**
- **Ventaja**: Mejor precisión teórica
- **Desventaja**: Lentitud inaceptable en autocompletado, overhead computacional
- **Nuestro caso**: El usuario espera respuesta <50ms

####  **Solo N-gramas**
- **Ventaja**: Rápido, interpretable
- **Desventaja**: No captura contexto lejano, calidad mediocre
- **Nuestro caso**: El usuario podría escribir párrafos largos

####  **Nuestro Enfoque Híbrido**
```
Trie (velocidad) + N-gramas (patrones) + LSTM (contexto)
= Balance perfecto de velocidad, precisión y recursos
```

---

##  Decisiones de Diseño Clave

### 1. **Español como Primera Clase**

La mayoría de librerías asumen inglés. Implementamos:

```python
class SpanishTokenizer:
    """Tokenización específica para español"""
    def tokenize(self, text):
        # Maneja:
        # - Tildes (á, é, í, ó, ú)
        # - Contracciones (del → de + el)
        # - Genérico-números (1º, 2ª)
        # - Palabras compuestas
```

### 2. **Feedback Loop Inmediato**

Cada selección del usuario mejora el modelo:

```python
@app.post("/api/feedback")
async def send_feedback(request: FeedbackRequest):
    """Cuando usuario selecciona palabra sugerida"""
    
    # Actualizar UserAdapter
    adapter = user_adapters[request.user_id]
    adapter.register_selection(request.text, request.selected)
    
    # Próximas predicciones reflejan esto
```

##  Validación y Evaluación

### Métricas

```
Accuracy = correct_predictions / total_predictions
Latency = tiempo desde entrada a sugerencia mostrada
Precision@k = ¿el usuario encontró su palabra en top-k?
```

### Ejemplo de Evaluación:

```python
# Simulamos usuario escribiendo
texts = [
    "El gato",
    "La política de",
    "Mientras caminaba"
]

for text in texts:
    predictions = predictor.predict(text, max_suggestions=5)
    
    # ¿La palabra que usuario quería escribir está en top-5?
    # Contar hits / total → accuracy
```

---

## Deployment

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - CORS_ORIGINS=*
    
  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    depends_on:
      - backend
```

**Ejecutar:**
```bash
docker-compose up --build
```

Acceder a: `http://localhost:5173`

---




