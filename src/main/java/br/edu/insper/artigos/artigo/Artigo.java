package br.edu.insper.artigos.artigo;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDateTime;

// ⭐ CAMPOS da entidade (viram as colunas da tabela e o JSON da API).
//    O nome de cada campo tem que ser igual ao "nome" no CAMPOS do front.
@Entity
@Getter
@Setter
public class Artigo {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;
    private String titulo;
    @Column(length = 1000)
    private String descricao;
    private String prioridade;         // BAIXA, MEDIA ou ALTA
    private String emailUsuario;       // o servidor preenche (email do token de quem criou)
    private LocalDateTime dataCriacao; // o servidor preenche (agora)
}
