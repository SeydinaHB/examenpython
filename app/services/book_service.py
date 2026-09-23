from app.extensions import db
from app.models.book import Book

class BookNotFoundError(Exception):
    pass

def get_all_books():
    return Book.query.all()

def get_book_by_id(book_id):
    book = Book.query.get(book_id)
    if book is None:
        raise BookNotFoundError(f"Book {book_id} not found")
    return book

def create_book(book):
    db.session.add(book)
    db.session.commit()
    return book

def update_book(book_id, data):
    book = get_book_by_id(book_id)
    for key, value in data.items():
        setattr(book, key, value)
    db.session.commit()
    return book

def delete_book(book_id):
    book = get_book_by_id(book_id)
    db.session.delete(book)
    db.session.commit()