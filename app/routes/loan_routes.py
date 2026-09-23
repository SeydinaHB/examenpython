from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from app.schemas.loan_schema import loan_schema, loans_schema
from app.services.loan_service import (
    create_loan,
    return_loan,
    get_loan_by_id,
    get_loans_of_user,
    get_all_loans,
    LoanNotFoundError,
    BookNotAvailableError,
    LoanLimitReachedError,
    BookNotFoundError,
    UserNotFoundError,
)

loan_bp = Blueprint("loans", __name__, url_prefix="/api/v1/loans")


@loan_bp.post("")
@jwt_required()
def borrow_book():
    """
    Emprunter un livre
    ---
    tags:
      - Loans
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - book_id
          properties:
            book_id:
              type: integer
            user_id:
              type: integer
              description: Réservé au staff, pour emprunter au nom d'un autre utilisateur
    responses:
      201:
        description: Emprunt créé
      403:
        description: Interdit pour un membre d'emprunter au nom d'un autre
      404:
        description: Livre ou utilisateur introuvable
      409:
        description: Livre indisponible ou limite d'emprunts atteinte
    """
    data = request.get_json()
    if not data or "book_id" not in data:
        return jsonify({"error": "invalid_payload", "message": "book_id requis"}), 400

    current_user_id = int(get_jwt_identity())
    role = get_jwt().get("role", "member")

    target_user_id = data.get("user_id", current_user_id)
    if target_user_id != current_user_id and role != "staff":
        return jsonify({"error": "forbidden", "message": "Seul un staff peut emprunter au nom d'un autre utilisateur"}), 403

    try:
        loan = create_loan(data["book_id"], target_user_id)
    except BookNotFoundError:
        return jsonify({"error": "book_not_found", "message": "Livre introuvable"}), 404
    except UserNotFoundError:
        return jsonify({"error": "user_not_found", "message": "Utilisateur introuvable"}), 404
    except BookNotAvailableError:
        return jsonify({"error": "book_not_available", "message": "Ce livre n'est pas disponible"}), 409
    except LoanLimitReachedError:
        return jsonify({"error": "loan_limit_reached", "message": "Limite de 3 emprunts actifs atteinte"}), 409

    return jsonify(loan_schema.dump(loan)), 201


@loan_bp.patch("/<int:loan_id>/return")
@jwt_required()
def give_back_book(loan_id):
    """
    Rendre un livre emprunté
    ---
    tags:
      - Loans
    security:
      - Bearer: []
    parameters:
      - in: path
        name: loan_id
        type: integer
        required: true
    responses:
      200:
        description: Emprunt marqué comme rendu
      403:
        description: Impossible de rendre l'emprunt d'un autre utilisateur
      404:
        description: Emprunt introuvable
    """
    current_user_id = int(get_jwt_identity())
    role = get_jwt().get("role", "member")

    try:
        loan = get_loan_by_id(loan_id)
    except LoanNotFoundError:
        return jsonify({"error": "loan_not_found", "message": "Emprunt introuvable"}), 404

    if loan.user_id != current_user_id and role != "staff":
        return jsonify({"error": "forbidden", "message": "Vous ne pouvez pas rendre l'emprunt d'un autre utilisateur"}), 403

    loan = return_loan(loan_id)
    return jsonify(loan_schema.dump(loan)), 200


@loan_bp.get("/me")
@jwt_required()
def my_loans():
    current_user_id = int(get_jwt_identity())
    loans = get_loans_of_user(current_user_id)
    return jsonify(loans_schema.dump(loans)), 200


@loan_bp.get("")
@jwt_required()
def list_loans():
    role = get_jwt().get("role", "member")
    if role != "staff":
        return jsonify({"error": "forbidden", "message": "Seul un staff peut lister tous les emprunts"}), 403

    loans = get_all_loans()
    return jsonify(loans_schema.dump(loans)), 200


@loan_bp.get("/<int:loan_id>")
@jwt_required()
def get_loan(loan_id):
    current_user_id = int(get_jwt_identity())
    role = get_jwt().get("role", "member")

    try:
        loan = get_loan_by_id(loan_id)
    except LoanNotFoundError:
        return jsonify({"error": "loan_not_found", "message": "Emprunt introuvable"}), 404

    if loan.user_id != current_user_id and role != "staff":
        return jsonify({"error": "forbidden", "message": "Vous ne voyez que vos propres emprunts"}), 403

    return jsonify(loan_schema.dump(loan)), 200