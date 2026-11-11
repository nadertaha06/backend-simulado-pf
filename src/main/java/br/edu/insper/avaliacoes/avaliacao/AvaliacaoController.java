package br.edu.insper.avaliacoes.avaliacao;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;

@RestController
@RequestMapping("/avaliacoes")                              // ⭐ ROTA
public class AvaliacaoController {

    // ⭐ Namespace da Action do Auth0 (igual ao NAMESPACE do front)
    private static final String NAMESPACE = "https://avaliacoes-insper.com";

    @Autowired
    private AvaliacaoService avaliacaoService;

    @GetMapping
    public List<Avaliacao> listarTodas(@AuthenticationPrincipal Jwt jwt) {
        verificarRole(jwt, "ADMIN", "USER");                 // ⭐ quem pode LISTAR
        return avaliacaoService.listarTodas();
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public Avaliacao criar(@RequestBody Avaliacao avaliacao, @AuthenticationPrincipal Jwt jwt) {
        verificarRole(jwt, "ADMIN");                         // ⭐ quem pode CADASTRAR
        String email = jwt.getClaimAsString(NAMESPACE + "/email");
        return avaliacaoService.criar(avaliacao, email);
    }

    // ===== Rotas prontas: descomente se a prova pedir (selecione e Cmd+/) =====

    // @GetMapping("/{id}")
    // public Avaliacao buscarPorId(@PathVariable Integer id, @AuthenticationPrincipal Jwt jwt) {
    //     verificarRole(jwt, "ADMIN", "USER");
    //     return avaliacaoService.buscarPorId(id);
    // }

    // @DeleteMapping("/{id}")
    // @ResponseStatus(HttpStatus.NO_CONTENT)
    // public void excluir(@PathVariable Integer id, @AuthenticationPrincipal Jwt jwt) {
    //     verificarRole(jwt, "ADMIN");
    //     avaliacaoService.excluir(id);
    // }

    // @PutMapping("/{id}")
    // public Avaliacao atualizar(@PathVariable Integer id, @RequestBody Avaliacao avaliacao, @AuthenticationPrincipal Jwt jwt) {
    //     verificarRole(jwt, "ADMIN");
    //     return avaliacaoService.atualizar(id, avaliacao);
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
