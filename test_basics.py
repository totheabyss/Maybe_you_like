import pytest
from request import get_artist_info,get_recommendation
from unittest.mock import Mock
import hashlib
import requests


def test_artist_info(monkeypatch):
    resposta = Mock()

    resposta.json.return_value = {
        "artist": {
            "name": "Metallica",
            "mbid": "id-falso-123",
            "stats": {
                "listeners": "50000"
            }
        }
    }
    mock_resposta = Mock(return_value=resposta)
    monkeypatch.setattr("request.requests.get",mock_resposta)
    resultado = get_artist_info("Metallica")
    assert mock_resposta.call_args.kwargs["params"] == {'method': 'artist.getInfo', 'artist': 'Metallica', 'api_key': 'de61432abee4cd4a428549a4f960f19e', 'format': 'json'}
    assert resultado["name"] == "Metallica"
    assert resultado["id"] == "id-falso-123"
    assert resultado["listeners"] == "50000"

def test_error_six(monkeypatch):
    resposta = Mock()
    resposta.json.return_value = {
    "error": 6,
    "message": "Artist not found"
    }
    monkeypatch.setattr("request.requests.get",Mock(return_value=resposta))
    with pytest.raises(FileNotFoundError):
        get_artist_info("a")
    
def test_no_id(monkeypatch):
    resposta = Mock()
   
    resposta.json.return_value = {
        "artist": {
        "name": "Metallica",
        "mbid": None,
        "stats": {
            "listeners": "50000"
            }
        }
    }
    monkeypatch.setattr("request.requests.get",Mock(return_value=resposta))    
    result = get_artist_info("Metallica")
    artist_id = hashlib.sha256(result["name"].lower().encode()).hexdigest()
    assert result["id"] == artist_id

def test_http_error(monkeypatch):
    resposta = Mock()
    resposta.raise_for_status.side_effect = requests.HTTPError("Erro HTTP")

    monkeypatch.setattr("request.requests.get",Mock(return_value=resposta))

    with pytest.raises(requests.HTTPError):
        get_artist_info("Metallica")


def test_artist_recommendation(monkeypatch):
    lista = []

    for i in range(0, 61):
        lista.append({
            "name": f"Artista {i}",
            "match": "1"
        })

    def resposta_api(url, params):
        resposta = Mock()

        if params["method"] == "artist.getSimilar":
            resposta.json.return_value = {
                "similarartists": {
                    "artist": lista
                }
            }

        elif params["method"] == "artist.getInfo":
            resposta.json.return_value = {
                "artist": {
                    "name": params["artist"],
                    "mbid": f"id-{params['artist']}",
                    "stats": {
                        "listeners": "50000"
                    }
                }
            }

        return resposta

    mock_resposta = Mock(side_effect=resposta_api)
    monkeypatch.setattr("request.requests.get", mock_resposta)

    resultado = get_recommendation("Metallica")

    assert mock_resposta.call_args_list[0].kwargs["params"] == {
        "method": "artist.getSimilar",
        "artist": "Metallica",
        "api_key": "de61432abee4cd4a428549a4f960f19e",
        "format": "json"
    }

    assert len(resultado) == 39
    assert resultado[0]["position"] == 21
    assert resultado[-1]["position"] == 59
    assert resultado[0]["name"] == "Artista 20"
    assert resultado[0]["listeners"] == "50000"
    assert resultado[0]["id"] == "id-Artista 20"

