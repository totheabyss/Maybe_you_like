
import sqlite3

import pytest
from fastapi.testclient import TestClient

import database



def test_create_user(client):
    resposta = client.post(
        "/users",
        json={"login": "teste", "password": "senha123"}
    )

    assert resposta.status_code == 200


def test_duplicate_user(client):
    dados = {"login": "teste", "password": "senha123"}

    client.post("/users", json=dados)
    resposta = client.post("/users", json=dados)

    assert resposta.status_code == 409


def test_login_success(client):
    client.post(
        "/users",
        json={"login": "teste", "password": "senha123"}
    )

    resposta = client.post(
        "/login",
        json={"login": "teste", "password": "senha123"}
    )

    assert resposta.status_code == 200
    assert resposta.json()["token_type"] == "Bearer"
    assert "access_token" in resposta.json()


def test_login_wrong_password(client):
    client.post(
        "/users",
        json={"login": "teste", "password": "senha123"}
    )

    resposta = client.post(
        "/login",
        json={"login": "teste", "password": "errada"}
    )

    assert resposta.status_code == 401


def test_invalid_token(client):
    resposta = client.get(
        "/users/me/favorites",
        headers={"Authorization": "Bearer token-invalido"}
    )

    assert resposta.status_code == 401
