def test_list_authors_empty(client):
    response = client.get("/api/v1/authors")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_author(client):
    payload = {"name": "George Orwell", "nationality": "British", "bio": "Écrivain britannique"}
    response = client.post("/api/v1/authors", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "George Orwell"
    assert data["id"] is not None


def test_create_author_missing_name(client):
    response = client.post("/api/v1/authors", json={"nationality": "British"})
    assert response.status_code == 422


def test_get_author_not_found(client):
    response = client.get("/api/v1/authors/999")
    assert response.status_code == 404


def test_get_author_books(client, sample_author):
    book_payload = {
        "title": "1984", "isbn": "9780451524935", "year": 1949,
        "genre": "Dystopie", "available": True, "author_id": sample_author.id,
    }
    client.post("/api/v1/books", json=book_payload)

    response = client.get(f"/api/v1/authors/{sample_author.id}/books")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["title"] == "1984"


def test_get_books_of_nonexistent_author(client):
    response = client.get("/api/v1/authors/999/books")
    assert response.status_code == 404


def test_update_author(client, sample_author):
    response = client.put(f"/api/v1/authors/{sample_author.id}", json={"nationality": "English"})
    assert response.status_code == 200
    assert response.get_json()["nationality"] == "English"


def test_delete_author(client, sample_author):
    response = client.delete(f"/api/v1/authors/{sample_author.id}")
    assert response.status_code == 204

    get_resp = client.get(f"/api/v1/authors/{sample_author.id}")
    assert get_resp.status_code == 404