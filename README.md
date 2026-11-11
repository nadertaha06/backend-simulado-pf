# API de Avaliações: guia completo para a prova

Backend em **FastAPI** com login pelo **Auth0**, rodando em Docker na **AWS** com deploy pelo **GitHub Actions**.
O front fica em outro repositório: [frontend-simulado-pf](https://github.com/nadertaha06/frontend-simulado-pf).

| O quê | Link |
|---|---|
| Site (Vercel) | https://frontend-simulado-pf.vercel.app |
| API / Swagger (AWS) | http://13.220.42.157:8080/docs |
| Deploys (GitHub Actions) | aba **Actions** deste repositório |

> Este guia cobre o **back e o front**, porque quase toda mudança da prova mexe nos dois.
> Os pontos de mudança no código estão marcados com ⭐. Todos os trechos de código deste guia foram testados.

---

## Sumário

1. [Como o projeto funciona](#1-como-o-projeto-funciona)
2. [Mapa: onde fica cada coisa](#2-mapa-onde-fica-cada-coisa)
3. [Roteiro na hora da prova](#3-roteiro-na-hora-da-prova)
4. [Receitas de mudança (com código pronto)](#4-receitas-de-mudança)
   - [A. Mudar o nome da rota](#a-mudar-o-nome-da-rota)
   - [B. Trocar a entidade inteira](#b-trocar-a-entidade-inteira-ex-avaliação--tarefa)
   - [C. Mudar quem pode acessar (roles)](#c-mudar-quem-pode-acessar-roles)
   - [D. Mudar o que o GET lista](#d-mudar-o-que-o-get-lista)
   - [E. Filtros por parâmetro](#e-filtros-por-parâmetro)
   - [F. Mostrar só alguns campos na listagem](#f-mostrar-só-alguns-campos-na-listagem)
   - [G. Adicionar / remover / renomear campo](#g-adicionar--remover--renomear-campo)
   - [H. Campo preenchido pelo servidor](#h-campo-preenchido-pelo-servidor)
   - [I. Validações](#i-validações)
   - [J. Rotas novas: buscar por id, excluir, atualizar](#j-rotas-novas-buscar-por-id-excluir-atualizar)
   - [K. Rota de estatística (média)](#k-rota-de-estatística-média)
   - [L. Regras de negócio](#l-regras-de-negócio)
   - [M. Porta, IP, nome da imagem](#m-porta-ip-nome-da-imagem)
5. [Deu erro? Tabela de problemas](#5-deu-erro-tabela-de-problemas)
6. [Configuração do Auth0 (do zero)](#6-configuração-do-auth0-do-zero)
7. [Secrets e deploy](#7-secrets-e-deploy)
8. [Rodar e testar localmente](#8-rodar-e-testar-localmente)

---

## 1. Como o projeto funciona

```
 Navegador ──► https://frontend-simulado-pf.vercel.app        (React)
                 │  login ◄──► Auth0  (devolve um token com as roles)
                 │
                 └─► /api/avaliacoes  ──(vercel.json repassa)──►  http://13.220.42.157:8080/avaliacoes
                                                                   (FastAPI no Docker, na EC2)
                                                                   valida o token e as roles
                                                                   salva no SQLite (volume api-data)
```

- **Por que `/api`?** A Vercel é https e a EC2 é http. O navegador bloqueia https chamando http, então a Vercel faz a ponte.
- **Deploy do back:** `git push` na `main` → Actions faz o build → push no Docker Hub → `docker pull` + `docker run` na EC2.
- **Deploy do front:** `git push` na `main` do front → a Vercel publica sozinha.

**Rotas atuais:**

| Rota | Quem acessa | O que faz |
|---|---|---|
| `POST /avaliacoes` | ADMIN | cadastra (o avaliador é o usuário logado, vem do token) |
| `GET /avaliacoes` | ADMIN, USER | lista todas, mais recentes primeiro |
| `GET /health` | público | checa se o container subiu |
| `GET /docs` | público | Swagger |

**Entidade:** `id`, `emailAvaliador`, `emailAvaliado`, `comentarios`, `nota` (0 a 10), `dataAvaliacao`.

---

## 2. Mapa: onde fica cada coisa

### Backend (este repositório)

| Arquivo | O que tem | Muda na prova? |
|---|---|---|
| ⭐ [app/config.py](app/config.py) | `ROTA`, `ROLES_CADASTRAR`, `ROLES_LISTAR`, namespace do Auth0 | **Sim**: rota e permissões |
| ⭐ [app/models.py](app/models.py) | os **campos** da entidade | **Sim**: campos e validações |
| ⭐ [app/routes.py](app/routes.py) | o que cada rota **faz** e o que o GET **lista**, mais exemplos prontos no fim | **Sim**: filtros, rotas novas, regras |
| [app/auth.py](app/auth.py) | valida o token do Auth0 e as roles | Quase nunca |
| [app/database.py](app/database.py) | conexão com o SQLite | Não |
| [app/main.py](app/main.py) | cria o app, CORS, `/health` | Não |
| [.github/workflows/deploy.yml](.github/workflows/deploy.yml) | o deploy | Só porta ou nome da imagem |

### Frontend ([outro repositório](https://github.com/nadertaha06/frontend-simulado-pf))

| Arquivo | O que tem | Muda na prova? |
|---|---|---|
| ⭐ `src/config.js` | `ROTA`, textos, roles, **lista `CAMPOS`** (formulário e tabela saem dela), botão Excluir | **Sim**, quase tudo é aqui |
| `src/api.js` | as chamadas à API (`listar`, `cadastrar`, `deletar`) | Só se tiver rota nova |
| `src/App.jsx` | login, roles, layout | Raramente |
| `src/components/Formulario.jsx` / `Lista.jsx` | gerados a partir de `CAMPOS` | Não |
| `vercel.json` | ponte `/api` → EC2 | Só se mudar IP ou porta |

---

## 3. Roteiro na hora da prova

1. **Leia o enunciado e anote:**
   - quais rotas;
   - quem acessa cada uma (ADMIN, USER…);
   - quais campos;
   - **o que o GET lista** (tudo? só do usuário logado?);
   - regras (ex.: "não pode avaliar a si mesmo").
2. **Backend**, nesta ordem:
   1. `app/config.py`: rota e roles;
   2. `app/models.py`: campos;
   3. `app/routes.py`: o que salva, o que lista e as regras.
3. **Frontend:** `src/config.js` com rota, textos, roles e `CAMPOS`. O `nome` de cada campo tem que ser **igual** ao do backend.
4. **Mudou campo?** Na hora do deploy, apague o banco ([veja G](#g-adicionar--remover--renomear-campo)).
5. **Suba os dois:**
   ```bash
   # na pasta do back
   git add . && git commit -m "prova" && git push
   # na pasta do front
   git add . && git commit -m "prova" && git push
   ```
6. **Confira:**
   - **Actions** do back está verde ✅;
   - a Vercel terminou o deploy;
   - abra o site, faça login, cadastre e liste.
7. **Deu erro?** Vá direto para a [tabela de problemas](#5-deu-erro-tabela-de-problemas).

> Dica: os **nomes das classes** (`Avaliacao`, `AvaliacaoBase`…) podem continuar iguais mesmo se a entidade mudar. Ninguém vê esses nomes. Se quiser renomear, use Buscar e Substituir na pasta `app/` (Cmd+Shift+H no VS Code): `Avaliacao` → `Tarefa`.

---

## 4. Receitas de mudança

### A. Mudar o nome da rota

Ex.: `/avaliacoes` → `/feedbacks`

| Onde | Mudança |
|---|---|
| Back: [app/config.py](app/config.py) | `ROTA = "/feedbacks"` |
| Front: `src/config.js` | `export const ROTA = '/feedbacks'` |

Não precisa mexer no `vercel.json`: ele repassa qualquer caminho que começa com `/api`.

**Só uma das rotas muda de nome** (ex.: o GET vira `/avaliacoes/todas`):
- Back, em [app/routes.py](app/routes.py): troque `@router.get("")` por `@router.get("/todas")`.
- Front, em `src/api.js`: troque `listar = (token) => request(token, ROTA)` por `request(token, \`${ROTA}/todas\`)`.

---

### B. Trocar a entidade inteira (ex.: Avaliação → Tarefa)

Enunciado de exemplo: *"Tarefa: id, título, descrição, prioridade (BAIXA/MEDIA/ALTA), horas (0 a 10), status (começa PENDENTE), email do criador, data de criação. POST /tarefas (ADMIN), GET /tarefas (ADMIN e USER)."*

**1. [app/config.py](app/config.py)**
```python
ROTA = "/tarefas"
```

**2. [app/models.py](app/models.py)**: troque as 3 classes por:
```python
from typing import Literal   # ← adicione no topo, junto com os outros imports

class AvaliacaoBase(SQLModel):                       # campos que o usuário PREENCHE
    titulo: str = Field(min_length=1, max_length=100)
    descricao: str
    prioridade: str
    horas: float = Field(ge=0, le=10)


class AvaliacaoCreate(AvaliacaoBase):                # corpo do POST
    prioridade: Literal["BAIXA", "MEDIA", "ALTA"]    # opções fixas: SÓ aqui (na tabela quebra)


class Avaliacao(AvaliacaoBase, table=True):          # tabela = o que o GET devolve
    __tablename__ = "tarefas"

    id: int | None = Field(default=None, primary_key=True)
    emailCriador: str                                # o servidor preenche (token)
    status: str = "PENDENTE"                         # o servidor preenche (valor padrão)
    dataCriacao: datetime = Field(default_factory=agora)
```
(Pode apagar o `from pydantic import EmailStr` se não usar mais email.)

**3. [app/routes.py](app/routes.py)**: no `cadastrar()`, troque tudo entre `def cadastrar(...):` e `session.add(...)` por:
```python
    avaliacao = Avaliacao(**dados.model_dump(), emailCriador=usuario.email)
```
e no `listar()` troque `Avaliacao.dataAvaliacao.desc()` por `Avaliacao.dataCriacao.desc()`.

**4. Front: `src/config.js`**
```js
export const TITULO = 'Tarefas'
export const SUBTITULO = 'Tarefas da equipe'
export const NOME_ITEM = 'tarefa'
export const ROTA = '/tarefas'

export const CAMPOS = [
  { nome: 'id', label: 'ID', tipo: 'number', noForm: false, naTabela: true },
  { nome: 'titulo', label: 'Título', tipo: 'text', noForm: true, naTabela: true, obrigatorio: true },
  { nome: 'descricao', label: 'Descrição', tipo: 'textarea', noForm: true, naTabela: true, obrigatorio: true },
  { nome: 'prioridade', label: 'Prioridade', tipo: 'select', opcoes: ['BAIXA', 'MEDIA', 'ALTA'], noForm: true, naTabela: true, obrigatorio: true },
  { nome: 'horas', label: 'Horas', tipo: 'number', min: 0, max: 10, step: 0.5, noForm: true, naTabela: true, obrigatorio: true },
  { nome: 'status', label: 'Status', tipo: 'text', noForm: false, naTabela: true },
  { nome: 'emailCriador', label: 'Criador', tipo: 'email', noForm: false, naTabela: true },
  { nome: 'dataCriacao', label: 'Data', tipo: 'datetime', noForm: false, naTabela: true },
]
```

**5. Apague o banco no deploy** ([veja G](#g-adicionar--remover--renomear-campo)) e suba os dois.

---

### C. Mudar quem pode acessar (roles)

| Situação | Back: [app/config.py](app/config.py) | Front: `src/config.js` |
|---|---|---|
| USER também cadastra | `ROLES_CADASTRAR = ["ADMIN", "USER"]` | `ROLES_PODE_CADASTRAR = ['ADMIN', 'USER']` |
| Só ADMIN lista | `ROLES_LISTAR = ["ADMIN"]` | nada (o USER vai ver o erro 403 na lista) |
| Role nova (ex.: `GESTOR`) | incluir `"GESTOR"` nas listas | incluir `'GESTOR'` em `ROLES_PODE_CADASTRAR` se ele cadastra |

**Role nova:** crie também no Auth0 (User Management › Roles), atribua ao usuário e **saia e entre de novo**.

**Rota com roles próprias:** coloque direto na rota, sem usar o config:
```python
usuario: Usuario = Depends(exigir_roles("ADMIN", "GESTOR")),
```

**Rota sem role, só precisa estar logado:**
```python
from app.auth import get_usuario
...
usuario: Usuario = Depends(get_usuario),
```

---

### D. Mudar o que o GET lista

Tudo dentro do `listar()` em [app/routes.py](app/routes.py). Troque a linha `query = ...`:

**D1. Só as avaliações em que o usuário logado é o AVALIADO:**
```python
    query = select(Avaliacao).where(Avaliacao.emailAvaliado == usuario.email).order_by(Avaliacao.dataAvaliacao.desc())
```

**D2. Só as que o usuário logado FEZ (avaliador):**
```python
    query = select(Avaliacao).where(Avaliacao.emailAvaliador == usuario.email).order_by(Avaliacao.dataAvaliacao.desc())
```

**D3. ADMIN vê tudo, USER vê só as dele:**
```python
    query = select(Avaliacao)
    if "ADMIN" not in usuario.roles:
        query = query.where(Avaliacao.emailAvaliado == usuario.email)
    query = query.order_by(Avaliacao.dataAvaliacao.desc())
```

**D4. Rota separada `GET /avaliacoes/minhas`** (cole **antes** de qualquer rota com `/{id}`):
```python
@router.get("/minhas", response_model=list[Avaliacao])
def minhas(
    usuario: Usuario = Depends(exigir_roles("ADMIN", "USER")),
    session: Session = Depends(get_session),
):
    query = select(Avaliacao).where(Avaliacao.emailAvaliado == usuario.email)
    return session.exec(query).all()
```

**D5. Outra ordenação:**
- maior nota primeiro: `.order_by(Avaliacao.nota.desc())`
- mais antigas primeiro: `.order_by(Avaliacao.dataAvaliacao)`

**Front:** nada muda. Ele mostra o que o back devolver. Para o front chamar `/minhas`, em `src/api.js` troque o `listar` por `request(token, \`${ROTA}/minhas\`)`.

---

### E. Filtros por parâmetro

**E1. Query string: `GET /avaliacoes?notaMinima=7&emailAvaliado=ana@empresa.com`**

Os parâmetros são opcionais. No [app/routes.py](app/routes.py), troque o `listar()` inteiro por:
```python
@router.get("", response_model=list[Avaliacao])
def listar(
    notaMinima: int | None = None,
    emailAvaliado: str | None = None,
    usuario: Usuario = Depends(exigir_roles(*config.ROLES_LISTAR)),
    session: Session = Depends(get_session),
):
    query = select(Avaliacao)
    if notaMinima is not None:
        query = query.where(Avaliacao.nota >= notaMinima)
    if emailAvaliado:
        query = query.where(Avaliacao.emailAvaliado == emailAvaliado)
    query = query.order_by(Avaliacao.dataAvaliacao.desc())
    return session.exec(query).all()
```

**E2. No caminho: `GET /avaliacoes/avaliado/{email}`** (antes de qualquer `/{id}`):
```python
@router.get("/avaliado/{email}", response_model=list[Avaliacao])
def por_avaliado(
    email: str,
    usuario: Usuario = Depends(exigir_roles(*config.ROLES_LISTAR)),
    session: Session = Depends(get_session),
):
    return session.exec(select(Avaliacao).where(Avaliacao.emailAvaliado == email)).all()
```

> ⚠️ **Ordem das rotas:** caminhos fixos (`/minhas`, `/media`, `/avaliado/{email}`) têm que vir **antes** de `/{id}` no arquivo. Senão o FastAPI tenta ler "minhas" como id e devolve 422.

---

### F. Mostrar só alguns campos na listagem

Ex.: *"o GET deve listar só id, avaliado e nota"*.

**1. [app/models.py](app/models.py)**: adicione no fim:
```python
class AvaliacaoResumo(SQLModel):
    id: int
    emailAvaliado: str
    nota: int
```

**2. [app/routes.py](app/routes.py)**:
- importe `AvaliacaoResumo`: `from app.models import Avaliacao, AvaliacaoCreate, AvaliacaoResumo`;
- no `listar()`, troque `response_model=list[Avaliacao]` por `response_model=list[AvaliacaoResumo]`.

**3. Front:** em `CAMPOS`, coloque `naTabela: false` nos campos que não vêm mais.

---

### G. Adicionar / remover / renomear campo

**Adicionar campo que o usuário preenche** (ex.: `cargo`):

| Onde | Mudança |
|---|---|
| Back: [app/models.py](app/models.py), em `AvaliacaoBase` | `cargo: str` |
| Front: `src/config.js`, em `CAMPOS` | `{ nome: 'cargo', label: 'Cargo', tipo: 'text', noForm: true, naTabela: true, obrigatorio: true },` |

**Campo opcional:**
- Back: `cargo: str | None = None`
- Front: tire o `obrigatorio: true`

**Remover:** apague a linha no back **e** o item no `CAMPOS` do front.

**Renomear:** mude o nome no back **e** o `nome` no front. Eles têm que ser idênticos, inclusive maiúsculas.

> ### ⚠️ Mudou campo? Apague o banco
> O SQLite não altera uma tabela que já existe. Sem apagar, aparece **erro 500** (`no such column`).
> - **Na AWS (jeito fácil):** GitHub › **Actions** › *Deploy backend na AWS* › **Run workflow** › marque **"Apagar o banco"** › Run.
> - **Na AWS pelo terminal:** `ssh -i projsoft26b.pem ubuntu@13.220.42.157 'docker rm -f api; docker volume rm api-data'` e rode o workflow.
> - **Local:** `rm avaliacoes.db`

---

### H. Campo preenchido pelo servidor

O usuário **não** envia esses campos; o back preenche.

Vão na classe `Avaliacao` (a tabela) em [app/models.py](app/models.py), **não** na `AvaliacaoBase`:
```python
class Avaliacao(AvaliacaoBase, table=True):
    ...
    status: str = "PENDENTE"                                  # valor padrão fixo
    dataAvaliacao: datetime = Field(default_factory=agora)    # data/hora automática
```

Se o valor vem do usuário logado, preencha no `cadastrar()` em [app/routes.py](app/routes.py):
```python
    avaliacao = Avaliacao(
        **dados.model_dump(exclude={"emailAvaliador"}),
        emailAvaliador=usuario.email,       # ← email do token
    )
```

No front, coloque esses campos em `CAMPOS` com `noForm: false, naTabela: true`.

---

### I. Validações

Tudo em [app/models.py](app/models.py). No front, ajuste `min`, `max`, `step` e `obrigatorio` em `CAMPOS`.

| Enunciado | Back | Front (`CAMPOS`) |
|---|---|---|
| Nota de 1 a 5 | `nota: int = Field(ge=1, le=5)` | `min: 1, max: 5` |
| Nota com decimal (7.5) | `nota: float = Field(ge=0, le=10)` | `step: 0.5` (ou `'any'`) |
| Texto obrigatório e com limite | `comentarios: str = Field(min_length=1, max_length=500)` | `obrigatorio: true` |
| Tem que ser email | `emailAvaliado: EmailStr` | `tipo: 'email'` |
| Opções fixas | Base: `prioridade: str`. **Create:** `prioridade: Literal["BAIXA", "MEDIA", "ALTA"]` (com `from typing import Literal`) | `tipo: 'select', opcoes: ['BAIXA', 'MEDIA', 'ALTA']` |
| Sim/não | `ativo: bool = True` | `tipo: 'checkbox'` |
| Data (sem hora) | `dataEntrega: date` (com `from datetime import date`) | `tipo: 'date'` |

Quando a validação falha, o back responde **422** e o front mostra o motivo em vermelho.

> ⚠️ O `Literal` (opções fixas) **só pode ficar no `AvaliacaoCreate`**. Na `AvaliacaoBase` ou na tabela ele dá erro (`issubclass() arg 1 must be a class`).

---

### J. Rotas novas: buscar por id, excluir, atualizar

As três já estão **prontas e comentadas** no fim de [app/routes.py](app/routes.py). É só apagar o `# ` do começo das linhas: selecione o bloco e use Cmd+/ no VS Code.

| Rota | Quem (padrão) | Retorno |
|---|---|---|
| `GET /avaliacoes/{id}` | ADMIN, USER | 200 ou 404 |
| `DELETE /avaliacoes/{id}` | ADMIN | 204 ou 404 |
| `PUT /avaliacoes/{id}` | ADMIN | 200 ou 404 |

**Botão "Excluir" no front:** ele já está pronto. Depois de descomentar o DELETE no back, em `src/config.js`:
```js
export const MOSTRAR_EXCLUIR = true
export const ROLES_PODE_EXCLUIR = ['ADMIN']
```

---

### K. Rota de estatística (média)

Ex.: *"GET /avaliacoes/media: média das notas de cada avaliado"*. Cole **antes** de qualquer `/{id}` e troque o import do topo para `from sqlmodel import Session, func, select`:
```python
@router.get("/media")
def media(
    usuario: Usuario = Depends(exigir_roles(*config.ROLES_LISTAR)),
    session: Session = Depends(get_session),
):
    linhas = session.exec(
        select(Avaliacao.emailAvaliado, func.avg(Avaliacao.nota), func.count())
        .group_by(Avaliacao.emailAvaliado)
    ).all()
    return [
        {"emailAvaliado": email, "media": round(media, 2), "quantidade": qtd}
        for email, media, qtd in linhas
    ]
```
Resposta: `[{"emailAvaliado": "ana@empresa.com", "media": 5.5, "quantidade": 2}]`

Outras agregações: `func.max(...)`, `func.min(...)`, `func.sum(...)`.

---

### L. Regras de negócio

Coloque no `cadastrar()` em [app/routes.py](app/routes.py), **depois** do `if not email_avaliador:` e **antes** de `avaliacao = Avaliacao(...)`.

**L1. Não pode avaliar a si mesmo → 400**
```python
    if email_avaliador == dados.emailAvaliado:
        raise HTTPException(400, "Você não pode avaliar a si mesmo")
```

**L2. Não pode avaliar a mesma pessoa duas vezes → 409**
```python
    ja_existe = session.exec(
        select(Avaliacao).where(
            Avaliacao.emailAvaliador == email_avaliador,
            Avaliacao.emailAvaliado == dados.emailAvaliado,
        )
    ).first()
    if ja_existe:
        raise HTTPException(409, "Você já avaliou essa pessoa")
```

**L3. O avaliador vem no corpo do POST, e não do token:**
- No `cadastrar()`, inverta a prioridade da primeira linha:
  ```python
      email_avaliador = dados.emailAvaliador or usuario.email
  ```
- No front, em `CAMPOS`, mude o `emailAvaliador` para `noForm: true, obrigatorio: true`.

**Códigos de erro:**

| Código | Quando usar |
|---|---|
| 400 | dado inválido pela regra |
| 403 | sem permissão |
| 404 | não encontrado |
| 409 | duplicado ou conflito |

---

### M. Porta, IP, nome da imagem

| Mudança | Onde |
|---|---|
| Porta externa (8080) | `PORTA_EXTERNA` em [.github/workflows/deploy.yml](.github/workflows/deploy.yml) **e** a porta no `vercel.json` do front. Libere a porta no Security Group da EC2. |
| IP da máquina | secret `EC2_HOST` **e** `vercel.json` do front |
| Nome da imagem no Docker Hub | `IMAGE_NAME` em [.github/workflows/deploy.yml](.github/workflows/deploy.yml) |
| Nome do container | `CONTAINER` em [.github/workflows/deploy.yml](.github/workflows/deploy.yml) |

---

## 5. Deu erro? Tabela de problemas

| Sintoma | Causa | Solução |
|---|---|---|
| Actions vermelho em **Conferir secrets** | falta algum secret | a mensagem diz qual. Cadastre em Settings › Secrets |
| Actions vermelho em **Login no Docker Hub** | token errado ou expirado | gere outro token (Read & Write) e atualize `DOCKERHUB_TOKEN` |
| Actions vermelho em **Pull e run** | chave SSH errada ou máquina desligada | confira o `EC2_SSH_KEY` (o .pem inteiro) e se a EC2 está ligada |
| Actions vermelho em **Verificar se a API subiu** | erro no código Python | os logs aparecem no próprio passo. Leia a última linha do erro |
| Site: **"Falta configurar o Auth0"** | faltam variáveis na Vercel | cadastre as 3 `VITE_AUTH0_*` (tipo Config) e faça **Redeploy** |
| Login: **Callback URL mismatch** | URL do site não está no Auth0 | Auth0 › Applications › SPA › Allowed Callback/Logout URLs e Web Origins |
| Login: **Client … is not authorized to access resource server** | SPA não autorizada na API | Auth0 › APIs › API › Application Access › Front › User Access: Authorized (Always grant all permissions) |
| **"sem role"** no topo / **403** | token sem roles | atribua a role ao usuário (User Management › Users › Roles), confira a Action no post-login e **saia e entre de novo** |
| **401 Invalid audience** | audience diferente no back e no front | `AUTH0_AUDIENCE` (secret) = `VITE_AUTH0_AUDIENCE` (Vercel) = Identifier da API |
| **401 Invalid issuer** | domínio errado | `AUTH0_DOMAIN` sem `https://` e sem `/` no final |
| **500** depois de mudar campo | banco antigo (`no such column`) | Run workflow com **"Apagar o banco"** marcado |
| **422** | dado não passou na validação | a mensagem diz o campo. Confira se o `nome` no front é igual ao do back |
| **405 Method Not Allowed** | rota existe, mas não com esse método | confira o `@router.get/post/delete` e o método no `src/api.js` |
| **404** em rota nova | caminho diferente no back e no front, ou rota depois de `/{id}` | confira `ROTA`, o caminho e a ordem das rotas |
| Lista vazia mas tem dados | filtro do `listar()` (D1/D2) com email diferente | o email do token é o email de login (Google ou senha) |

**Ver logs da API na máquina:**
```bash
ssh -i projsoft26b.pem ubuntu@13.220.42.157
docker ps              # o container "api" está Up?
docker logs -f api     # erros da API em tempo real (Ctrl+C para sair)
```

---

## 6. Configuração do Auth0 (do zero)

Faça só se precisar de um tenant novo. Siga a ordem.

1. **API**: Applications › APIs › **+ Create API**
   - Name: `API Avaliacoes`
   - Identifier: `https://avaliacoes-api` (este é o **AUDIENCE**; não dá para mudar depois)
   - RS256
2. **Aplicação SPA**: Applications › Applications › **+ Create Application** › **Single Page Web Applications**
   - Copie o **Domain** e o **Client ID** (o Client Secret não é usado)
   - Em **Allowed Callback URLs**, **Allowed Logout URLs** e **Allowed Web Origins**, coloque:
     `http://localhost:5173, https://frontend-simulado-pf.vercel.app`
   - **Save Changes**
3. **Autorizar a SPA na API** (contas novas exigem): APIs › API Avaliacoes › **Application Access** › Front Avaliacoes › Edit › **User Access** › ligue **Always grant all permissions** › Save.
   - Para conferir: o *Grant ID* deve deixar de mostrar "No per-app authorization grant".
4. **Roles**: User Management › Roles › crie `ADMIN` e `USER` (maiúsculas).
5. **Usuários**: quem entra com **Google** é criado sozinho no primeiro login, mas **sem role**.
   - Abra User Management › Users › (usuário) › **Roles** › **Assign Roles**.
6. **Action** (põe roles e email no token): Actions › Triggers › **post-login** › no painel da direita **+** / Create Action › Build from scratch. Cole o código abaixo, clique em **Deploy**, arraste a action entre *Start* e *Complete* e clique em **Apply**.
   ```js
   exports.onExecutePostLogin = async (event, api) => {
     const namespace = 'https://avaliacoes-insper.com'; // ⭐ igual ao NAMESPACE do back e do front
     const roles = event.authorization?.roles || [];
     api.accessToken.setCustomClaim(`${namespace}/roles`, roles);
     api.accessToken.setCustomClaim(`${namespace}/email`, event.user.email);
     api.idToken.setCustomClaim(`${namespace}/roles`, roles);
   };
   ```

> Mudou a role de alguém? A pessoa precisa **sair e entrar de novo**.

**Conferir o token:**
1. No site, abra o DevTools (F12) › Network › chamada `avaliacoes`.
2. Copie o header `Authorization` sem o `Bearer `.
3. Cole em **jwt.io**. Tem que aparecer `"https://avaliacoes-insper.com/roles": ["ADMIN"]`.

---

## 7. Secrets e deploy

**Secrets** (Settings › Secrets and variables › Actions):

| Secret | Valor |
|---|---|
| `DOCKERHUB_USERNAME` | seu usuário do Docker Hub |
| `DOCKERHUB_TOKEN` | hub.docker.com › Account settings › Personal access tokens (Read & Write) |
| `EC2_HOST` | `13.220.42.157` |
| `EC2_SSH_KEY` | o conteúdo **inteiro** do `.pem`. No Mac: `pbcopy < projsoft26b.pem` |
| `AUTH0_DOMAIN` | ex.: `dev-xxxx.us.auth0.com` (sem `https://`) |
| `AUTH0_AUDIENCE` | `https://avaliacoes-api` |
| `EC2_USER` | opcional (padrão `ubuntu`) |

**O que o deploy faz** ([deploy.yml](.github/workflows/deploy.yml)):
1. login no Docker Hub, build e `docker push` (`SEU_USUARIO/api-avaliacoes:latest`);
2. SSH na EC2, `docker pull` e:
   ```bash
   docker run -d --name api --restart unless-stopped -p 8080:8000 -v api-data:/data \
     -e AUTH0_DOMAIN=... -e AUTH0_AUDIENCE=... SEU_USUARIO/api-avaliacoes:latest
   ```
   O `-v api-data:/data` mantém o banco entre os deploys;
3. confere o `/health` e, se falhar, mostra os logs.

**Quando o deploy roda:**
- todo push na `main` (mudanças só em `.md` não disparam);
- manualmente, em Actions › *Deploy backend na AWS* › **Run workflow**, com a opção de **apagar o banco**.

---

## 8. Rodar e testar localmente

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env            # preencha AUTH0_DOMAIN e AUTH0_AUDIENCE
uvicorn app.main:app --reload   # http://localhost:8000/docs
pytest -q                       # testes
```

Front local apontando para esse back: no `.env` do front, `VITE_PROXY_TARGET=http://localhost:8000`, depois `npm run dev`.

**Testar com curl:** copie o token do navegador (DevTools › Network › header `Authorization`):
```bash
curl -H "Authorization: Bearer SEU_TOKEN" http://13.220.42.157:8080/avaliacoes
```
O token da aba *Test* da API no Auth0 **não** passa pela Action, então vem sem roles e recebe 403.

> Os testes em `tests/` usam os campos de avaliação. Se mudar a entidade, eles quebram, mas **não** atrapalham o deploy (não rodam no Actions). Atualize o `AVALIACAO` em `tests/test_api.py` ou ignore.
