"""
=====================================================================
 ⭐ ROTAS — o que cada rota faz e o que ela lista fica AQUI
=====================================================================
 O caminho base vem de config.ROTA ("/avaliacoes").
 Quem pode acessar vem de config.ROLES_CADASTRAR / config.ROLES_LISTAR.

 No fim do arquivo há EXEMPLOS PRONTOS (comentados) das mudanças que
 costumam cair: buscar por id, deletar, atualizar, filtrar pelo usuário
 logado, filtrar por query param...
=====================================================================
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app import config
from app.auth import Usuario, exigir_roles
from app.database import get_session
from app.models import Avaliacao, AvaliacaoCreate

router = APIRouter(prefix=config.ROTA, tags=["avaliacoes"])


# POST /avaliacoes  (ADMIN)
@router.post("", response_model=Avaliacao, status_code=201)
def cadastrar(
    dados: AvaliacaoCreate,
    usuario: Usuario = Depends(exigir_roles(*config.ROLES_CADASTRAR)),
    session: Session = Depends(get_session),
):
    # O avaliador é o usuário logado (email vem do token).
    email_avaliador = usuario.email or dados.emailAvaliador
    if not email_avaliador:
        raise HTTPException(400, "Email do avaliador não veio no token nem no corpo da requisição")

    avaliacao = Avaliacao(
        **dados.model_dump(exclude={"emailAvaliador"}),
        emailAvaliador=email_avaliador,
    )
    session.add(avaliacao)
    session.commit()
    session.refresh(avaliacao)
    return avaliacao


# GET /avaliacoes  (ADMIN e USER)
@router.get("", response_model=list[Avaliacao])
def listar(
    usuario: Usuario = Depends(exigir_roles(*config.ROLES_LISTAR)),
    session: Session = Depends(get_session),
):
    # ⭐ O QUE É LISTADO: troque a query abaixo (veja exemplos no fim do arquivo)
    query = select(Avaliacao).order_by(Avaliacao.dataAvaliacao.desc())
    return session.exec(query).all()


# =====================================================================
# EXEMPLOS PRONTOS: descomente e ajuste se a prova pedir
# =====================================================================
#
# --- Listar só as avaliações EM QUE o usuário logado é o AVALIADO ---
#     (troque a query do listar() acima por esta)
#   query = select(Avaliacao).where(Avaliacao.emailAvaliado == usuario.email)
#
# --- Listar só as que o usuário logado FEZ (avaliador) ---
#   query = select(Avaliacao).where(Avaliacao.emailAvaliador == usuario.email)
#
# --- ADMIN vê tudo, USER vê só as dele ---
#   query = select(Avaliacao)
#   if "ADMIN" not in usuario.roles:
#       query = query.where(Avaliacao.emailAvaliado == usuario.email)
#
# --- Filtro opcional por query param: GET /avaliacoes?notaMinima=7 ---
#   def listar(notaMinima: int | None = None, usuario=..., session=...):
#       query = select(Avaliacao)
#       if notaMinima is not None:
#           query = query.where(Avaliacao.nota >= notaMinima)
#
# --- GET /avaliacoes/{id} ---
# @router.get("/{id}", response_model=Avaliacao)
# def buscar(id: int,
#            usuario: Usuario = Depends(exigir_roles("ADMIN", "USER")),
#            session: Session = Depends(get_session)):
#     avaliacao = session.get(Avaliacao, id)
#     if not avaliacao:
#         raise HTTPException(404, "Avaliação não encontrada")
#     return avaliacao
#
# --- DELETE /avaliacoes/{id} (ADMIN) ---
# @router.delete("/{id}", status_code=204)
# def deletar(id: int,
#             usuario: Usuario = Depends(exigir_roles("ADMIN")),
#             session: Session = Depends(get_session)):
#     avaliacao = session.get(Avaliacao, id)
#     if not avaliacao:
#         raise HTTPException(404, "Avaliação não encontrada")
#     session.delete(avaliacao)
#     session.commit()
#
# --- PUT /avaliacoes/{id} (ADMIN) ---
# @router.put("/{id}", response_model=Avaliacao)
# def atualizar(id: int, dados: AvaliacaoCreate,
#               usuario: Usuario = Depends(exigir_roles("ADMIN")),
#               session: Session = Depends(get_session)):
#     avaliacao = session.get(Avaliacao, id)
#     if not avaliacao:
#         raise HTTPException(404, "Avaliação não encontrada")
#     for campo, valor in dados.model_dump(exclude={"emailAvaliador"}).items():
#         setattr(avaliacao, campo, valor)
#     session.commit()
#     session.refresh(avaliacao)
#     return avaliacao
