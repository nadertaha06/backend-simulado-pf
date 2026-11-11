package br.edu.insper.avaliacoes.avaliacao;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import java.time.LocalDateTime;
import java.util.List;

// ⭐ O que cada rota FAZ: o que o GET lista, o que o POST salva, validações e regras.
//    Erro para o front: throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "mensagem");
@Service
public class AvaliacaoService {

    @Autowired
    private AvaliacaoRepository avaliacaoRepository;

    public List<Avaliacao> listarTodas() {
        // ⭐ o que o GET lista
        return avaliacaoRepository.findAllByOrderByDataAvaliacaoDesc();
    }

    public Avaliacao criar(Avaliacao avaliacao, String emailAvaliador) {
        if (emailAvaliador == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST,
                    "O token não tem email. Confira a Action do Auth0.");
        }
        validar(avaliacao);

        // ⭐ regras de negócio entram aqui (ex.: não pode avaliar a si mesmo)

        // ⭐ campos que o servidor preenche
        avaliacao.setId(null);
        avaliacao.setEmailAvaliador(emailAvaliador);
        avaliacao.setDataAvaliacao(LocalDateTime.now());
        return avaliacaoRepository.save(avaliacao);
    }

    public Avaliacao buscarPorId(Integer id) {
        return avaliacaoRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Avaliação não encontrada"));
    }

    public void excluir(Integer id) {
        Avaliacao avaliacao = buscarPorId(id);
        avaliacaoRepository.delete(avaliacao);
    }

    public Avaliacao atualizar(Integer id, Avaliacao dados) {
        validar(dados);
        Avaliacao avaliacao = buscarPorId(id);
        avaliacao.setEmailAvaliado(dados.getEmailAvaliado());
        avaliacao.setComentarios(dados.getComentarios());
        avaliacao.setNota(dados.getNota());
        return avaliacaoRepository.save(avaliacao);
    }

    // ⭐ Validações dos campos que o usuário envia (erro 400 com a mensagem)
    private void validar(Avaliacao avaliacao) {
        if (avaliacao.getEmailAvaliado() == null || !avaliacao.getEmailAvaliado().matches("^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$")) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "emailAvaliado deve ser um email válido");
        }
        if (avaliacao.getComentarios() == null || avaliacao.getComentarios().isBlank()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "comentarios é obrigatório");
        }
        if (avaliacao.getNota() == null || avaliacao.getNota() < 0 || avaliacao.getNota() > 10) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "nota deve ser de 0 a 10");
        }
    }
}
