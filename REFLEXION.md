# Réponses aux questions de réflexion

## Question 1 — Choix du sujet et justification

J'ai choisi le Sujet A — API de gestion de bibliothèque. Ce domaine me permet de me concentrer sur la qualité technique de l'implémentation plutôt que sur la complexité métier, tout en couvrant des règles intéressantes à modéliser. La règle la plus riche à mon sens est la limite de 3 emprunts actifs par membre : elle nécessite une requête de comptage à chaque tentative d'emprunt et une gestion d'erreur claire (409). La distinction de permissions entre member et staff est aussi pertinente à modéliser proprement via le contrôle d'accès JWT. Enfin, le calcul de l'attribut overdue (dérivé de due_date et de la date courante) est un bon exercice de logique métier à isoler dans la couche service plutôt que dans la route.

## Question 2 — Tableau des ressources (contrat HTTP)

| Ressource | URL collection | URL élément | Méthodes | Code succès |
|---|---|---|---|---|
| Book | `/api/v1/books` | `/api/v1/books/<id>` | GET, POST, PUT, DELETE | 200 / 201 / 204 |
| Author | `/api/v1/authors` | `/api/v1/authors/<id>` | GET, POST, PUT, DELETE | 200 / 201 / 204 |
| Author (livres) | `/api/v1/authors/<id>/books` | — | GET | 200 |
| Auth | `/api/v1/auth/register`, `/login`, `/refresh` | `/api/v1/auth/me` | POST, POST, POST, GET | 201 / 200 / 200 / 200 |
| Loan | `/api/v1/loans` | `/api/v1/loans/<id>` | POST, GET | 201 / 200 |
| Loan (retour) | — | `/api/v1/loans/<id>/return` | PATCH | 200 |
| Loan (mes emprunts) | `/api/v1/loans/me` | — | GET | 200 |

**Écarts au CRUD standard, justifiés :**

- **`PATCH /loans/<id>/return`** au lieu d'un `PUT` générique : on ne modifie pas l'emprunt dans son ensemble, seulement son état de retour — un `PATCH` est sémantiquement plus juste, et évite au client de devoir renvoyer tous les champs de l'emprunt pour une seule action.
- **`GET /loans/me`** plutôt qu'un filtre `?user_id=<moi>` sur `/loans` : rend l'intention explicite dans l'URL, sans avoir à vérifier à chaque appel que le `user_id` demandé correspond bien à l'utilisateur connecté.
- **Pas de `DELETE` sur Loan** : un emprunt n'est jamais supprimé, seulement "retourné" (`returned_at` renseigné) — on conserve l'historique, cohérent avec l'exigence "mes emprunts" qui doit aussi montrer les emprunts passés.
- **`POST /auth/register` plutôt qu'un `POST /users` générique** : la création d'un utilisateur passe uniquement par le flux d'inscription, avec hash du mot de passe imposé — pas de création "libre" d'utilisateurs.

## Question 3 — Les 3 codes d'erreur les plus fréquents

| Code | Situation métier concrète |
|---|---|
| 404 | `GET /books/999` sur un livre inexistant, ou `GET /loans/<id>` sur un emprunt inconnu |
| 409 | Emprunter un livre déjà indisponible, ou dépasser la limite de 3 emprunts actifs |
| 403 | Un membre tente `GET /loans` (liste complète, réservée au staff) ou consulte l'emprunt d'un autre utilisateur |

Deux codes supplémentaires très présents dans l'API : le 422 (validation Marshmallow ratée sur `POST /books` ou `/authors`) et le 401 (accès à une route protégée sans jeton JWT valide).

## Question 4 — Schémas JSON (réponse d'erreur et pagination)

**Réponse d'erreur unique, valable pour toute l'API :**

```json
{
  "error": "book_not_available",
  "message": "Ce livre n'est pas disponible"
}
```

**Réponse de collection paginée :**

```json
{
  "data": [
    { "id": 1, "title": "1984" },
    { "id": 2, "title": "Le Meilleur des mondes" }
  ],
  "meta": {
    "page": 1,
    "per_page": 20,
    "total_items": 42,
    "total_pages": 3
  }
}
```

## Question 5 — Modèle de données et stratégie lazy/eager

**Cardinalités et clés étrangères :**

- Author 1 — N Book : `books.author_id → authors.id`
- Book 1 — N Loan : `loans.book_id → books.id`
- User 1 — N Loan : `loans.user_id → users.id`

**Stratégie de chargement :**

| Relation | Type | Justification |
|---|---|---|
| `Book.author` | eager (`joined`) | Presque toujours nécessaire dès qu'on affiche un livre — évite une requête supplémentaire (N+1) |
| `Loan.book` | eager (`joined`) | Nécessaire dès qu'on affiche un emprunt |
| `Loan.user` | eager (`joined`) | Nécessaire dès qu'on affiche un emprunt |
| `Author.books` | lazy (`select`) | Utile seulement sur l'endpoint dédié `/authors/<id>/books` — chargement systématique serait un gaspillage |
| `User.loans` | lazy (`select`) | Utile seulement sur `/loans/me` — pas nécessaire à chaque accès à un utilisateur |

Les relations many-to-one très souvent consultées sont chargées en eager pour éviter le problème classique des requêtes N+1 (une requête supplémentaire par ligne). Les relations one-to-many, utilisées seulement sur des endpoints spécifiques, restent en lazy pour ne pas alourdir les requêtes qui n'en ont pas besoin.