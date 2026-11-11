package br.edu.insper.artigos.artigo;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;

@RestController
@RequestMapping("/artigos")                                  // ⭐ ROTA
public class ArtigoController {

    // ⭐ Namespace da Action do Auth0 (igual ao NAMESPACE do front)
    private static final String NAMESPACE = "https://avaliacoes-insper.com";

    @Autowired
    private ArtigoService artigoService;

    // GET /artigos: lista todos os artigos (ADMIN e usuário comum)
    @GetMapping
    public List<Artigo> listarTodos(@AuthenticationPrincipal Jwt jwt) {
        verificarRole(jwt, "ADMIN", "USER");                 // ⭐ quem pode LISTAR
        return artigoService.listarTodos();
    }

    // POST /artigos: cria um artigo (só ADMIN). O e-mail de quem criou vem do token.
    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public Artigo criar(@RequestBody Artigo artigo, @AuthenticationPrincipal Jwt jwt) {
        verificarRole(jwt, "ADMIN");                         // ⭐ quem pode CRIAR
        String email = jwt.getClaimAsString(NAMESPACE + "/email");
        return artigoService.criar(artigo, email);
    }

    // DELETE /artigos/{id}: deleta um artigo existente (só ADMIN)
    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void excluir(@PathVariable Integer id, @AuthenticationPrincipal Jwt jwt) {
        verificarRole(jwt, "ADMIN");                         // ⭐ quem pode DELETAR
        artigoService.excluir(id);
    }

    // ===== Rotas prontas: descomente se a prova pedir (selecione e Cmd+/) =====

    // @GetMapping("/{id}")
    // public Artigo buscarPorId(@PathVariable Integer id, @AuthenticationPrincipal Jwt jwt) {
    //     verificarRole(jwt, "ADMIN", "USER");
    //     return artigoService.buscarPorId(id);
    // }

    // @PutMapping("/{id}")
    // public Artigo atualizar(@PathVariable Integer id, @RequestBody Artigo artigo, @AuthenticationPrincipal Jwt jwt) {
    //     verificarRole(jwt, "ADMIN");
    //     return artigoService.atualizar(id, artigo);
    // }

    // Lê as roles do token (claim {NAMESPACE}/roles) e dá 403 se não tiver nenhuma das permitidas
    private void verificarRole(Jwt jwt, String... rolesPermitidas) {
        List<String> roles = jwt.getClaimAsStringList(NAMESPACE + "/roles");
        if (roles == null) {
            roles = List.of();
        }
        for (String role : rolesPermitidas) {
            if (roles.contains(role)) {
                return;
            }
        }
        throw new ResponseStatusException(HttpStatus.FORBIDDEN,
                "Acesso negado. Precisa de uma das roles " + List.of(rolesPermitidas) + ", seu token tem " + roles);
    }
}
