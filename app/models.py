"""
=====================================================================
 ⭐ ENTIDADE — os campos ficam AQUI
=====================================================================
 - AvaliacaoBase ... campos que o front ENVIA no POST (e que também são salvos)
 - AvaliacaoCreate . o corpo do POST (Base + extras opcionais)
 - Avaliacao ....... a tabela do banco = o que o GET devolve
                     (Base + campos gerados pelo servidor: id, avaliador, data)

 Para ADICIONAR um campo que o usuário preenche: coloque em AvaliacaoBase.
 Para um campo que o SERVIDOR preenche (data, usuário logado...): coloque em
 Avaliacao e preencha em routes.py.

 Os nomes estão em camelCase de propósito: assim o JSON sai igual
 ({"emailAvaliado": ...}) sem precisar de alias.

 ⚠️ Mudou campo? Apague o arquivo avaliacoes.db (local) ou o volume na AWS
    (docker volume rm api-data), porque o SQLite não altera tabela existente.
=====================================================================
"""

from datetime import datetime, timezone

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


def agora() -> datetime:
    return datetime.now(timezone.utc)


class AvaliacaoBase(SQLModel):
    emailAvaliado: EmailStr
    comentarios: str = Field(min_length=1)
    nota: int = Field(ge=0, le=10)          # ⭐ nota de 0 a 10 (troque int por float se aceitar 7.5)


class AvaliacaoCreate(AvaliacaoBase):
    # Só é usado se o token NÃO trouxer o email do usuário logado.
    emailAvaliador: EmailStr | None = None


class Avaliacao(AvaliacaoBase, table=True):
    __tablename__ = "avaliacoes"

    id: int | None = Field(default=None, primary_key=True)
    emailAvaliador: str
    dataAvaliacao: datetime = Field(default_factory=agora)
