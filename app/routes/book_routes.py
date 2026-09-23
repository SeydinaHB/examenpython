from flask import Blueprint, request, jsonify

from app.schemas.book_schema import book_schema, books_schema
from app.services.book_service import (
    get_all_books,
    get_book_by_id,
    create_book,
    update_book,
    delete_book,
    BookNotFoundError,
)

book_bp = Blueprint("books", __name__, url_prefix="/api/v1/books")


@book_bp.get("")
def list_books():
    """
    Lister tous les livres
    ---
    tags:
      - Books
    responses:
      200:
        description: Liste des livres
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              title:
                type: string
              isbn:
                type: string
              available:
                type: boolean
    """
    books = get_all_books()
    return jsonify(books_schema.dump(books)), 200


@book_bp.get("/<int:book_id>")
def get_book(book_id):
    try:
        book = get_book_by_id(book_id)
    except BookNotFoundError:
        return jsonify({"error": "book_not_found", "message": f"Livre {book_id} introuvable"}), 404
    return jsonify(book_schema.dump(book)), 200


@book_bp.post("")
def add_book():
    """
    Créer un livre
    ---
    tags:
      - Books
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - title
            - isbn
            - author_id
          properties:
            title:
              type: string
            isbn:
              type: string
            year:
              type: integer
            genre:
              type: string
            available:
              type: boolean
            author_id:
              type: integer
    responses:
      201:
        description: Livre créé
      422:
        description: Erreur de validation
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "invalid_payload", "message": "Corps JSON manquant"}), 400

    errors = book_schema.validate(json_data)
    if errors:
        return jsonify({"error": "validation_error", "message": errors}), 422

    book = book_schema.load(json_data)
    book = create_book(book)
    return jsonify(book_schema.dump(book)), 201


@book_bp.put("/<int:book_id>")
def edit_book(book_id):
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "invalid_payload", "message": "Corps JSON manquant"}), 400

    try:
        book = update_book(book_id, json_data)
    except BookNotFoundError:
        return jsonify({"error": "book_not_found", "message": f"Livre {book_id} introuvable"}), 404

    return jsonify(book_schema.dump(book)), 200


@book_bp.delete("/<int:book_id>")
def remove_book(book_id):
    try:
        delete_book(book_id)
    except BookNotFoundError:
        return jsonify({"error": "book_not_found", "message": f"Livre {book_id} introuvable"}), 404
    return "", 204