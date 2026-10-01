# Pytest test framework
import pytest
from httpx import AsyncClient
from app.main import app

# ---------------------------------------
# REGISTER TEST
# ---------------------------------------
@pytest.mark.asyncio
async def test_register():
    """
    /auth/register endpoint'i düzgün çalışıyor mu?
    201 dönmeli ve access_token içermeli.
    """
    # AsyncClient ile FastAPI app'i test modunda ayağa kaldır
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/auth/register",
            json={
                "username": "testuser_register",
                "email": "test_register@example.com",
                "password": "1234",
                "name": "Test Register",
            },
        )
    # Status code kontrolü
    assert response.status_code == 201
    # Response body JSON'a çevir
    data = response.json()
     # Token alanları var mı?
    assert "access_token" in data
    assert data["token_type"] == "bearer"

# ---------------------------------------
# LOGIN (SUCCESS) TEST
# ---------------------------------------
@pytest.mark.asyncio
async def test_login_success():
    """
    1) Önce bir kullanıcı register et
    2) Sonra /auth/login ile aynı email + şifreyi kullan
    200 dönmeli ve access_token gelmeli.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # 1. Kullanıcı oluştur
        register_resp = await ac.post(
            "/auth/register",
            json={
                "username": "testuser_login",
                "email": "test_login@example.com",
                "password": "1234",
                "name": "Test Login",
            },
        )
        assert register_resp.status_code == 201

        # 2. Login dene
        login_resp = await ac.post(
            "/auth/login",
            json={
                "email": "test_login@example.com",
                "password": "1234",
            },
        )

    assert login_resp.status_code == 200
    data = login_resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


# ---------------------------------------
# LOGIN (WRONG PASSWORD) TEST
# ---------------------------------------
@pytest.mark.asyncio
async def test_login_wrong_password():
    """
    Yanlış şifre ile login denendiğinde
    400 ve 'Invalid email or password' dönüyor mu?
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # 1. Kullanıcı oluştur
        register_resp = await ac.post(
            "/auth/register",
            json={
                "username": "testuser_wrongpass",
                "email": "wrongpass@example.com",
                "password": "dogru_sifre",
                "name": "Wrong Pass User",
            },
        )
        assert register_resp.status_code == 201

        # 2. Bu sefer yanlış şifre ile login dene
        login_resp = await ac.post(
            "/auth/login",
            json={
                "email": "wrongpass@example.com",
                "password": "yanlis_sifre",
            },
        )

    assert login_resp.status_code == 400
    data = login_resp.json()
    assert data["detail"] == "Invalid email or password"
