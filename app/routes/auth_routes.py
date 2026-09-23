from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)

from app.schemas.user_schema import user_schema
from app.services.auth_service import (
    register_user,
    authenticate_user,
    get_user_by_id,
    UserAlreadyExistsError,
    InvalidCredentialsError,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth_bp.post("/register")
def register():
    """
    Inscrire un nouvel utilisateur
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - username
            - password
          properties:
            email:
              type: string
            username:
              type: string
            password:
              type: string
            role:
              type: string
              enum: [member, staff]
    responses:
      201:
        description: Utilisateur créé
      409:
        description: Email ou username déjà utilisé
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid_payload", "message": "Corps JSON manquant"}), 400

    required = {"email", "username", "password"}
    if not required.issubset(data):
        return jsonify({"error": "validation_error", "message": "email, username et password sont requis"}), 422

    role = data.get("role", "member")
    if role not in ("member", "staff"):
        return jsonify({"error": "validation_error", "message": "role doit être 'member' ou 'staff'"}), 422

    try:
        user = register_user(data["email"], data["username"], data["password"], role)
    except UserAlreadyExistsError as e:
        return jsonify({"error": "user_exists", "message": str(e)}), 409

    return jsonify(user_schema.dump(user)), 201

from app.extensions import limiter
@auth_bp.post("/login")
@limiter.limit("5 per minute")
def login():
    """
    Se connecter
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      200:
        description: Jetons JWT retournés
      401:
        description: Identifiants invalides
    """
    data = request.get_json()
    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "invalid_payload", "message": "username et password requis"}), 400

    try:
        user = authenticate_user(data["username"], data["password"])
    except InvalidCredentialsError as e:
        return jsonify({"error": "invalid_credentials", "message": str(e)}), 401

    access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user_schema.dump(user),
    }), 200


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    new_access_token = create_access_token(identity=identity)
    return jsonify({"access_token": new_access_token}), 200


@auth_bp.get("/me")
@jwt_required()
def me():
    identity = get_jwt_identity()
    user = get_user_by_id(int(identity))
    if user is None:
        return jsonify({"error": "user_not_found", "message": "Utilisateur introuvable"}), 404
    return jsonify(user_schema.dump(user)), 200