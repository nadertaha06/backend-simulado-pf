package br.edu.insper.artigos.artigo;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import java.time.LocalDateTime;
import java.util.List;

// ⭐ O que cada rota FAZ: o que o GET lista, o que o POST salva, validações e regras.
//    Erro para o front: throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "mensagem");
@Service
public class ArtigoService {

    @Autowired
    private ArtigoRepository artigoRepository;

    public List<Artigo> listarTodos() {
        // ⭐ o que o GET lista
        return artigoRepository.findAllByOrderByDataCriacaoDesc();
    }

    public Artigo criar(Artigo artigo, String emailUsuario) {
        if (emailUsuario == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST,
                    "O token não tem email. Confira a Action do Auth0.");
        }
        validar(artigo);

        // ⭐ regras de negócio entram aqui

        // ⭐ campos que o servidor preenche
        artigo.setId(null);
        artigo.setEmailUsuario(emailUsuario);
        artigo.setDataCriacao(LocalDateTime.now());
        return artigoRepository.save(artigo);
    }

    public Artigo buscarPorId(Integer id) {
        return artigoRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Artigo não encontrado"));
    }

    public void excluir(Integer id) {
        Artigo artigo = buscarPorId(id);
        artigoRepository.delete(artigo);
    }

    public Artigo atualizar(Integer id, Artigo dados) {
        validar(dados);
        Artigo artigo = buscarPorId(id);
        artigo.setTitulo(dados.getTitulo());
        artigo.setDescricao(dados.getDescricao());
        artigo.setPrioridade(dados.getPrioridade());
        return artigoRepository.save(artigo);
    }

    // ⭐ Validações dos campos que o usuário envia (erro 400 com a mensagem)
    private void validar(Artigo artigo) {
        if (artigo.getTitulo() == null || artigo.getTitulo().isBlank()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "titulo é obrigatório");
        }
        if (artigo.getDescricao() == null || artigo.getDescricao().isBlank()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "descricao é obrigatória");
        }
        if (artigo.getDescricao().length() > 1000) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "descricao deve ter no máximo 1000 caracteres");
        }
        if (!List.of("BAIXA", "MEDIA", "ALTA").contains(artigo.getPrioridade())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "prioridade deve ser BAIXA, MEDIA ou ALTA");
        }
    }
}
