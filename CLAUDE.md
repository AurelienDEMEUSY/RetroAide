# RetroAide — Plan d’implémentation (Next.js + backend Python)

> **Pour l’agent d’exécution :** sous-skill recommandé : `superpowers:executing-plans` pour implémenter ce plan tâche par tâche.

**Objectif :** Livrer RetroAide (PRD v1.0) avec **Next.js** et un **backend Python** où **OpenHosta** porte toute la couche LLM (droits oubliés, checklist, glossaire). Les **seuls calculs figés** restent en Python pur ; le **PDF** reste fpdf2, hors LLM.

**Stack :** Next.js (TS, App Router), Tailwind, **FastAPI**, **OpenHosta** (hand-e-fr), Pydantic, **fpdf2**, python-dotenv, Docker.

---

## OpenHosta — rôle, intégration, flux

**À quoi ça sert :** OpenHosta relie le backend à un LLM avec des **fonctions Python “décorées”** (souvent via `emulate()` dans la doc du projet) : tu écris la **signature + docstring** (contrat métier), le runtime appelle le modèle et **retourne une valeur typée** (liste, texte, etc.). Pas de chaîne de prompts dispersée dans FastAPI : **tout le LLM passe par `backend/ai/advisor.py`**.

| Besoin produit | Fonction (PRD §7.3) | Endpoint qui l’utilise |
|----------------|---------------------|-------------------------|
| Droits potentiellement oubliés | `detect_missing_quarters(profile: dict) -> list[dict]` | `POST /api/v1/analyze` |
| Checklist personnalisée | `generate_checklist(profile, missing_quarters) -> list[...]` | `POST /api/v1/analyze` |
| Explication d’un terme | `explain_term(term: str) -> str` | `POST /api/v1/glossary` |

**Règles simples :**
- **Chiffres du dashboard** (`departure_age`, `quarters_worked`, `quarters_remaining`) : **jamais** OpenHosta — uniquement `core/calculator.py`.
- **Tout texte “intelligent”** (listes, phrases, glossaire) : **OpenHosta** dans `advisor.py`.
- **Échec LLM / JSON illisible :** fallback minimal (checklist statique courte, `missing_quarters` vide ou message générique, glossaire : phrase fixe).

**Config :** `backend/ai/config.py` lit la clé / le provider depuis `.env` (noms exacts selon la doc OpenHosta du dépôt hand-e-fr). `CORS_ORIGINS` reste dans la même `.env` ou à côté.

**Schéma mental :**

```
[Next.js] --JSON profil--> [FastAPI /analyze] --> calculator (chiffres)
                                              --> advisor.detect_missing_quarters (OpenHosta)
                                              --> advisor.generate_checklist (OpenHosta)
[Next.js] --{term}--> [FastAPI /glossary] --> advisor.explain_term (OpenHosta)
[Next.js] --snapshot--> [FastAPI /export-pdf] --> pdf_export (fpdf2, pas de LLM)
```

---

## Architecture (résumé)

- **Frontend :** formulaire 3 étapes, dashboard, glossaire (appels HTTP), checklists en état local, loaders pendant les appels **analyze** et **glossary**.
- **Backend :** FastAPI + **OpenHosta centralisé dans `ai/advisor.py`** + `core/calculator.py` + **`core/pdf_export.py` (détail important, voir A6)**.
- Pas d’auth, pas de persistance serveur des cases cochées.

---

## Rôles : deux personnes, deux périmètres

| Qui | Dossier | Responsabilité |
|-----|---------|----------------|
| **A — Backend** | `backend/` | FastAPI, **OpenHosta (`advisor.py`)**, calculator, **PDF**, tests, Dockerfile |
| **B — Frontend** | `frontend/` | Next.js, `fetch` vers l’API, UX/a11y, Dockerfile |

**Intégration :** `docker-compose.yml` à la racine quand les deux Dockerfiles existent. B peut utiliser un **mock JSON** tant que `/analyze` n’est pas prêt.

---

## Contrat API (figé au kickoff)

| Méthode | Route | Rôle |
|--------|--------|------|
| `POST` | `/api/v1/analyze` | Chiffres (Python) + **OpenHosta** : `missing_quarters`, `checklist` |
| `POST` | `/api/v1/glossary` | **OpenHosta** : `explain_term` |
| `POST` | `/api/v1/export-pdf` | **fpdf2** uniquement — body = snapshot profil + résultat analyse |

**Profil (champs PRD) :** `birth_year`, `career_start_year`, `status`, `currently_employed`, flags enfants / chômage / arrêt long / militaire / temps partiel long.

**Exemple réponse `analyze` (extrait) :**

```json
{
  "departure_age": 64,
  "quarters_worked": 128,
  "quarters_remaining": 44,
  "missing_quarters": [{ "period": "…", "reason": "…", "action": "…" }],
  "checklist": [{ "title": "…", "detail": "…", "url": "https://…" }]
}
```

*(Si `checklist` est une liste de chaînes côté LLM, normaliser en objets dans `advisor.py` ou documenter pour B.)*

OpenAPI : `GET /openapi.json` → partager avec B.

---

## Structure dépôt

```
backend/
  app/main.py, schemas.py
  app/routers/analyze.py   # calculator + advisor (OpenHosta)
  app/routers/glossary.py  # advisor.explain_term uniquement
  app/routers/pdf.py       # pdf_export uniquement
  core/calculator.py
  core/pdf_export.py       # fpdf2 — section A6 détaillée
  ai/config.py             # env OpenHosta
  ai/advisor.py            # TOUTES les fonctions emulate / LLM ici
frontend/ …
```

---

## Kickoff commun (court)

1. URLs : API `8000`, front `3000`.
2. Figurer champs JSON + forme `missing_quarters` / `checklist`.
3. A expose `/docs` ; B aligne les types TS sur OpenAPI.
4. Décider où annoncer un changement de contrat (issue / Slack).

---

## Piste A — Backend

### A1 — Env + README

- `backend/.env.example` : variables **OpenHosta** (doc hand-e-fr) + `CORS_ORIGINS=http://localhost:3000`.
- `backend/README.md` : `uvicorn`, `pytest`, lien `/docs`.

`chore(backend): env example and readme`

---

### A2 — Calculator seul (sans OpenHosta)

- `core/calculator.py` : `calculate_departure_age`, `estimate_quarters_worked`, `quarters_remaining` (PRD §7.4).
- `tests/test_calculator.py` : quelques assertions sur années / plafond 172.

`feat(backend): deterministic retirement metrics`

---

### A3 — OpenHosta : un seul module `advisor.py`

**But :** trois entrées LLM, un seul endroit à maintenir.

**Fichiers :** `ai/config.py`, `ai/advisor.py`, `tests/test_advisor_mock.py` (monkeypatch / mock des appels LLM pour CI sans clé).

**Contrat des fonctions (docstrings = prompt implicite pour le modèle) :**

```python
# advisor.py — pseudo-code : adapter aux imports réels OpenHosta (hand-e-fr)

def detect_missing_quarters(profile: dict) -> list[dict]:
    """
    Périodes pouvant donner des trimestres souvent oubliés (France, régime général).
    Retour : liste de dicts avec clés period, reason, action. Français simple.
    """
    return emulate()  # ou équivalent décorateur OpenHosta

def generate_checklist(profile: dict, missing_quarters: list) -> list[dict]:
    """
    5 à 10 étapes concrètes, ordonnées, français simple, URLs admin quand connu.
    """
    return emulate()

def explain_term(term: str) -> str:
    """
    Explication en français très simple, max 3 phrases, sans jargon, pour senior.
    """
    return emulate()
```

**Étape unique côté implémentation :** brancher la vraie API OpenHosta sur ces trois fonctions ; si erreur → retours de secours (listes vides / checklist minimaliste / phrase glossaire générique).

`feat(backend): OpenHosta advisor (single module) + mocks`

---

### A4 — `POST /api/v1/analyze` (route mince)

- Assemble : `calculator` → chiffres ; puis `advisor.detect_missing_quarters` puis `advisor.generate_checklist` (ou en parallèle si tu veux gagner de la latence — **YAGNI** : séquentiel suffit pour 48h).
- Un test `TestClient` : POST minimal → clés présentes + types cohérents.

**Jalon :** prévenir B quand l’URL réelle répond.

`feat(api): analyze endpoint`

---

### A5 — `POST /api/v1/glossary` (une ligne métier)

- Body `{ "term": "trimestre" }` → `{ "explanation": advisor.explain_term(term) }`.
- Test mocké.

`feat(api): glossary endpoint`

---

### A6 — PDF (fpdf2) + `POST /api/v1/export-pdf` — **ne pas simplifier**

**Objectif :** PDF A4 lisible, **disclaimer légal obligatoire** (PRD §9), même contenu sensible que l’écran (résumé profil + checklist), sans OpenHosta.

**Fichiers :**
- `core/pdf_export.py`
- `app/routers/pdf.py`
- `tests/test_pdf_export.py`

**Contenu obligatoire du PDF :**
1. Titre : ex. « RetroAide — Mon plan d’action ».
2. Date de génération.
3. **Résumé profil** (année naissance, début carrière, statut, oui/non situations — pas besoin d’être exhaustif si le body API est déjà un snapshot).
4. **Trois métriques** : âge légal de départ, trimestres estimés, trimestres restants (reprises du body ou recalculées de la même source que `/analyze` pour cohérence).
5. **Checklist** (titres + détails + URL si présents).
6. **Bloc disclaimer** (texte visible, pas en filigrane seul), par exemple :

> RetroAide est un outil d’information pédagogique. Les résultats sont des estimations basées sur votre profil et ne constituent pas un avis juridique. Pour toute décision officielle, consultez votre caisse de retraite ou un conseiller agréé.

**Implémentation fpdf2 (recommandations) :**
- `FPDF` ou `FPDF2` : marges confortables (ex. 20 mm), police au moins 11–12 pt pour le corps, titres plus grands.
- Utiliser `multi_cell` pour les paragraphes longs (wrapping) ; gérer `ln` après les blocs.
- Sections séparées par un peu d’espace vertical ; éviter les tableaux complexes (listes numérotées simples pour la checklist).
- Nom de fichier téléchargeable côté route : ex. `Content-Disposition: attachment; filename="retroaide-plan.pdf"`.

**Route FastAPI :**
- Body : même schéma qu’un « snapshot » convenu avec le front (profil + `departure_age` + trimestres + `checklist` au minimum) — évite de rappeler OpenHosta ici.
- Réponse : `Response(content=pdf_bytes, media_type="application/pdf", headers=...)`.

**Tests :**
- Générer un PDF en mémoire depuis un dict fixe ; assert `len(bytes) > 1000` (ordre de grandeur) ; assert qu’un **fragment du disclaimer** apparaît dans les bytes décodés en latin-1 / utf-8 selon ce que fpdf2 émet (ou recherche sous-chaîne « avis juridique » si encodage compatible).

`feat(api): pdf export with legal disclaimer`

---

### A7 — Docker backend + CORS

- `backend/Dockerfile`, `uvicorn`, user non-root si facile.
- Documenter pour B l’URL publique de l’API (`NEXT_PUBLIC_API_URL`).

`chore(backend): dockerfile`

---

## Piste B — Frontend (rappel court)

- B1 `.env.local.example` + mock optionnel.
- B2 Next + `lib/api.ts` (`analyze`, `glossary`, `downloadPlanPdf`).
- B3 layout a11y + disclaimer accueil.
- B4 wizard 3 étapes + « C’est quoi ça ? » → `/glossary`.
- B5 dashboard + loaders (**attente OpenHosta** sur analyze/glossary).
- B6 bouton PDF + Dockerfile front.

Intégration : `docker-compose.yml` + QA croisée (profil Martine, CORS, PDF reçu).

---

*RetroAide — OpenHosta = couche LLM unique (`advisor.py`) ; PDF = fpdf2 détaillé en A6.*
