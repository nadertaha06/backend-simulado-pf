"""
Testes da API. Rodar com:  .venv/bin/pytest -q

Os tokens são JWT RS256 de verdade, assinados com uma chave gerada aqui;
só a busca da chave pública no Auth0 (JWKS) é trocada por essa chave local.
"""

import time
from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app import auth, config
from app.database import get_session
from app.main import app

DOMINIO = "teste.us.auth0.com"
AUDIENCE = "https://avaliacoes-api"
CHAVE = rsa.generate_private_key(public_exponent=65537, key_size=2048)
ROTA = config.ROTA


def gerar_token(roles=None, email="admin@empresa.com", audience=AUDIENCE, exp_em=3600):
    payload = {
        "sub": "auth0|123",
        "iss": f"https://{DOMINIO}/",
        "aud": audience,
        "iat": int(time.time()),
        "exp": int(time.time()) + exp_em,
        config.ROLES_CLAIM: roles or [],
    }
    if email:
        payload[config.EMAIL_CLAIM] = email
    return jwt.encode(payload, CHAVE, algorithm="RS256")


def header(**kwargs):
    return {"Authorization": f"Bearer {gerar_token(**kwargs)}"}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(config, "AUTH0_DOMAIN", DOMINIO)
    monkeypatch.setattr(config, "AUTH0_AUDIENCE", AUDIENCE)
    jwks_falso = SimpleNamespace(get_signing_key_from_jwt=lambda t: SimpleNamespace(key=CHAVE.public_key()))
    monkeypatch.setattr(auth, "_get_jwks_client", lambda: jwks_falso)

    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    def session_teste():
        with Session(engine) as s:
            yield s

    app.dependency_overrides[get_session] = session_teste
    yield TestClient(app)
    app.dependency_overrides.clear()


AVALIACAO = {"emailAvaliado": "joao@empresa.com", "comentarios": "Ótimo trabalho", "nota": 9}


def test_admin_cadastra_e_avaliador_vem_do_token(client):
    r = client.post(ROTA, json=AVALIACAO, headers=header(roles=["ADMIN"]))
    assert r.status_code == 201, r.text
    corpo = r.json()
    assert corpo["id"] == 1
    assert corpo["emailAvaliador"] == "admin@empresa.com"
    assert corpo["emailAvaliado"] == "joao@empresa.com"
    assert corpo["nota"] == 9
    assert corpo["dataAvaliacao"]


def test_user_nao_pode_cadastrar(client):
    r = client.post(ROTA, json=AVALIACAO, headers=header(roles=["USER"]))
    assert r.status_code == 403


def test_admin_e_user_listam(client):
    client.post(ROTA, json=AVALIACAO, headers=header(roles=["ADMIN"]))
    for role in ["ADMIN", "USER"]:
        r = client.get(ROTA, headers=header(roles=[role]))
        assert r.status_code == 200
        assert len(r.json()) == 1


def test_sem_role_nao_lista(client):
    assert client.get(ROTA, headers=header(roles=[])).status_code == 403


def test_sem_token_401(client):
    assert client.get(ROTA).status_code == 401
    assert client.post(ROTA, json=AVALIACAO).status_code == 401


def test_token_audience_errada_401(client):
    assert client.get(ROTA, headers=header(roles=["ADMIN"], audience="outra")).status_code == 401


def test_token_expirado_401(client):
    assert client.get(ROTA, headers=header(roles=["ADMIN"], exp_em=-10)).status_code == 401


@pytest.mark.parametrize("nota", [-1, 11])
def test_nota_fora_de_0_a_10_422(client, nota):
    r = client.post(ROTA, json={**AVALIACAO, "nota": nota}, headers=header(roles=["ADMIN"]))
    assert r.status_code == 422


def test_email_invalido_422(client):
    r = client.post(ROTA, json={**AVALIACAO, "emailAvaliado": "nao-e-email"}, headers=header(roles=["ADMIN"]))
    assert r.status_code == 422


def test_avaliador_pelo_corpo_quando_token_sem_email(client):
    corpo = {**AVALIACAO, "emailAvaliador": "chefe@empresa.com"}
    r = client.post(ROTA, json=corpo, headers=header(roles=["ADMIN"], email=None))
    assert r.status_code == 201
    assert r.json()["emailAvaliador"] == "chefe@empresa.com"


def test_health_publico(client):
    assert client.get("/health").json() == {"status": "ok"}
