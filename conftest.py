
import sqlite3

import pytest
from fastapi.testclient import TestClient

import database


@pytest.fixture
def client(monkeypatch):
    # Seleciona o banco de testes antes de importar a aplicação
    monkeypatch.setattr(database, "in_test", True)

    db_path = database.get_database()

    with sqlite3.connect(db_path) as conn:
        conn.executescript("""
            DROP TABLE IF EXISTS recommendations;
            DROP TABLE IF EXISTS favorites;
            DROP TABLE IF EXISTS users;

            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                login TEXT,
                password_hash TEXT,
                role TEXT
            );

            CREATE UNIQUE INDEX idx_users_login
            ON users(login);

            CREATE TABLE favorites (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                artist_id TEXT NOT NULL,
                artist_name TEXT NOT NULL,
                UNIQUE(user_id, artist_id)
            );

            CREATE TABLE recommendations (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                artist_id TEXT NOT NULL,
                artist_name TEXT NOT NULL,
                recommended_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, artist_id)
            );
        """)

    # Importa a aplicação somente depois de selecionar o banco de testes
    from main import app

    with TestClient(app) as test_client:
        yield test_client
