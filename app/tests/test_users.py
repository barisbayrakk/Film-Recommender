# Pytest async test desteği
import pytest
# FastAPI async endpoint’lerini test etmek için
from httpx import AsyncClient
# Test edilecek FastAPI uygulaması
from app.main import app

# ---------------------------------------
# USER LIST TEST
# ---------------------------------------
@pytest.mark.asyncio
async def test_list_users():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.get("/users/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

# ---------------------------------------
# USER DETAIL TEST
# ---------------------------------------
@pytest.mark.asyncio
async def test_get_user_detail():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # önce yeni kullanıcı oluştur
        create = await ac.post(
            "/auth/register",
            json={
                "username": "user_detail",
                "email": "detail@example.com",
                "password": "1234",
                "name": "Detail User",
            },
        )
        assert create.status_code == 201

        # user_id her zaman 1 olmayabilir, token’den alamıyoruz
        # bu yüzden listeyi çekip son eklenen user’ın id’sini alıyoruz
        users = await ac.get("/users/")
        user_id = users.json()[-1]["id"]

        # şimdi detay endpointini test et
        resp = await ac.get(f"/users/{user_id}")

    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == user_id
    assert data["username"] == "user_detail"


@pytest.mark.asyncio
async def test_update_user():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # 1. Yeni kullanıcı oluştur
        create = await ac.post(
            "/auth/register",
            json={
                "username": "user_update",
                "email": "update@example.com",
                "password": "1234",
                "name": "Update User",
            },
        )
        assert create.status_code == 201

        # 2. user_id al
        users = await ac.get("/users/")
        user_id = users.json()[-1]["id"]

        # 3. update isteği gönder
        resp = await ac.put(
            f"/users/{user_id}",
            json={
                "username": "updated_user",
                "email": "updated@example.com",
                "name": "Updated Name",
                "password": "yeni1234"
            },
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "updated_user"
    assert data["email"] == "updated@example.com"
