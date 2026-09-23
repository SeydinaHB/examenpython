from app.extensions import ma
from app.models.user import User

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = False
        exclude = ("password_hash",)

    id = ma.auto_field(dump_only=True)
    email = ma.auto_field()
    username = ma.auto_field()
    role = ma.auto_field(dump_only=True)

user_schema = UserSchema()