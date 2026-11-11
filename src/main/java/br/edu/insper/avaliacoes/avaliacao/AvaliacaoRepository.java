package br.edu.insper.avaliacoes.avaliacao;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

// ⭐ Consultas: o Spring monta o SQL pelo NOME do método (findBy + Campo + OrderBy + Campo + Desc)
public interface AvaliacaoRepository extends JpaRepository<Avaliacao, Integer> {

    // GET /avaliacoes: todas, mais recentes primeiro
    List<Avaliacao> findAllByOrderByDataAvaliacaoDesc();

    // Exemplos prontos para a prova (use no AvaliacaoService):
    List<Avaliacao> findByEmailAvaliadoOrderByDataAvaliacaoDesc(String emailAvaliado);

    List<Avaliacao> findByEmailAvaliadorOrderByDataAvaliacaoDesc(String emailAvaliador);

    List<Avaliacao> findByNotaGreaterThanEqualOrderByDataAvaliacaoDesc(Integer nota);

    boolean existsByEmailAvaliadorAndEmailAvaliado(String emailAvaliador, String emailAvaliado);
}
