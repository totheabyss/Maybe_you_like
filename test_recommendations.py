
from unittest.mock import patch


def criar_usuario_e_token(client):
    client.post(
        "/users",
        json={"login": "teste", "password": "senha123"}
    )

    resposta = client.post(
        "/login",
        json={"login": "teste", "password": "senha123"}
    )

    return {
        "Authorization": f"Bearer {resposta.json()['access_token']}"
    }


def adicionar_favorito(client, headers):
    with patch(
        "favorites.get_artist_info",
        return_value={
            "name": "Metallica",
            "id": "metallica-id",
            "listeners": "50000"
        }
    ):
        return client.post(
            "/users/me/favorites",
            json={"artist_name": "Metallica"},
            headers=headers
        )


def test_get_recommendation(client):
    headers = criar_usuario_e_token(client)
    adicionar_favorito(client, headers)

    recomendacao = {
        "name": "Evile",
        "id": "evile-id",
        "match": "0.8",
        "position": 25,
        "listeners": "50000"
    }

    with patch(
        "recommendations.get_recommendation",
        return_value=[recomendacao]
    ):
        resposta = client.get(
            "/users/me/recommendations",
            headers=headers
        )

    assert resposta.status_code == 200
    assert resposta.json()["name"] == "Evile"
    assert resposta.json()["id"] == "evile-id"


def test_no_favorites_to_recommend(client):
    headers = criar_usuario_e_token(client)

    resposta = client.get(
        "/users/me/recommendations",
        headers=headers
    )

    assert resposta.status_code == 409


def test_empty_recommendation_list(client):
    headers = criar_usuario_e_token(client)
    adicionar_favorito(client, headers)

    with patch(
        "recommendations.get_recommendation",
        return_value=[]
    ):
        resposta = client.get(
            "/users/me/recommendations",
            headers=headers
        )

    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "No new recommendations available"
