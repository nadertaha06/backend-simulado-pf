"""
Autenticação com Auth0 (JWT RS256) e checagem de roles.

Normalmente NÃO precisa mexer aqui na prova. Para mudar quem acessa cada
rota, edite ROLES_* em config.py ou use exigir_roles(...) direto na rota.
"""

from dataclasses import dataclass, field

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app import config

bearer = HTTPBearer(auto_error=False)
_jwks_client: jwt.PyJWKClient | None = None


@dataclass
class Usuario:
    sub: str
    email: str | None
    roles: list[str] = field(default_factory=list)
    claims: dict = field(default_factory=dict)


def _get_jwks_client() -> jwt.PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        _jwks_client = jwt.PyJWKClient(f"https://{config.AUTH0_DOMAIN}/.well-known/jwks.json")
    return _jwks_client


def _nao_autorizado(msg: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=msg,
        headers={"WWW-Authenticate": "Bearer"},
    )


def validar_token(token: str) -> dict:
    if not config.AUTH0_DOMAIN or not config.AUTH0_AUDIENCE:
        raise HTTPException(500, "AUTH0_DOMAIN e AUTH0_AUDIENCE não configurados no servidor")
    try:
        chave = _get_jwks_client().get_signing_key_from_jwt(token).key
        return jwt.decode(
            token,
            chave,
            algorithms=["RS256"],
            audience=config.AUTH0_AUDIENCE,
            issuer=f"https://{config.AUTH0_DOMAIN}/",
        )
    except jwt.PyJWTError as e:
        raise _nao_autorizado(f"Token inválido: {e}")


def get_usuario(cred: HTTPAuthorizationCredentials | None = Depends(bearer)) -> Usuario:
    """Qualquer usuário logado (sem checar role)."""
    if cred is None:
        raise _nao_autorizado("Token não enviado")
    claims = validar_token(cred.credentials)
    roles = claims.get(config.ROLES_CLAIM) or []
    return Usuario(
        sub=claims.get("sub", ""),
        email=claims.get(config.EMAIL_CLAIM) or claims.get("email"),
        roles=[str(r).upper() for r in roles],
        claims=claims,
    )


def exigir_roles(*roles_permitidas: str):
    """Uso: usuario: Usuario = Depends(exigir_roles("ADMIN", "USER"))"""
    permitidas = {r.upper() for r in roles_permitidas}

    def checar(usuario: Usuario = Depends(get_usuario)) -> Usuario:
        if not permitidas & set(usuario.roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Precisa de uma das roles: {sorted(permitidas)}",
            )
        return usuario

    return checar
