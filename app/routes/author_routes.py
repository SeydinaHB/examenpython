from flask import Blueprint, request, jsonify

from app.schemas.author_schema import author_schema, authors_schema
from app.schemas.book_schema import books_schema
from app.services.author_service import (
    get_all_authors,
    get_author_by_id,
    get_books_of_author,
    create_author,
    update_author,
    delete_author,
    AuthorNotFoundError,
)

author_bp = Blueprint("authors", __name__, url_prefix="/api/v1/authors")


@author_bp.get("")
def list_authors():
    authors = get_all_authors()
    return jsonify(authors_schema.dump(authors)), 200


@author_bp.get("/<int:author_id>")
def get_author(author_id):
    try:
        author = get_author_by_id(author_id)
    except AuthorNotFoundError:
        return jsonify({"error": "author_not_found", "message": f"Auteur {author_id} introuvable"}), 404
    return jsonify(author_schema.dump(author)), 200


@author_bp.get("/<int:author_id>/books")
def get_author_books(author_id):
    try:
        books = get_books_of_author(author_id)
    except AuthorNotFoundError:
        return jsonify({"error": "author_not_found", "message": f"Auteur {author_id} introuvable"}), 404
    return jsonify(books_schema.dump(books)), 200


@author_bp.post("")
def add_author():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "invalid_payload", "message": "Corps JSON manquant"}), 400

    errors = author_schema.validate(json_data)
    if errors:
        return jsonify({"error": "validation_error", "message": errors}), 422

    author = author_schema.load(json_data)
    author = create_author(author)
    return jsonify(author_schema.dump(author)), 201


@author_bp.put("/<int:author_id>")
def edit_author(author_id):
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "invalid_payload", "message": "Corps JSON manquant"}), 400

    try:
        author = update_author(author_id, json_data)
    except AuthorNotFoundError:
        return jsonify({"error": "author_not_found", "message": f"Auteur {author_id} introuvable"}), 404

    return jsonify(author_schema.dump(author)), 200


@author_bp.delete("/<int:author_id>")
def remove_author(author_id):
    try:
        delete_author(author_id)
    except AuthorNotFoundError:
        return jsonify({"error": "author_not_found", "message": f"Auteur {author_id} introuvable"}), 404
    return "", 204