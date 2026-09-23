def test_register_user(client):
    response = client.post("/api/v1/auth/register", json={
        "email": "alice@example.com",
        "username": "alice",
        "password": "motdepasse123",
        "role": "member",
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["username"] == "alice"
    assert "password" not in data
    assert "password_hash" not in data


def test_register_duplicate_user(client):
    payload = {
        "email": "alice@example.com",
        "username": "alice",
        "password": "motdepasse123",
    }
    client.post("/api/v1/auth/register", json=payload)
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409


def test_register_invalid_role(client):
    response = client.post("/api/v1/auth/register", json={
        "email": "bob@example.com",
        "username": "bob",
        "password": "motdepasse123",
        "role": "admin",  # rôle invalide
    })
    assert response.status_code == 422


def test_login_success(client):
    client.post("/api/v1/auth/register", json={
        "email": "alice@example.com",
        "username": "alice",
        "password": "motdepasse123",
    })
    response = client.post("/api/v1/auth/login", json={
        "username": "alice",
        "password": "motdepasse123",
    })
    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_wrong_password(client):
    client.post("/api/v1/auth/register", json={
        "email": "alice@example.com",
        "username": "alice",
        "password": "motdepasse123",
    })
    response = client.post("/api/v1/auth/login", json={
        "username": "alice",
        "password": "mauvais_mdp",
    })
    assert response.status_code == 401


def test_me_without_token(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_me_with_token(client):
    client.post("/api/v1/auth/register", json={
        "email": "alice@example.com",
        "username": "alice",
        "password": "motdepasse123",
    })
    login_resp = client.post("/api/v1/auth/login", json={
        "username": "alice",
        "password": "motdepasse123",
    })
    token = login_resp.get_json()["access_token"]

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.get_json()["username"] == "alice"