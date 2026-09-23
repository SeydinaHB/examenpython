import pytest
from app import create_app
from app.extensions import db
from app.models.author import Author


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_author(app):
    author = Author(name="George Orwell", nationality="British")
    db.session.add(author)
    db.session.commit()
    return author

@pytest.fixture
def auth_headers(client):
    client.post("/api/v1/auth/register", json={
        "email": "alice@example.com",
        "username": "alice",
        "password": "motdepasse123",
        "role": "member",
    })
    login_resp = client.post("/api/v1/auth/login", json={
        "username": "alice",
        "password": "motdepasse123",
    })
    token = login_resp.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def staff_headers(client):
    client.post("/api/v1/auth/register", json={
        "email": "staff@example.com",
        "username": "staffuser",
        "password": "motdepasse123",
        "role": "staff",
    })
    login_resp = client.post("/api/v1/auth/login", json={
        "username": "staffuser",
        "password": "motdepasse123",
    })
    token = login_resp.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_book(app, sample_author):
    from app.extensions import db
    from app.models.book import Book

    book = Book(
        title="1984", isbn="9780451524935", year=1949,
        genre="Dystopie", available=True, author_id=sample_author.id,
    )
    db.session.add(book)
    db.session.commit()
    return book