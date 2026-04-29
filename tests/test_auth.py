def test_register_success(client):
    response = client.post("/auth/register", json={
        "username": "aastha",
        "password": "123456"
    })

    assert response.status_code == 200
    assert response.json()["message"] == "User created"

def test_register_duplicate_username(client):
    payload = {
        "username": "john",
        "password": "123456"
    }

    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)

    assert response.status_code in [400, 409]

def test_login_success(client):
    client.post("/auth/register", json={
        "username": "john",
        "password": "123456"
    })

    response = client.post("/auth/login", json={
        "username": "john",
        "password": "123456"
    })

    assert response.status_code == 200
    assert response.json()["message"] == "Login successful"
    assert "set-cookie" in response.headers


def test_login_invalid_password(client):
    response = client.post("/auth/login", json={
        "username": "john",
        "password": "wrong"
    })

    assert response.status_code == 200
    assert response.json()["error"] == "Invalid credentials"


def test_me_without_token(client):
    response = client.get("/me")

    assert response.status_code == 401