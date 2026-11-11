package br.edu.insper.avaliacoes.avaliacao;

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
public class Avaliacao {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;
    private String emailAvaliador;      // o servidor preenche (email do token)
    private String emailAvaliado;
    @Column(length = 1000)
    private String comentarios;
    private Integer nota;               // 0 a 10
    private LocalDateTime dataAvaliacao; // o servidor preenche (agora)
}
