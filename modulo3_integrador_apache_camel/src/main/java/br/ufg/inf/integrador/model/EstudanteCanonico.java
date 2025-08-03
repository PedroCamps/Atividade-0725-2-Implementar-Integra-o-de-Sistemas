package br.ufg.inf.integrador.model;

import com.j256.ormlite.field.DatabaseField;
import com.j256.ormlite.table.DatabaseTable;

/**
 * Modelo de Dados Canônico para Estudante
 * 
 * Implementa o padrão Canonical Data Model (CDM):
 * - Serve como formato intermediário entre sistemas SGA e SB
 * - Possui identificador universal (UUID)
 * - Contém campos normalizados de ambos os sistemas
 * - Evita acoplamento direto entre modelos de origem e destino
 */
@DatabaseTable(tableName = "estudante_canonico")
public class EstudanteCanonico {
    
    @DatabaseField(id = true)
    private String idCanonico;        // Identificador universal UUID
    
    @DatabaseField
    private String prenome;           // Primeiro nome (derivado de nome_completo)
    
    @DatabaseField  
    private String sobrenome;         // Sobrenome (derivado de nome_completo)
    
    @DatabaseField
    private String nomeCompleto;      // Nome completo original (SGA)
    
    @DatabaseField
    private String dataDeNascimento;  // Data nascimento (formato string)
    
    @DatabaseField
    private String matricula;         // Número de matrícula (como string)
    
    @DatabaseField
    private String statusAcademico;   // Status no sistema acadêmico
    
    @DatabaseField
    private String statusBiblioteca;  // Status empréstimos biblioteca
    
    // Construtor padrão (necessário para ORMLite)
    public EstudanteCanonico() {}
    
    public EstudanteCanonico(String idCanonico, String prenome, String sobrenome, 
                           String nomeCompleto, String dataDeNascimento, String matricula,
                           String statusAcademico, String statusBiblioteca) {
        this.idCanonico = idCanonico;
        this.prenome = prenome;
        this.sobrenome = sobrenome;
        this.nomeCompleto = nomeCompleto;
        this.dataDeNascimento = dataDeNascimento;
        this.matricula = matricula;
        this.statusAcademico = statusAcademico;
        this.statusBiblioteca = statusBiblioteca;
    }
    
    // Getters e Setters
    public String getIdCanonico() {
        return idCanonico;
    }
    
    public void setIdCanonico(String idCanonico) {
        this.idCanonico = idCanonico;
    }
    
    public String getPrenome() {
        return prenome;
    }
    
    public void setPrenome(String prenome) {
        this.prenome = prenome;
    }
    
    public String getSobrenome() {
        return sobrenome;
    }
    
    public void setSobrenome(String sobrenome) {
        this.sobrenome = sobrenome;
    }
    
    public String getNomeCompleto() {
        return nomeCompleto;
    }
    
    public void setNomeCompleto(String nomeCompleto) {
        this.nomeCompleto = nomeCompleto;
    }
    
    public String getDataDeNascimento() {
        return dataDeNascimento;
    }
    
    public void setDataDeNascimento(String dataDeNascimento) {
        this.dataDeNascimento = dataDeNascimento;
    }
    
    public String getMatricula() {
        return matricula;
    }
    
    public void setMatricula(String matricula) {
        this.matricula = matricula;
    }
    
    public String getStatusAcademico() {
        return statusAcademico;
    }
    
    public void setStatusAcademico(String statusAcademico) {
        this.statusAcademico = statusAcademico;
    }
    
    public String getStatusBiblioteca() {
        return statusBiblioteca;
    }
    
    public void setStatusBiblioteca(String statusBiblioteca) {
        this.statusBiblioteca = statusBiblioteca;
    }
    
    @Override
    public String toString() {
        return String.format("EstudanteCanonico{idCanonico='%s', prenome='%s', sobrenome='%s', " +
                           "nomeCompleto='%s', matricula='%s', statusAcademico='%s', statusBiblioteca='%s'}",
                           idCanonico, prenome, sobrenome, nomeCompleto, matricula, 
                           statusAcademico, statusBiblioteca);
    }
}