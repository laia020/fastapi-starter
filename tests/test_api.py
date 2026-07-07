import os

os.environ["APP_DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["APP_JWT_SECRET_KEY"] = "test-secret-key-with-at-least-32-bytes"

from fastapi.testclient import TestClient

from app.db.database import Base, engine
from app.main import app


def reset_database() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def register_user(
    client: TestClient,
    *,
    name: str = "Ana Silva",
    email: str = "ana@example.com",
    password: str = "strongpass123",
) -> dict:
    response = client.post(
        "/auth/register",
        json={
            "name": name,
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 201
    return response.json()


def login_user(
    client: TestClient,
    *,
    email: str = "ana@example.com",
    password: str = "strongpass123",
) -> str:
    response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )

    assert response.status_code == 200
    return response.json()["access_token"]


def test_health_check() -> None:
    reset_database()

    with TestClient(app) as client:
        response = client.get("/health")
        db_response = client.get("/health/db")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert db_response.status_code == 200
    assert db_response.json()["database"] == "connected"


def test_register_login_and_get_me() -> None:
    reset_database()

    with TestClient(app) as client:
        user = register_user(client)
        token = login_user(client)
        me_response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert user["email"] == "ana@example.com"
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "ana@example.com"


def test_reject_duplicate_register() -> None:
    reset_database()

    with TestClient(app) as client:
        register_user(client)
        response = client.post(
            "/auth/register",
            json={
                "name": "Ana Silva",
                "email": "ana@example.com",
                "password": "strongpass123",
            },
        )

    assert response.status_code == 400


def test_reject_invalid_login() -> None:
    reset_database()

    with TestClient(app) as client:
        register_user(client)
        response = client.post(
            "/auth/login",
            data={
                "username": "ana@example.com",
                "password": "wrong-password",
            },
        )

    assert response.status_code == 401


def test_documents_require_authentication() -> None:
    reset_database()

    with TestClient(app) as client:
        response = client.get("/documents")

    assert response.status_code == 401


def test_authenticated_document_flow() -> None:
    reset_database()

    with TestClient(app) as client:
        user = register_user(client)
        token = login_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        create_response = client.post(
            "/documents",
            json={
                "title": "Primeiro documento",
                "content": "Conteudo do documento.",
            },
            headers=headers,
        )
        document = create_response.json()

        list_response = client.get(
            "/documents",
            params={"limit": 20, "offset": 0},
            headers=headers,
        )
        get_response = client.get(
            f"/documents/{document['id']}",
            headers=headers,
        )
        delete_response = client.delete(
            f"/documents/{document['id']}",
            headers=headers,
        )
        not_found_response = client.get(
            f"/documents/{document['id']}",
            headers=headers,
        )

    assert create_response.status_code == 201
    assert document["owner_id"] == user["id"]
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert get_response.status_code == 200
    assert delete_response.status_code == 204
    assert not_found_response.status_code == 404


def test_user_cannot_access_another_user_document() -> None:
    reset_database()

    with TestClient(app) as client:
        register_user(client)
        ana_token = login_user(client)
        ana_headers = {"Authorization": f"Bearer {ana_token}"}
        create_response = client.post(
            "/documents",
            json={
                "title": "Documento privado",
                "content": "Conteudo privado.",
            },
            headers=ana_headers,
        )
        document = create_response.json()

        register_user(
            client,
            name="Bruno Lima",
            email="bruno@example.com",
            password="anotherpass123",
        )
        bruno_token = login_user(
            client,
            email="bruno@example.com",
            password="anotherpass123",
        )
        bruno_headers = {"Authorization": f"Bearer {bruno_token}"}

        get_response = client.get(
            f"/documents/{document['id']}",
            headers=bruno_headers,
        )
        list_response = client.get("/documents", headers=bruno_headers)
        delete_response = client.delete(
            f"/documents/{document['id']}",
            headers=bruno_headers,
        )

    assert create_response.status_code == 201
    assert get_response.status_code == 404
    assert list_response.status_code == 200
    assert list_response.json() == []
    assert delete_response.status_code == 404
