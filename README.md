# API Bibliothèque — Projet Final Flask

API REST de gestion de bibliothèque universitaire : catalogue, auteurs, utilisateurs et emprunts, avec authentification JWT et contrôle d'accès par rôle.

## Stack technique
- Flask + Flask-SQLAlchemy (persistance)
- Flask-Migrate / Alembic (migrations)
- Flask-Marshmallow (validation)
- Flask-JWT-Extended (authentification)
- Flask-Limiter (rate limiting)
- Flasgger (documentation OpenAPI / Swagger)
- pytest (tests, couverture ≥ 70%)
- Docker + Gunicorn (déploiement)

## Installation locale

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
```

Copiez `.env.example` en `.env` et ajustez les valeurs si besoin.

## Lancement (local, SQLite)

```bash
$env:FLASK_APP="run.py"
flask db upgrade
python run.py
```

L'API est disponible sur `http://127.0.0.1:5000`.
Documentation interactive : `http://127.0.0.1:5000/apidocs/`

## Lancement avec Docker (API + PostgreSQL)

```bash
docker compose up
```

Les migrations sont appliquées automatiquement au démarrage.

## Tests

```bash
pytest -v
pytest --cov=app --cov-report=term-missing
```

## Ressources principales

| Ressource | Endpoints |
|---|---|
| Auth | `/api/v1/auth/register`, `/login`, `/refresh`, `/me` |
| Books | `/api/v1/books` (CRUD) |
| Authors | `/api/v1/authors` (CRUD), `/api/v1/authors/<id>/books` |
| Loans | `/api/v1/loans` (emprunter), `/api/v1/loans/<id>/return`, `/api/v1/loans/me` |

## Règles métier principales
- Un livre non disponible ne peut pas être emprunté (409)
- Limite de 3 emprunts actifs par utilisateur (409)
- Rôles `member` / `staff` avec permissions distinctes
- Un membre ne voit que ses propres emprunts (403 sinon)