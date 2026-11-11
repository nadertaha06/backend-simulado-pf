# API de Avalacioess (base de conhecimentos): guia completo para a prova

Backend em **Spring Boot** (Java 25), no **mesmo padrão do projeto do professor**
([projeto-software-2026-2-partida](https://github.com/ezambomsantana/projeto-software-2026-2-partida)):
Lombok, PostgreSQL, login pelo **Auth0** e deploy pelo **GitHub Actions** na **AWS**.
O front fica em outro repositório: [frontend-simulado-pf](https://github.com/nadertaha06/frontend-simulado-pf).

| O quê | Link |
|---|---|
| Site (Vercel) | https://frontend-simulado-pf.vercel.app |
| API (AWS) | http://13.220.42.157:8080/Avalacioess (precisa de token) |
| Deploys | aba **Actions** deste repositório |

> Este guia cobre o **back e o front**, porque quase toda mudança da prova mexe nos dois.
> Os pontos de mudança no código estão marcados com ⭐.

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
   - [F. Mostrar só alguns campos (DTO)](#f-mostrar-só-alguns-campos-dto)
   - [G. Adicionar / remover / renomear campo](#g-adicionar--remover--renomear-campo)
   - [H. Campo preenchido pelo servidor](#h-campo-preenchido-pelo-servidor)
   - [I. Validações](#i-validações)
   - [J. Buscar por id, excluir, atualizar](#j-buscar-por-id-excluir-atualizar)
   - [K. Rota de estatística (média)](#k-rota-de-estatística-média)
   - [L. Regras de negócio](#l-regras-de-negócio)
   - [M. Porta, IP, imagem](#m-porta-ip-imagem)
5. [Deu erro? Tabela de problemas](#5-deu-erro-tabela-de-problemas)
6. [Configuração do Auth0 (do zero)](#6-configuração-do-auth0-do-zero)
7. [Secrets e deploy](#7-secrets-e-deploy)
8. [Rodar localmente](#8-rodar-localmente)
9. [O que é igual e o que é diferente do professor](#9-o-que-é-igual-e-o-que-é-diferente-do-professor)

---

## 1. Como o projeto funciona

```
 Navegador ──► https://frontend-simulado-pf.vercel.app        (React)
                 │  login ◄──► Auth0  (devolve um token com roles e email)
                 │
                 └─► /api/Avalacioess ──(vercel.json repassa)──► http://13.220.42.157:8080/Avalacioess
                                                                  container "api" (Spring Boot)
                                                                  │  valida o token (issuer + audience)
                                                                  │  confere a role no controller
                                                                  └─► container "postgres-aula" (rede "rede")
```

- **Por que `/api`?** A Vercel é https e a EC2 é http. O navegador bloqueia, então a Vercel faz a ponte.
- **Deploy do back:** `git push` na `main` → Actions: Maven → imagem no Docker Hub → SSH na EC2 → `docker run`.
- **Deploy do front:** `git push` na `main` do front → a Vercel publica sozinha.

**Rotas atuais:**

| Rota | Quem acessa | O que faz |
|---|---|---|
| `GET /Avalacioess` | ADMIN, USER | lista todos os Avalacioess, mais recentes primeiro |
| `POST /Avalacioess` | ADMIN | cria um Avalacioes (o e-mail de quem criou é o do usuário logado, vem do token) |
| `DELETE /Avalacioess/{id}` | ADMIN | deleta um Avalacioes existente (404 se não existir) |

**Entidade:** `id`, `titulo`, `descricao`, `prioridade` (BAIXA, MEDIA ou ALTA), `emailUsuario`, `dataCriacao`.

> As receitas abaixo (A–M) usam como exemplo os campos do simulado de avaliações (`emailAvaliado`, `nota`...).
> A ideia é a mesma: troque pelos campos do Avalacioes.

---

## 2. Mapa: onde fica cada coisa

### Backend (este repositório): `src/main/java/br/edu/insper/Avalacioess/`

| Arquivo | O que tem | Muda na prova? |
|---|---|---|
| ⭐ [Avalacioes/Avalacioes.java](src/main/java/br/edu/insper/Avalacioess/Avalacioes/Avalacioes.java) | os **campos** (`@Entity @Getter @Setter`) | **Sim** |
| ⭐ [Avalacioes/AvalacioesController.java](src/main/java/br/edu/insper/Avalacioess/Avalacioes/AvalacioesController.java) | a **rota**, **quem pode** (`verificarRole`) e rotas prontas comentadas | **Sim** |
| ⭐ [Avalacioes/AvalacioesService.java](src/main/java/br/edu/insper/Avalacioess/Avalacioes/AvalacioesService.java) | o que **lista**, o que **salva**, **validações** e **regras** | **Sim** |
| ⭐ [Avalacioes/AvalacioesRepository.java](src/main/java/br/edu/insper/Avalacioess/Avalacioes/AvalacioesRepository.java) | consultas (`findBy...`) | Quando muda a listagem ou os campos |
| [config/WebSecurityConfig.java](src/main/java/br/edu/insper/Avalacioess/config/WebSecurityConfig.java) | CORS e "toda rota precisa de token" | Quase nunca |
| [application.properties](src/main/resources/application.properties) | porta 8000, Postgres, Auth0 | Quase nunca |
| [.github/workflows/deploy.yml](.github/workflows/deploy.yml) | o deploy | Só usuário do Docker Hub, porta |

**Quem chama quem:** Controller (rota + role) → Service (regras) → Repository (banco).

### Frontend ([outro repositório](https://github.com/nadertaha06/frontend-simulado-pf))

| Arquivo | O que tem | Muda na prova? |
|---|---|---|
| ⭐ `src/config.js` | `ROTA`, textos, roles, **lista `CAMPOS`** (formulário e tabela saem dela), botão Excluir | **Sim**, quase tudo é aqui |
| `src/api.js` | as chamadas (`listar`, `cadastrar`, `deletar`) | Só se tiver rota nova |
| `vercel.json` | ponte `/api` → EC2 | Só se mudar IP ou porta |

---

## 3. Roteiro na hora da prova

1. **Leia o enunciado e anote:** rotas, quem acessa cada uma, campos, **o que o GET lista** e as regras.
2. **Backend**, nesta ordem:
   1. `Avalacioes.java`: campos;
   2. `AvalacioesController.java`: rota e `verificarRole(...)`;
   3. `AvalacioesService.java`: `validar()`, o que o `criar()` preenche e o que o `listarTodos()` devolve;
   4. `AvalacioesRepository.java`: **apague ou ajuste os métodos que usam campos que não existem mais** (senão a API não sobe).
3. **Compile antes de subir** (pega erro de digitação em 20 segundos): `./mvnw -q compile`
4. **Frontend:** `src/config.js` com rota, textos, roles e `CAMPOS`. O `nome` de cada campo tem que ser **igual** ao do Java.
5. **Suba os dois:**
   ```bash
   # na pasta do back
   git add . && git commit -m "prova" && git push
   # na pasta do front
   git add . && git commit -m "prova" && git push
   ```
6. **Confira:** Actions verde ✅ → Vercel terminou → abra o site, faça login, cadastre e liste.
7. **Deu erro?** [Tabela de problemas](#5-deu-erro-tabela-de-problemas).

---

## 4. Receitas de mudança

### A. Mudar o nome da rota

Ex.: `/Avalacioess` → `/feedbacks`

| Onde | Mudança |
|---|---|
| Back: `AvalacioesController.java` | `@RequestMapping("/feedbacks")` |
| Front: `src/config.js` | `export const ROTA = '/feedbacks'` |

**Só uma rota muda** (ex.: o GET vira `/Avalacioess/todas`):
- Back: troque `@GetMapping` por `@GetMapping("/todas")`.
- Front, `src/api.js`: `listar = (token) => request(token, \`${ROTA}/todas\`)`.

---

### B. Trocar a entidade inteira (ex.: Avaliação → Tarefa)

Enunciado de exemplo: *"Tarefa: id, título, descrição, prioridade (BAIXA/MEDIA/ALTA), horas (0 a 10), status (começa PENDENTE), email do criador, data de criação. POST /tarefas (ADMIN), GET /tarefas (ADMIN e USER)."*

**Renomear as classes (opcional, mas fica mais bonito):** clique no nome da classe e aperte **F2** no VS Code
(**Shift+F6** no IntelliJ). Ele renomeia o arquivo e todos os usos. Faça em `Avalacioes`, `AvalacioesController`,
`AvalacioesService` e `AvalacioesRepository`. Com pressa, pode deixar os nomes; só os campos importam.

**1. Entidade** (troque os campos):
```java
@Entity
@Getter
@Setter
public class Tarefa {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;
    private String titulo;
    private String descricao;
    private String prioridade;          // BAIXA, MEDIA, ALTA
    private Double horas;               // 0 a 10, aceita decimal
    private String status;              // servidor preenche: PENDENTE
    private String emailCriador;        // servidor preenche: email do token
    private LocalDateTime dataCriacao;  // servidor preenche: agora
}
```

**2. Repository:** apague os métodos de exemplo e deixe só:
```java
List<Tarefa> findAllByOrderByDataCriacaoDesc();
```

**3. Service:** `listarTodos()` chama `findAllByOrderByDataCriacaoDesc()`. No `criar()`, troque o bloco "campos que o servidor preenche" por
(o F2 renomeia a classe, mas a variável continua `avaliacao`):
```java
        Avalacioes.setId(null);
        Avalacioes.setStatus("PENDENTE");
        Avalacioes.setEmailCriador(emailUsuario);
        Avalacioes.setDataCriacao(LocalDateTime.now());
```
Troque o `validar()` por:
```java
    private void validar(Tarefa tarefa) {
        if (tarefa.getTitulo() == null || tarefa.getTitulo().isBlank()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "titulo é obrigatório");
        }
        if (!List.of("BAIXA", "MEDIA", "ALTA").contains(tarefa.getPrioridade())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "prioridade deve ser BAIXA, MEDIA ou ALTA");
        }
        if (tarefa.getHoras() == null || tarefa.getHoras() < 0 || tarefa.getHoras() > 10) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "horas deve ser de 0 a 10");
        }
    }
```
No `atualizar()`, troque os `set...` pelos campos novos (ou apague o método, se não usar o PUT).

**4. Controller:** `@RequestMapping("/tarefas")`.

**5. Front: `src/config.js`**
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

**6. Compile** (`./mvnw -q compile`) e suba os dois. A tabela nova é criada sozinha.

---

### C. Mudar quem pode acessar (roles)

As roles são conferidas no **controller**, com o `verificarRole(jwt, ...)`. Ele lê
`jwt.getClaimAsStringList(NAMESPACE + "/roles")`, igual o professor faz, e dá **403** se não tiver nenhuma das roles.

| Situação | Back (`AvalacioesController.java`) | Front (`src/config.js`) |
|---|---|---|
| USER também cadastra | no `criar`: `verificarRole(jwt, "ADMIN", "USER");` | `ROLES_PODE_CADASTRAR = ['ADMIN', 'USER']` |
| Só ADMIN lista | no `listarTodos`: `verificarRole(jwt, "ADMIN");` | nada (o USER vê o erro 403) |
| Basta estar logado | apague a linha `verificarRole(...)` | — |
| Role nova (`GESTOR`) | `verificarRole(jwt, "ADMIN", "GESTOR");` | inclua `'GESTOR'` onde precisar |

**Role nova:** crie também no Auth0 (User Management › Roles), atribua ao usuário e **saia e entre de novo**.
O nome é sensível a maiúsculas: `ADMIN` ≠ `admin`.

---

### D. Mudar o que o GET lista

O email e as roles de quem está logado saem do token, no controller:
```java
String email = jwt.getClaimAsString(NAMESPACE + "/email");
List<String> roles = jwt.getClaimAsStringList(NAMESPACE + "/roles");
```

**D1. Só as avaliações em que o usuário logado é o AVALIADO**

Service (adicione):
```java
    public List<Avalacioes> listarPorAvaliado(String email) {
        return AvalacioesRepository.findByEmailAvaliadoOrderByDataCriacaoDesc(email);
    }
```
Controller, no `listarTodos`, troque o `return` por:
```java
        return AvalacioesService.listarPorAvaliado(jwt.getClaimAsString(NAMESPACE + "/email"));
```

**D2. Só as que o usuário logado FEZ (avaliador):** igual ao D1, usando
`findByEmailUsuarioOrderByDataCriacaoDesc(email)` (já está no repository).

**D3. ADMIN vê tudo, USER vê só as dele** (use o `listarPorAvaliado` do D1). Controller, no `listarTodos`:
```java
        verificarRole(jwt, "ADMIN", "USER");
        List<String> roles = jwt.getClaimAsStringList(NAMESPACE + "/roles");
        if (roles.contains("ADMIN")) {
            return AvalacioesService.listarTodos();
        }
        return AvalacioesService.listarPorAvaliado(jwt.getClaimAsString(NAMESPACE + "/email"));
```

**D4. Rota separada `GET /Avalacioess/minhas`** (controller, cole junto das outras rotas):
```java
    @GetMapping("/minhas")
    public List<Avalacioes> minhas(@AuthenticationPrincipal Jwt jwt) {
        verificarRole(jwt, "ADMIN", "USER");
        return AvalacioesService.listarPorAvaliado(jwt.getClaimAsString(NAMESPACE + "/email"));
    }
```
No Spring a ordem das rotas no arquivo **não importa**: `/minhas` funciona mesmo existindo `/{id}`.
Para o front chamar `/minhas`: em `src/api.js`, `listar = (token) => request(token, \`${ROTA}/minhas\`)`.

**D5. Outra ordenação** (repository, o nome do método define o SQL):
- maior nota primeiro: `List<Avalacioes> findAllByOrderByNotaDesc();`
- mais antigas primeiro: `List<Avalacioes> findAllByOrderByDataCriacaoAsc();`

**Como montar o nome do método:** `findBy` + Campo + (`And`/`Or` + Campo) + `OrderBy` + Campo + `Asc`/`Desc`.
Ex.: `findByEmailAvaliadoAndNotaGreaterThanEqual(String email, Integer nota)`.
Palavras úteis: `GreaterThan`, `LessThanEqual`, `Between`, `Containing`, `IgnoreCase`, `IsNull`, `Not`.

---

### E. Filtros por parâmetro

**E1. Query string: `GET /Avalacioess?notaMinima=7&emailAvaliado=ana@empresa.com`** (os dois opcionais)

Controller, troque o `listarTodos` por:
```java
    @GetMapping
    public List<Avalacioes> listarTodos(@RequestParam(required = false) Integer notaMinima,
                                       @RequestParam(required = false) String emailAvaliado,
                                       @AuthenticationPrincipal Jwt jwt) {
        verificarRole(jwt, "ADMIN", "USER");
        return AvalacioesService.listarTodos(notaMinima, emailAvaliado);
    }
```
Service, troque o `listarTodos()` por:
```java
    public List<Avalacioes> listarTodos(Integer notaMinima, String emailAvaliado) {
        return AvalacioesRepository.findAllByOrderByDataCriacaoDesc().stream()
                .filter(a -> notaMinima == null || a.getNota() >= notaMinima)
                .filter(a -> emailAvaliado == null || a.getEmailAvaliado().equals(emailAvaliado))
                .toList();
    }
```

**E2. No caminho: `GET /Avalacioess/avaliado/{email}`** (controller):
```java
    @GetMapping("/avaliado/{email}")
    public List<Avalacioes> porAvaliado(@PathVariable String email, @AuthenticationPrincipal Jwt jwt) {
        verificarRole(jwt, "ADMIN", "USER");
        return AvalacioesService.listarPorAvaliado(email);   // método do D1
    }
```

---

### F. Mostrar só alguns campos (DTO)

Ex.: *"o GET deve listar só id, avaliado e nota"*. Igual ao `PartidaResultadoDTO` do professor.

**1. Crie `Avalacioes/AvalacioesResumoDTO.java`:**
```java
package br.edu.insper.Avalacioess.Avalacioes;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class AvalacioesResumoDTO {
    private Integer id;
    private String emailAvaliado;
    private Integer nota;
}
```
**2. Service:**
```java
    public List<AvalacioesResumoDTO> listarResumo() {
        return AvalacioesRepository.findAllByOrderByDataCriacaoDesc().stream()
                .map(a -> new AvalacioesResumoDTO(a.getId(), a.getEmailAvaliado(), a.getNota()))
                .toList();
    }
```
**3. Controller:** o `listarTodos` passa a devolver `List<AvalacioesResumoDTO>` e chamar `AvalacioesService.listarResumo()`.

**4. Front:** em `CAMPOS`, `naTabela: false` nos campos que não vêm mais.

---

### G. Adicionar / remover / renomear campo

**Adicionar campo que o usuário preenche** (ex.: `cargo`):

| Onde | Mudança |
|---|---|
| `Avalacioes.java` | `private String cargo;` (o Lombok cria o getter e o setter) |
| `AvalacioesService.java`, `validar()` (se obrigatório) | `if (Avalacioes.getCargo() == null \|\| Avalacioes.getCargo().isBlank()) { throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "cargo é obrigatório"); }` |
| `AvalacioesService.java`, `atualizar()` (se usar PUT) | `Avalacioes.setCargo(dados.getCargo());` |
| Front, `CAMPOS` | `{ nome: 'cargo', label: 'Cargo', tipo: 'text', noForm: true, naTabela: true, obrigatorio: true },` |

A coluna nova é criada sozinha no deploy (`ddl-auto=update`).

**Remover:** apague o campo no Java, os usos dele (`validar`, `atualizar`, **métodos do repository**) e o item no `CAMPOS`.

**Renomear:** mude no Java (e nos usos) **e** o `nome` no front. Têm que ser idênticos, inclusive maiúsculas.

> ### ⚠️ Mudou o TIPO de um campo ou trocou a entidade? Apague o banco
> O `ddl-auto=update` cria tabelas e colunas novas, mas **não muda o tipo** de uma coluna que já existe
> (ex.: `Integer nota` → `Double nota`). Aí aparece erro 500 ao salvar.
> - **Jeito fácil:** GitHub › **Actions** › *Deploy automatico* › **Run workflow** › marque **"Apagar o banco"** › Run.
> - **Pelo terminal:** `ssh -i projsoft26b.pem ubuntu@13.220.42.157 'docker exec postgres-aula psql -U usuario -d auladb -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"; docker restart api'`

---

### H. Campo preenchido pelo servidor

O usuário **não** envia; o back preenche no `criar()` do service, no bloco "campos que o servidor preenche":
```java
        Avalacioes.setStatus("PENDENTE");                 // valor fixo
        Avalacioes.setDataCriacao(LocalDateTime.now()); // data/hora de agora
        Avalacioes.setEmailUsuario(emailUsuario);     // email do token
```
Mesmo que o JSON do POST mande esses campos, o `set...` do servidor sobrescreve.

Outros dados do token, no controller: `jwt.getSubject()` (id do usuário no Auth0), `jwt.getClaimAsString(NAMESPACE + "/email")`.

No front: `noForm: false, naTabela: true`.

---

### I. Validações

Ficam no `validar()` do service, um `if` por regra (do mesmo jeito que o professor valida no `PartidaProducer`).
O front mostra a mensagem em vermelho. No front, ajuste também `min`, `max`, `step` e `obrigatorio` em `CAMPOS`.

| Enunciado | `if` no `validar()` (erro 400) | Front (`CAMPOS`) |
|---|---|---|
| Obrigatório (texto) | `if (a.getTitulo() == null \|\| a.getTitulo().isBlank())` | `obrigatorio: true` |
| Obrigatório (número) | `if (a.getNota() == null)` | `obrigatorio: true` |
| Nota de 1 a 5 | `if (a.getNota() == null \|\| a.getNota() < 1 \|\| a.getNota() > 5)` | `min: 1, max: 5` |
| Nota com decimal (7.5) | campo `private Double nota;` | `step: 0.5` |
| Tamanho máximo | `if (a.getComentarios().length() > 500)` | — |
| Email | `if (a.getEmailAvaliado() == null \|\| !a.getEmailAvaliado().matches("^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$"))` | `tipo: 'email'` |
| Opções fixas | `if (!List.of("BAIXA", "MEDIA", "ALTA").contains(a.getPrioridade()))` | `tipo: 'select', opcoes: [...]` |
| Sim/não | campo `private Boolean ativo;` | `tipo: 'checkbox'` |
| Data (sem hora) | campo `private LocalDate dataEntrega;` (`import java.time.LocalDate;`) | `tipo: 'date'` |
| Data no futuro | `if (a.getDataEntrega() == null \|\| !a.getDataEntrega().isAfter(LocalDate.now()))` | `tipo: 'date'` |

Modelo do `throw`: `throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "mensagem que o front mostra");`

---

### J. Buscar por id, excluir, atualizar

Já estão **prontas e comentadas** no `AvalacioesController.java` (e os métodos já existem no service).
Selecione o bloco e aperte **Cmd+/** (Ctrl+/ no Windows) para descomentar.

| Rota | Quem (padrão) | Retorno |
|---|---|---|
| `GET /Avalacioess/{id}` | ADMIN, USER | 200 ou 404 |
| `DELETE /Avalacioess/{id}` | ADMIN | 204 ou 404 |
| `PUT /Avalacioess/{id}` | ADMIN | 200 ou 404 |

**Botão "Excluir" no front:** já existe. Depois de descomentar o DELETE, em `src/config.js`:
```js
export const MOSTRAR_EXCLUIR = true
export const ROLES_PODE_EXCLUIR = ['ADMIN']
```

**Rota que muda só um pedaço** (estilo `POST /partidas/{id}/resultado` do professor), ex.: `PATCH /Avalacioess/{id}/nota`:
```java
    @PatchMapping("/{id}/nota")
    public Avalacioes mudarNota(@PathVariable Integer id, @RequestBody Avalacioes dados, @AuthenticationPrincipal Jwt jwt) {
        verificarRole(jwt, "ADMIN");
        Avalacioes avaliacao = AvalacioesService.buscarPorId(id);
        Avalacioes.setNota(dados.getNota());
        return AvalacioesService.salvar(avaliacao);
    }
```
(no service: `public Avalacioes salvar(Avalacioes a) { return AvalacioesRepository.save(a); }`)

---

### K. Rota de estatística (média)

Ex.: *"GET /Avalacioess/media: média das notas de cada avaliado"*.

Service (adicione os imports `java.util.Map` e `java.util.stream.Collectors` no topo):
```java
    public List<Map<String, Object>> medias() {
        Map<String, Double> medias = AvalacioesRepository.findAll().stream()
                .collect(Collectors.groupingBy(Avalacioes::getEmailAvaliado,
                        Collectors.averagingInt(Avalacioes::getNota)));
        return medias.entrySet().stream()
                .map(e -> Map.<String, Object>of("emailAvaliado", e.getKey(), "media", e.getValue()))
                .toList();
    }
```
Controller (adicione `import java.util.Map;`):
```java
    @GetMapping("/media")
    public List<Map<String, Object>> medias(@AuthenticationPrincipal Jwt jwt) {
        verificarRole(jwt, "ADMIN", "USER");
        return AvalacioesService.medias();
    }
```
Resposta: `[{"emailAvaliado": "ana@empresa.com", "media": 5.5}]`.
Outras contas: `Collectors.counting()` (quantidade), `Collectors.summingInt(...)` (soma).
Média geral de todos: `findAll().stream().mapToInt(Avalacioes::getNota).average().orElse(0)`.

---

### L. Regras de negócio

No `criar()` do service, **depois** do `validar(avaliacao);`:

**L1. Não pode avaliar a si mesmo → 400**
```java
        if (emailUsuario.equals(Avalacioes.getEmailAvaliado())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Você não pode avaliar a si mesmo");
        }
```

**L2. Não pode avaliar a mesma pessoa duas vezes → 409** (o método já está no repository)
```java
        if (AvalacioesRepository.existsByEmailUsuarioAndEmailAvaliado(emailUsuario, Avalacioes.getEmailAvaliado())) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "Você já avaliou essa pessoa");
        }
```

**L3. O avaliador vem no corpo do POST, e não do token:** no `criar()`, troque
`Avalacioes.setEmailUsuario(emailUsuario);` por
```java
        if (Avalacioes.getEmailUsuario() == null) {
            Avalacioes.setEmailUsuario(emailUsuario);
        }
```
No front, `emailUsuario` com `noForm: true, obrigatorio: true`.

**Códigos de erro:**

| Código | `HttpStatus.` | Quando usar |
|---|---|---|
| 400 | `BAD_REQUEST` | dado inválido pela regra |
| 403 | `FORBIDDEN` | sem permissão |
| 404 | `NOT_FOUND` | não encontrado |
| 409 | `CONFLICT` | duplicado ou conflito |

---

### M. Porta, IP, imagem

| Mudança | Onde |
|---|---|
| Porta externa (8080) | `-p 8080:8000` no `deploy.yml` **e** a porta no `vercel.json` do front. Libere a porta no Security Group. |
| Porta interna (8000) | `server.port` no `application.properties` **e** o `8000` do `-p` (se a prova pedir `8080:8080`, apague a linha `server.port`) |
| IP da máquina | secret `HOST_TEST` (ou `EC2_HOST`) **e** `vercel.json` do front |
| Usuário do Docker Hub | `DOCKER_IMAGE` e `DOCKER_USER` no `deploy.yml` |
| Nome do container | `CONTAINER_NAME` no `deploy.yml` |

---

## 5. Deu erro? Tabela de problemas

| Sintoma | Causa | Solução |
|---|---|---|
| Actions vermelho em **Build with Maven** | erro de compilação | abra o passo: aparece `[ERROR] /.../Arquivo.java:[linha]` com o motivo. Rode `./mvnw -q compile` local |
| `cannot find symbol ... getNota()` | usa um campo que não existe mais | ajuste o `validar()`, `atualizar()` ou o controller |
| Actions vermelho em **Login to Docker Hub** | `DOCKERHUB_TOKEN` errado ou expirado | gere outro token (Read & Write) |
| Actions vermelho em **Deploy via SSH**, sem logs | chave ou IP errados, ou EC2 desligada | confira `HOST_TEST`/`KEY_TEST` (ou `EC2_HOST`/`EC2_SSH_KEY`) |
| **Deploy via SSH** mostra `No property 'nota' found for type` | método do repository com campo que não existe | apague ou renomeie o método no `AvalacioesRepository` |
| **Deploy via SSH** mostra `Could not resolve placeholder 'AUTH0_DOMAIN'` | faltam os secrets do Auth0 | cadastre `AUTH0_DOMAIN` e `AUTH0_AUDIENCE` |
| Site: **"Falta configurar o Auth0"** | faltam variáveis na Vercel | cadastre as 3 `VITE_AUTH0_*` (tipo Config) e faça **Redeploy** |
| Login: **Callback URL mismatch** | URL do site não está no Auth0 | Auth0 › Applications › SPA › Allowed Callback/Logout URLs e Web Origins |
| Login: **Client … is not authorized to access resource server** | SPA não autorizada na API | Auth0 › APIs › API › Application Access › Front › User Access: Authorized |
| **403 Acesso negado … seu token tem []** | usuário sem role | atribua a role (User Management › Users › Roles), confira a Action e **saia e entre de novo** |
| **401 Token inválido: The aud claim is not valid** | audience diferente | `AUTH0_AUDIENCE` (secret) = `VITE_AUTH0_AUDIENCE` (Vercel) = Identifier da API |
| **401 … iss claim is not valid** ou **Unable to resolve the Configuration** | domínio errado | `AUTH0_DOMAIN` sem `https://` e sem `/` no final |
| **400 O token não tem email** | Action sem o claim de email | confira a Action (seção 6) |
| **400 JSON parse error** | tipo errado (texto num campo número) | confira o `tipo` no `CAMPOS` do front |
| **500** depois de mudar tipo de campo | coluna antiga no banco | Run workflow com **"Apagar o banco"** |
| **404** em rota nova | caminho diferente no back e no front | confira `@RequestMapping`, `@GetMapping("...")` e `src/api.js` |
| **405 Method Not Allowed** | rota existe, mas não com esse método | confira `@GetMapping`/`@PostMapping`/`@DeleteMapping` |
| Lista vazia, mas tem dados | filtro por email (D1/D2) | o email do token é o email de login (Google ou senha) |

**Ver logs na máquina:**
```bash
ssh -i projsoft26b.pem ubuntu@13.220.42.157
docker ps                 # "api" e "postgres-aula" estão Up?
docker logs -f api        # erros da API em tempo real (Ctrl+C sai)
docker exec -it postgres-aula psql -U usuario -d auladb -c "select * from Avalacioes;"
```

---

## 6. Configuração do Auth0 (do zero)

Faça só se precisar de um tenant novo. Siga a ordem.

1. **API**: Applications › APIs › **+ Create API**
   - Name: `API Avaliacoes`
   - Identifier: `https://avaliacoes-api` (este é o **AUDIENCE**; não dá para mudar depois)
2. **Aplicação SPA**: Applications › Applications › **+ Create Application** › **Single Page Web Applications**
   - Copie o **Domain** e o **Client ID**
   - Em **Allowed Callback URLs**, **Allowed Logout URLs** e **Allowed Web Origins**:
     `http://localhost:5173, https://frontend-simulado-pf.vercel.app` › **Save Changes**
3. **Autorizar a SPA na API**: APIs › API Avaliacoes › **Application Access** › Front › Edit › **User Access** ›
   **Always grant all permissions** › Save.
4. **Roles**: User Management › Roles › crie `ADMIN` e `USER` (maiúsculas).
5. **Usuários**: quem entra com **Google** é criado sozinho no primeiro login, mas **sem role**.
   Atribua em User Management › Users › (usuário) › **Roles** › **Assign Roles**.
6. **Action** (põe roles e email no token): Actions › Triggers › **post-login** › **+** › Build from scratch.
   Cole, clique em **Deploy**, arraste entre *Start* e *Complete* e clique em **Apply**:
   ```js
   exports.onExecutePostLogin = async (event, api) => {
     const namespace = 'https://avaliacoes-insper.com'; // ⭐ igual ao NAMESPACE do controller e do front
     const roles = event.authorization?.roles || [];
     api.accessToken.setCustomClaim(`${namespace}/roles`, roles);
     api.accessToken.setCustomClaim(`${namespace}/email`, event.user.email);
     api.idToken.setCustomClaim(`${namespace}/roles`, roles);
   };
   ```

> Mudou a role de alguém? A pessoa precisa **sair e entrar de novo**.

**Conferir o token:** DevTools (F12) › Network › chamada `Avalacioess` › copie o header `Authorization`
sem o `Bearer ` › cole em **jwt.io**. Tem que aparecer `"https://avaliacoes-insper.com/roles": ["ADMIN"]`.

---

## 7. Secrets e deploy

**Secrets** (Settings › Secrets and variables › Actions):

| Secret | Valor |
|---|---|
| `DOCKERHUB_TOKEN` | hub.docker.com › Account settings › Personal access tokens (Read & Write) |
| `HOST_TEST` (ou `EC2_HOST`) | `13.220.42.157` |
| `KEY_TEST` (ou `EC2_SSH_KEY`) | conteúdo **inteiro** do `.pem`. No Mac: `pbcopy < projsoft26b.pem` |
| `AUTH0_DOMAIN` | ex.: `dev-xxxx.us.auth0.com` (sem `https://`) |
| `AUTH0_AUDIENCE` | `https://avaliacoes-api` |

`HOST_TEST` e `KEY_TEST` são os nomes do professor. O workflow aceita os dois nomes.
O usuário do Docker Hub fica no `deploy.yml` (`DOCKER_USER` e `DOCKER_IMAGE`), igual ao do professor.

**O que o deploy faz** ([deploy.yml](.github/workflows/deploy.yml)):
1. `mvn -B package` (compila; se tiver erro de Java, para aqui);
2. build e push da imagem `nadertaha06/api-avaliacoes:<commit>` no Docker Hub;
3. SSH na EC2:
   - cria a rede `rede` e o container `postgres-aula` (só na primeira vez; dados no volume `postgres-data`);
   - `docker pull` e
     ```bash
     docker run -d --name api --restart unless-stopped -p 8080:8000 \
       -e DB_HOST=postgres-aula -e AUTH0_DOMAIN=... -e AUTH0_AUDIENCE=... \
       --network=rede nadertaha06/api-avaliacoes:<commit>
     ```
   - espera a API responder (sem token ela responde **401**, que quer dizer "no ar e protegida"). Se não subir, mostra os logs.

**Quando roda:** todo push na `main` (mudança só em `.md` não dispara) ou em Actions › **Run workflow** (com a opção de apagar o banco).

---
---

## 9. O que é igual e o que é diferente do professor

**Igual:** pacotes `br.edu.insper.<projeto>` com a pasta da entidade (`Avalacioes/`) e `config/`; Lombok
`@Getter @Setter`; `@Autowired` nos campos; Controller → Service → Repository; `WebSecurityConfig` com
`oauth2ResourceServer(jwt(Customizer.withDefaults()))`; roles lidas com `@AuthenticationPrincipal Jwt jwt` e
`jwt.getClaimAsStringList(".../roles")`; PostgreSQL `postgres-aula` na rede `rede`; Dockerfile em 2 estágios
com Java 25; workflow com `setup-java`, `build-push-action` e `appleboy/ssh-action`.

**Diferente, de propósito:**
- `server.port=8000`, porque a prova pede `-p 8080:8000` (o professor usa 8080).
- `spring.security.oauth2.resourceserver.jwt.audiences` (**com s**). O professor escreve `audience`, que não existe no Spring 4 e é ignorado: a audience não é conferida.
- `issuer-uri` e `audiences` vêm dos secrets (`AUTH0_DOMAIN`, `AUTH0_AUDIENCE`). Se quiser igual ao professor, coloque o valor fixo no `application.properties`.
- O workflow cria o Postgres sozinho, faz login no Docker Hub na EC2 e confere se a API subiu.
- `spring.web.error.include-message=always`, para a mensagem do erro chegar no front.
