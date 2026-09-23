from app.extensions import db
from app.models.author import Author


class AuthorNotFoundError(Exception):
    pass


def get_all_authors():
    return Author.query.all()


def get_author_by_id(author_id):
    author = Author.query.get(author_id)
    if author is None:
        raise AuthorNotFoundError(f"Author {author_id} not found")
    return author


def get_books_of_author(author_id):
    author = get_author_by_id(author_id)
    return author.books


def create_author(author):
    db.session.add(author)
    db.session.commit()
    return author


def update_author(author_id, data):
    author = get_author_by_id(author_id)
    for key, value in data.items():
        setattr(author, key, value)
    db.session.commit()
    return author


def delete_author(author_id):
    author = get_author_by_id(author_id)
    db.session.delete(author)
    db.session.commit()