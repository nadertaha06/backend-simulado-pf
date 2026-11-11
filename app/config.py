"""
=====================================================================
 ⭐ CONFIGURAÇÕES — o que mais muda na prova está AQUI
=====================================================================
 - ROTA ..................... caminho base das rotas (ex.: "/avaliacoes")
 - ROLES_CADASTRAR .......... quem pode fazer POST
 - ROLES_LISTAR ............. quem pode fazer GET
 - ROLES_CLAIM / EMAIL_CLAIM  nome dos claims que a Action do Auth0 coloca no token

 Os dados do Auth0 (domínio e audience) vêm de variáveis de ambiente:
 localmente pelo arquivo .env e na AWS pelos secrets do GitHub Actions.
=====================================================================
"""

import os

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------
# ⭐ ROTAS E PERMISSÕES
# ---------------------------------------------------------------------
ROTA = "/avaliacoes"

ROLES_CADASTRAR = ["ADMIN"]          # POST /avaliacoes
ROLES_LISTAR = ["ADMIN", "USER"]     # GET  /avaliacoes

# ---------------------------------------------------------------------
# AUTH0 (vem do .env ou das variáveis do container)
# ---------------------------------------------------------------------
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "")        # ex.: dev-xxxx.us.auth0.com
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE", "")    # ex.: https://avaliacoes-api

# ⭐ Precisa ser IGUAL ao namespace usado na Action do Auth0 (veja o README)
NAMESPACE = os.getenv("AUTH0_NAMESPACE", "https://avaliacoes-insper.com")
ROLES_CLAIM = f"{NAMESPACE}/roles"
EMAIL_CLAIM = f"{NAMESPACE}/email"

# ---------------------------------------------------------------------
# BANCO E CORS
# ---------------------------------------------------------------------
# Local: arquivo ./avaliacoes.db | Docker: /data/avaliacoes.db (definido no Dockerfile)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./avaliacoes.db")

# "*" libera qualquer front. Para restringir: "https://meu-front.vercel.app,http://localhost:5173"
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
