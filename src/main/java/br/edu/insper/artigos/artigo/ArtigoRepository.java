package br.edu.insper.artigos.artigo;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

// ⭐ Consultas: o Spring monta o SQL pelo NOME do método (findBy + Campo + OrderBy + Campo + Desc)
public interface ArtigoRepository extends JpaRepository<Artigo, Integer> {

    // GET /artigos: todos, mais recentes primeiro
    List<Artigo> findAllByOrderByDataCriacaoDesc();

    // Exemplo pronto (use no ArtigoService): só os artigos criados por um usuário
    List<Artigo> findByEmailUsuarioOrderByDataCriacaoDesc(String emailUsuario);
}
