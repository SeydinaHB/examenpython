from app.extensions import ma
from app.models.book import Book

class BookSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Book
        load_instance = True
        include_fk = True

    id = ma.auto_field(dump_only=True)
    title = ma.auto_field(required=True)
    isbn = ma.auto_field(required=True)
    year = ma.auto_field()
    genre = ma.auto_field()
    available = ma.auto_field()
    author_id = ma.auto_field(required=True)

book_schema = BookSchema()
books_schema = BookSchema(many=True)