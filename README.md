# Textor Predictor Agent 

Un agente inteligente de prediccion de texto en espanol que aprende y se adapta segun tu forma de escribir.

## Caracteristicas

- Prediccion en Tiempo Real: Sugerencias mientras escribes
- Adaptacion Dinamica: Aprende de tu estilo de escritura
- Algoritmo Hibrido Robusto: N-gramas + LSTM + Trie
- Interfaz Calida: Anaranjados, dorados, tonos tierra
- Sin Emojis: Diseno limpio y profesional
- Corpus de 500+ Palabras: Entrenado desde cero
- Backend Robusto: FastAPI + Python
- Frontend Responsivo: React con Tailwind CSS

## Inicio Rapido

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Arquitectura

Algoritmo Hibrido de 3 Capas:
1. N-gramas (Markov Chains) - Analisis de patrones locales
2. LSTM Neural Network - Entiende contexto profundo
3. Trie Data Structure - Autocompletado instantaneo

## Autor

Joseph-hs
