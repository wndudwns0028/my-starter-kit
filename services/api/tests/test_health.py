import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_liveness():
  response = client.get("/health/live")
  assert response.status_code == 200
  assert response.json()["status"] == "ok"


def test_root():
  response = client.get("/")
  assert response.status_code == 200
  assert response.json()["service"] == "devops-starter-api"


def test_create_and_get_item():
  # 생성
  response = client.post(
    "/api/v1/items",
    json={"name": "테스트 아이템", "description": "설명", "price": 9900},
  )
  assert response.status_code == 201
  item_id = response.json()["id"]

  # 조회
  response = client.get(f"/api/v1/items/{item_id}")
  assert response.status_code == 200
  assert response.json()["name"] == "테스트 아이템"


def test_item_not_found():
  response = client.get("/api/v1/items/99999")
  assert response.status_code == 404
