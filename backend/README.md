# RetroAide — Backend (FastAPI + OpenHosta)

API Python pour l’analyse retraite (calculs déterministes, LLM via OpenHosta, export PDF).

## Prérequis

- Python 3.11+ (recommandé)
- Un environnement virtuel

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

## Configuration

```bash
cp .env.example .env
```

Renseigner au minimum :

- `OPENHOSTA_DEFAULT_MODEL_API_KEY` — clé API du modèle distant (voir [OpenHosta — Option B](https://github.com/hand-e-fr/OpenHosta#option-b-remote-api-openai)).
- `CORS_ORIGINS` — origine du front Next.js (ex. `http://localhost:3000`).

## Lancer l’API (une fois `app/main.py` en place)

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **Documentation interactive (Swagger UI)** : [http://localhost:8000/docs](http://localhost:8000/docs)
- **OpenAPI JSON** : [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

## Tests

```bash
pytest tests/ -v
```

## Structure prévue

Voir `CLAUDE.md` à la racine du dépôt (piste A — backend).
