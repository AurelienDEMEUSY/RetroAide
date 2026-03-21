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

Les appels LLM du produit passent par **`ai/advisor.py`** (`detect_missing_quarters`, `generate_checklist`, `explain_term`) via `emulate()`. Le fichier **`ai/config.py`** charge `.env` avant l’import d’OpenHosta.

## Lancer l’API (une fois `app/main.py` en place)

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **Documentation interactive (Swagger UI)** : [http://localhost:8000/docs](http://localhost:8000/docs)
- **OpenAPI JSON** : [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

## Tests

Le répertoire `backend/` est la racine pytest (`pythonpath` dans `pyproject.toml`).

```bash
pytest tests/ -v
```

## Docker (image backend)

Contexte de build : répertoire **`backend/`** (pas la racine du monorepo).

### Compose (recommandé)

Depuis **`backend/`**, avec un fichier **`.env`** (copie de `.env.example`, clé API renseignée) :

```bash
cd backend
cp -n .env.example .env   # puis éditer .env
docker compose up --build
```

- **Swagger** : [http://localhost:8000/docs](http://localhost:8000/docs)
- Arrêt : `Ctrl+C` ou `docker compose down`

### Image seule (`docker build` / `docker run`)

```bash
# depuis la racine du dépôt RetroAide
docker build -t retroaide-api ./backend
```

```bash
docker run --rm -p 8000:8000 \
  -e OPENHOSTA_DEFAULT_MODEL_API_KEY="votre-clé" \
  -e OPENHOSTA_DEFAULT_MODEL_NAME="gpt-4.1" \
  -e CORS_ORIGINS="http://localhost:3000" \
  retroaide-api
```

- **Front (personne B)** : `NEXT_PUBLIC_API_URL=http://localhost:8000`. Si le front est dans Docker, adapter `CORS_ORIGINS` à l’origine réelle (ex. `http://localhost:3000`).

## Structure prévue

Voir `CLAUDE.md` à la racine du dépôt (piste A — backend).
