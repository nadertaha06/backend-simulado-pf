# Backend: API de Avaliações (FastAPI + Auth0)

| Rota | Quem acessa | O que faz |
|---|---|---|
| `POST /avaliacoes` | ADMIN | cadastra uma avaliação (o avaliador é o usuário logado) |
| `GET /avaliacoes` | ADMIN, USER | lista as avaliações (mais recentes primeiro) |
| `GET /health` | público | só para checar se o container subiu |
| `GET /docs` | público | Swagger (as rotas pedem o token) |

Entidade **Avaliação**: `id`, `emailAvaliador`, `emailAvaliado`, `comentarios`, `nota` (0 a 10), `dataAvaliacao`.

Exemplo de POST:

```json
{ "emailAvaliado": "joao@empresa.com", "comentarios": "Ótimo trabalho", "nota": 9 }
```

`id`, `emailAvaliador` (vem do token) e `dataAvaliacao` (agora, em UTC) são preenchidos pelo servidor.

---

## ⭐ Onde mudar cada coisa na prova

| A prova pede… | Backend | Frontend |
|---|---|---|
| **Mudar a rota** (`/avaliacoes` → `/feedbacks`) | `ROTA` em [app/config.py](app/config.py) | `ROTA` em `src/config.js` |
| **Mudar quem pode cadastrar/listar** | `ROLES_CADASTRAR` / `ROLES_LISTAR` em [app/config.py](app/config.py) | `ROLES_PODE_CADASTRAR` em `src/config.js` |
| **Mudar o que o GET lista** (só as do usuário logado, filtro por nota…) | a `query` dentro de `listar()` em [app/routes.py](app/routes.py); tem exemplos prontos no fim do arquivo | nada |
| **Adicionar / remover / renomear campo** que o usuário preenche | `AvaliacaoBase` em [app/models.py](app/models.py) | lista `CAMPOS` em `src/config.js` |
| **Campo que o servidor preenche** (status padrão, usuário logado…) | classe `Avaliacao` em [app/models.py](app/models.py) + preencher em `cadastrar()` em [app/routes.py](app/routes.py) | `CAMPOS` com `noForm: false` |
| **Nova rota** (GET por id, DELETE, PUT) | exemplos prontos no fim de [app/routes.py](app/routes.py) | exemplos no fim de `src/api.js` |
| **Nota com decimal** (7.5) | `nota: int` → `nota: float` em [app/models.py](app/models.py) | `step: 0.5` no campo nota em `CAMPOS` |
| **Validação de campo** (tamanho, faixa) | `Field(ge=, le=, min_length=, max_length=)` em [app/models.py](app/models.py) | `min`/`max`/`obrigatorio` em `CAMPOS` |
| **Trocar o nome da imagem** no Docker Hub | `IMAGE_NAME` em [.github/workflows/deploy.yml](.github/workflows/deploy.yml) | nada |
| **Trocar a porta externa** (8080) | `PORTA_EXTERNA` em [.github/workflows/deploy.yml](.github/workflows/deploy.yml) | `vercel.json` |
| **Trocar o IP da máquina** | secret `EC2_HOST` | `vercel.json` |

Os pontos de mudança no código estão marcados com ⭐.

> **Mudou campo da entidade?** O SQLite não altera uma tabela que já existe. Apague o banco:
> - local: `rm avaliacoes.db`
> - na AWS: `ssh -i projsoft26b.pem ubuntu@13.220.42.157 'docker rm -f api; docker volume rm api-data'` e rode o workflow de novo (Actions › Deploy backend na AWS › Run workflow).

Não precisa renomear as classes (`Avaliacao`…) se a entidade mudar de nome: trocar `ROTA`, os campos e o `__tablename__` já resolve.

---

## 1. Configurar o Auth0 (uma vez só, serve para back e front)

1. **API** (Applications › APIs › *Create API*)
   - Name: `API Avaliacoes`
   - Identifier: `https://avaliacoes-api`. Esse é o **AUDIENCE** (não precisa ser uma URL real)
   - Signing algorithm: RS256
2. **Aplicação do front** (Applications › Applications › *Create Application* › **Single Page Web Applications**)
   - Copie o **Domain** e o **Client ID**
   - Em *Settings*, preencha **Allowed Callback URLs**, **Allowed Logout URLs** e **Allowed Web Origins** com:
     `http://localhost:5173, https://SEU-FRONT.vercel.app`
3. **Roles** (User Management › Roles): crie `ADMIN` e `USER`.
   Atribua aos usuários em User Management › Users › (usuário) › *Roles* › *Assign Roles*.
4. **Action** para colocar roles e email no token (Actions › Library › *Create Action* › *Build from scratch*, trigger **Login / Post Login**):

   ```js
   exports.onExecutePostLogin = async (event, api) => {
     const namespace = 'https://avaliacoes-insper.com'; // ⭐ igual ao NAMESPACE do back e do front
     const roles = event.authorization?.roles || [];
     api.accessToken.setCustomClaim(`${namespace}/roles`, roles);
     api.accessToken.setCustomClaim(`${namespace}/email`, event.user.email);
     api.idToken.setCustomClaim(`${namespace}/roles`, roles);
   };
   ```

   Clique em **Deploy** e depois, em Actions › Triggers › **post-login**, arraste a Action para o fluxo e clique em **Apply**.

> Mudou a role de alguém? A pessoa precisa **sair e entrar de novo** para o token novo trazer a role.

---

## 2. Secrets do GitHub (Settings › Secrets and variables › Actions › *New repository secret*)

| Secret | Valor |
|---|---|
| `DOCKERHUB_USERNAME` | seu usuário do Docker Hub |
| `DOCKERHUB_TOKEN` | token do Docker Hub: hub.docker.com › Account settings › **Personal access tokens** › *Generate new token* (permissão **Read & Write**) |
| `EC2_HOST` | `13.220.42.157` |
| `EC2_SSH_KEY` | o conteúdo **inteiro** do `projsoft26b.pem` (de `-----BEGIN` até `END-----`). No Mac: `pbcopy < projsoft26b.pem` |
| `AUTH0_DOMAIN` | ex.: `dev-xxxx.us.auth0.com` (sem `https://` e sem `/` no final) |
| `AUTH0_AUDIENCE` | `https://avaliacoes-api` (o Identifier da API) |
| `EC2_USER` | opcional, o padrão é `ubuntu` |

## 3. Deploy na AWS (GitHub Actions)

Todo `git push` na `main` dispara o [deploy.yml](.github/workflows/deploy.yml), que:

1. faz login no Docker Hub, o build da imagem e o `docker push` (`SEU_USUARIO/api-avaliacoes:latest`);
2. entra na EC2 por SSH e faz `docker pull` da imagem;
3. recria o container:
   ```bash
   docker run -d --name api --restart unless-stopped -p 8080:8000 -v api-data:/data -e AUTH0_DOMAIN=... -e AUTH0_AUDIENCE=... SEU_USUARIO/api-avaliacoes:latest
   ```
   O `-v api-data:/data` guarda o banco SQLite fora do container, então os dados sobrevivem aos deploys;
4. confere se `/health` respondeu (se não, mostra os logs do container).

Para rodar sem push: aba **Actions** › *Deploy backend na AWS* › **Run workflow**.

API no ar: `http://13.220.42.157:8080/docs`

Comandos úteis na máquina:

```bash
ssh -i projsoft26b.pem ubuntu@13.220.42.157
docker ps                 # container rodando?
docker logs -f api        # logs da API
docker restart api
```

---

## Rodar localmente

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env      # preencha AUTH0_DOMAIN e AUTH0_AUDIENCE
uvicorn app.main:app --reload        # http://localhost:8000/docs
pytest -q                            # testes
```

Testar com curl: faça login no front, abra o DevTools › Network, copie o header `Authorization` de alguma chamada e use:

```bash
curl -H "Authorization: Bearer SEU_TOKEN" http://localhost:8000/avaliacoes
```

(O token da aba *Test* da API no Auth0 não passa pela Action, então vem **sem roles** e recebe 403.)

## Estrutura

```
app/
  config.py    ⭐ rota, roles, namespace do Auth0
  models.py    ⭐ campos da entidade
  routes.py    ⭐ rotas (+ exemplos prontos de GET por id, DELETE, PUT, filtros)
  auth.py      validação do JWT do Auth0 e checagem de roles
  database.py  conexão SQLite
  main.py      cria o app, CORS e /health
tests/         testes com tokens JWT reais assinados localmente
```
