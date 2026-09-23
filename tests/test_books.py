def test_list_books_empty(client):
    response = client.get("/api/v1/books")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_book(client, sample_author):
    payload = {
        "title": "1984",
        "isbn": "9780451524935",
        "year": 1949,
        "genre": "Dystopie",
        "available": True,
        "author_id": sample_author.id,
    }
    response = client.post("/api/v1/books", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "1984"
    assert data["id"] is not None


def test_create_book_missing_fields(client):
    response = client.post("/api/v1/books", json={"title": "Sans ISBN"})
    assert response.status_code == 422


def test_get_book_not_found(client):
    response = client.get("/api/v1/books/999")
    assert response.status_code == 404


def test_update_book(client, sample_author):
    create_resp = client.post("/api/v1/books", json={
        "title": "1984", "isbn": "9780451524935", "year": 1949,
        "genre": "Dystopie", "available": True, "author_id": sample_author.id,
    })
    book_id = create_resp.get_json()["id"]

    update_resp = client.put(f"/api/v1/books/{book_id}", json={"available": False})
    assert update_resp.status_code == 200
    assert update_resp.get_json()["available"] is False


def test_delete_book(client, sample_author):
    create_resp = client.post("/api/v1/books", json={
        "title": "1984", "isbn": "9780451524935", "year": 1949,
        "genre": "Dystopie", "available": True, "author_id": sample_author.id,
    })
    book_id = create_resp.get_json()["id"]

    delete_resp = client.delete(f"/api/v1/books/{book_id}")
    assert delete_resp.status_code == 204

    get_resp = client.get(f"/api/v1/books/{book_id}")
    assert get_resp.status_code == 404