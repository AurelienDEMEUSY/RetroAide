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
- `LOG_LEVEL` — verbosité des logs applicatifs (`DEBUG`, `INFO`, `WARNING`…). Par défaut **DEBUG** : chaque requête, calculs, appels advisor et erreurs apparaissent sur **stdout** (visible avec `docker compose logs -f`).

Les appels LLM du produit passent par **`ai/advisor.py`** (`detect_missing_quarters`, `generate_checklist`, `explain_term`) via `emulate()`. Le fichier **`ai/config.py`** charge `.env` avant l’import d’OpenHosta.

### Pipeline produit (formulaire → enrichissement → LLM → JSON)

1. **Formulaire** : le front envoie un `UserProfile` JSON sur `POST /api/v1/analyze` ou `POST /api/v1/analyze/report`.
2. **Enrichissement (équivalent MCP, in-process)** : `tools/mcp_pipeline.run_enrichment()` enchaîne les **mêmes handlers** que le serveur MCP (`tools/enrichment_handlers.py`) : appels HTTP vers **CNAV** et **data.gouv** selon l’inventaire YAML. Le bloc texte agrégé est passé au LLM en `retrieval_context`. La réponse API inclut **`enrichment`** : `context_block`, `sources_touched`, et **`tools`** (trace par outil : `sub_steps` pour chaque requête réseau).
3. **LLM** : OpenHosta produit `missing_quarters`, `checklist`, et sur `/analyze/report` la synthèse markdown.
4. **JSON** : champs structurés + sections **markdown** (`/analyze/report`). **Aucune génération PDF** dans ce dépôt : voir *Handoff PDF* ci-dessous.

L’API **ne lance pas** de processus MCP : elle appelle directement les handlers (fiable sous Docker). Un **serveur MCP** séparé expose les mêmes capacités pour Cursor / agents externes.

### Open data (CNAV / data.gouv)

- **`tools/data/opendata_inventory.yaml`** : configuration **statique** (pas une API) qui liste **quels** jeux open data appeler : `dataset_id` CNAV Explore, limites d’enregistrements, requête data.gouv, liens vers les fiches portail, disclaimer légal. Le backend lit ce fichier puis exécute les HTTP via `OpenDataClient`. Pour enrichir les sources, tu modifies ce YAML ou les handlers.
- **Client HTTP** : `tools/opendata_client.py` (timeouts, `User-Agent` via `RETROAIDE_HTTP_USER_AGENT`).
- **Handlers** : `tools/enrichment_handlers.py` (`tool_open_data_bundle`). **`tools/context_builder.py`** reste une façade mince pour compatibilité.
- **Orchestrateur** : `tools/mcp_pipeline.py` (`run_enrichment`). Désactiver les appels sortants avec `ENABLE_OPENDATA_CONTEXT=false`.
- **Prévisualisation** : `POST /internal/context` renvoie le même schéma que `enrichment` (`context_block`, `sources_touched`, `tools`). Protégé par `Authorization: Bearer <INTERNAL_API_TOKEN>` ; sans token, **503**.

### Serveur MCP (stdio)

Pour brancher un client MCP (ex. Cursor) sur les **mêmes** appels APIs externes :

```bash
cd backend
source .venv/bin/activate   # ou équivalent
python -m mcp_server
```

Transport **stdio** par défaut (FastMCP). Outil exposé : **`retroaide_open_data_context`** (paramètre `profile` : objet JSON du formulaire). Le conteneur Docker API n’a pas besoin de ce processus pour servir `/analyze`.

### Rapport JSON + markdown (gabarit document / autre brique PDF)

- **`POST /api/v1/analyze/report`** : même entrée que `/analyze` (champs optionnels document : `full_name`, `ville_signature`, `nb_enfants` ≤ 15, `nb_mois_armee` ≤ 120, `nb_trimestres_avant_20` ≤ 24, `pays_etranger`, `montant_estime_euros` ≥ 1 ou **absent** pour « non renseigné »).
- Réponse : **`identity`**, **`key_figures`**, **`special_cases`** (source unique des valeurs affichées / fusion), **`markdown`** (`document_complet` = synthèse + checklist détaillée + cas particuliers sans redite de la checklist dans le seed LLM), **`enrichment`**, **`analyze`**.

### Handoff PDF (autre personne / autre service)

La génération binaire PDF est **hors scope** de ce backend. Consommer typiquement :

- `markdown.document_complet` ou `markdown.synthese` / `checklist` / `cas_particuliers` ;
- champs structurés pour un gabarit type « fusion de champs » (ex. anciennes clés `[NOM_UTILISATEUR]` → `identity.nom_utilisateur`, `[AGE_LEGAL]` → `str(key_figures.age_legal)`, `[LISTE_PERIODES_MANQUANTES]` → `special_cases.liste_periodes_manquantes`, etc.) ;
- `enrichment.context_block` et `enrichment.tools` pour citation / audit de sources.

La fonction utilitaire `core.report_document.build_merge_placeholders` reste disponible côté code si tu veux regénérer un dict `[CLÉ]` → `str` à partir des mêmes valeurs que le routeur.

`POST /api/v1/analyze` inclut aussi **`analyze.enrichment`** (même schéma) pour le dashboard sans appeler `/report`.

## Lancer l’API (une fois `app/main.py` en place)

```bash
pip install -r requirements.txt
# optionnel : export LOG_LEVEL=DEBUG
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
```

- **Documentation interactive (Swagger UI)** : [http://localhost:8000/docs](http://localhost:8000/docs)
- **OpenAPI JSON** : [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

## Tests

Le répertoire `backend/` est la racine pytest (`pythonpath` dans `pyproject.toml`).

```bash
pytest tests/ -v
# optionnel : smoke HTTP réel vers CNAV / data.gouv
RUN_LIVE_OPENDATA=1 pytest tests/test_integration_opendata.py -v -m integration
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

- **Swagger** : ouvrir **[http://localhost:8000/docs](http://localhost:8000/docs)** (ou `http://127.0.0.1:8000/docs`). Ne pas utiliser `http://0.0.0.0:8000` dans le navigateur : `0.0.0.0` signifie seulement « écouter sur toutes les interfaces », ce n’est pas une adresse de connexion.
- Le fichier `.env` est monté dans le conteneur (`/app/.env`) pour éviter les avertissements OpenHosta tout en gardant les secrets hors image.
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
