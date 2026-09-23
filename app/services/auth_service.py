from app.extensions import db
from app.models.user import User


class UserAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


def register_user(email, username, password, role="member"):
    if User.query.filter((User.email == email) | (User.username == username)).first():
        raise UserAlreadyExistsError("Email ou nom d'utilisateur déjà utilisé")

    user = User(email=email, username=username, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        raise InvalidCredentialsError("Identifiants invalides")
    return user


def get_user_by_id(user_id):
    return User.query.get(user_id)