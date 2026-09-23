from app.extensions import ma
from app.models.author import Author

class AuthorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Author
        load_instance = True

    id = ma.auto_field(dump_only=True)
    name = ma.auto_field(required=True)
    nationality = ma.auto_field()
    bio = ma.auto_field()

author_schema = AuthorSchema()
authors_schema = AuthorSchema(many=True)