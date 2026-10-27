
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


def test_add_favorite(client):
    headers = criar_usuario_e_token(client)

    with patch(
        "favorites.get_artist_info",
        return_value={
            "name": "Metallica",
            "id": "metallica-id",
            "listeners": "50000"
        }
    ):
        resposta = client.post(
            "/users/me/favorites",
            json={"artist_name": "Metallica"},
            headers=headers
        )

    assert resposta.status_code == 200

    resposta_lista = client.get(
        "/users/me/favorites",
        headers=headers
    )

    assert resposta_lista.status_code == 200
    assert resposta_lista.json()[0]["artist_name"] == "Metallica"


def test_duplicate_favorite(client):
    headers = criar_usuario_e_token(client)

    with patch(
        "favorites.get_artist_info",
        return_value={
            "name": "Metallica",
            "id": "metallica-id",
            "listeners": "50000"
        }
    ):
        primeira = client.post(
            "/users/me/favorites",
            json={"artist_name": "Metallica"},
            headers=headers
        )

        segunda = client.post(
            "/users/me/favorites",
            json={"artist_name": "Metallica"},
            headers=headers
        )

    assert primeira.status_code == 200
    assert segunda.status_code == 409


def test_delete_favorite(client):
    headers = criar_usuario_e_token(client)

    with patch(
        "favorites.get_artist_info",
        return_value={
            "name": "Metallica",
            "id": "metallica-id",
            "listeners": "50000"
        }
    ):
        client.post(
            "/users/me/favorites",
            json={"artist_name": "Metallica"},
            headers=headers
        )

    favoritos = client.get(
        "/users/me/favorites",
        headers=headers
    ).json()

    favorite_id = favoritos[0]["id"]

    resposta = client.delete(
        f"/users/me/favorites/{favorite_id}",
        headers=headers
    )

    assert resposta.status_code == 200
    assert resposta.json() == "Band Deleted"

    lista_final = client.get(
        "/users/me/favorites",
        headers=headers
    )

    assert lista_final.json() == []
