def test_borrow_book(client, auth_headers, sample_book):
    response = client.post("/api/v1/loans", json={"book_id": sample_book.id}, headers=auth_headers)
    assert response.status_code == 201
    data = response.get_json()
    assert data["book_id"] == sample_book.id
    assert data["overdue"] is False


def test_borrow_book_without_token(client, sample_book):
    response = client.post("/api/v1/loans", json={"book_id": sample_book.id})
    assert response.status_code == 401


def test_borrow_unavailable_book(client, auth_headers, sample_book):
    client.post("/api/v1/loans", json={"book_id": sample_book.id}, headers=auth_headers)
    response = client.post("/api/v1/loans", json={"book_id": sample_book.id}, headers=auth_headers)
    assert response.status_code == 409


def test_borrow_book_updates_availability(client, auth_headers, sample_book):
    client.post("/api/v1/loans", json={"book_id": sample_book.id}, headers=auth_headers)
    response = client.get(f"/api/v1/books/{sample_book.id}")
    assert response.get_json()["available"] is False


def test_loan_limit_reached(client, auth_headers, sample_author):
    from app.extensions import db
    from app.models.book import Book

    for i in range(4):
        book = Book(
            title=f"Book {i}", isbn=f"ISBN{i}", year=2000,
            genre="Test", available=True, author_id=sample_author.id,
        )
        db.session.add(book)
    db.session.commit()

    books = Book.query.all()
    for book in books[:3]:
        response = client.post("/api/v1/loans", json={"book_id": book.id}, headers=auth_headers)
        assert response.status_code == 201

    response = client.post("/api/v1/loans", json={"book_id": books[3].id}, headers=auth_headers)
    assert response.status_code == 409


def test_return_book(client, auth_headers, sample_book):
    loan_resp = client.post("/api/v1/loans", json={"book_id": sample_book.id}, headers=auth_headers)
    loan_id = loan_resp.get_json()["id"]

    response = client.patch(f"/api/v1/loans/{loan_id}/return", headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()["returned_at"] is not None

    book_resp = client.get(f"/api/v1/books/{sample_book.id}")
    assert book_resp.get_json()["available"] is True


def test_my_loans(client, auth_headers, sample_book):
    client.post("/api/v1/loans", json={"book_id": sample_book.id}, headers=auth_headers)
    response = client.get("/api/v1/loans/me", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_list_all_loans_forbidden_for_member(client, auth_headers):
    response = client.get("/api/v1/loans", headers=auth_headers)
    assert response.status_code == 403


def test_list_all_loans_allowed_for_staff(client, staff_headers):
    response = client.get("/api/v1/loans", headers=staff_headers)
    assert response.status_code == 200