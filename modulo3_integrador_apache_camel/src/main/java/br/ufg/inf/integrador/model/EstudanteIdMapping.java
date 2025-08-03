package br.ufg.inf.integrador.model;

import com.j256.ormlite.field.DatabaseField;
import com.j256.ormlite.table.DatabaseTable;

/**
 * Mapeamento de IDs entre sistemas para Estudante
 * 
 * Esta classe implementa o conceito de correlação de identificadores:
 * - idCanonico: Identificador universal UUID
 * - idSGA: ID no sistema SGA (ORM/SQLite) 
 * - idSB: ID no sistema SB (ODM/MongoDB)
 * - ultimaAtualizacao: Timestamp da última sincronização
 * 
 * Benefícios:
 * - Idempotência: Evita duplicação de dados
 * - Rastreabilidade: Histórico de sincronizações
 * - Extensibilidade: Fácil adição de novos sistemas
 */
@DatabaseTable(tableName = "estudante_id_mapping")
public class EstudanteIdMapping {
    
    @DatabaseField(id = true)
    private String idCanonico;        // Chave primária - UUID universal
    
    @DatabaseField
    private String idSGA;             // ID no Sistema de Gestão Acadêmica
    
    @DatabaseField
    private String idSB;              // ID no Sistema de Biblioteca
    
    @DatabaseField
    private String ultimaAtualizacao; // Timestamp ISO da última sincronização
    
    // Construtor padrão (necessário para ORMLite)
    public EstudanteIdMapping() {}
    
    public EstudanteIdMapping(String idCanonico, String idSGA, String idSB, String ultimaAtualizacao) {
        this.idCanonico = idCanonico;
        this.idSGA = idSGA;
        this.idSB = idSB;
        this.ultimaAtualizacao = ultimaAtualizacao;
    }
    
    // Getters e Setters
    public String getIdCanonico() {
        return idCanonico;
    }
    
    public void setIdCanonico(String idCanonico) {
        this.idCanonico = idCanonico;
    }
    
    public String getIdSGA() {
        return idSGA;
    }
    
    public void setIdSGA(String idSGA) {
        this.idSGA = idSGA;
    }
    
    public String getIdSB() {
        return idSB;
    }
    
    public void setIdSB(String idSB) {
        this.idSB = idSB;
    }
    
    public String getUltimaAtualizacao() {
        return ultimaAtualizacao;
    }
    
    public void setUltimaAtualizacao(String ultimaAtualizacao) {
        this.ultimaAtualizacao = ultimaAtualizacao;
    }
    
    /**
     * Verifica se o mapeamento está completo (possui ambos os IDs)
     */
    public boolean isComplete() {
        return idSGA != null && !idSGA.isEmpty() && 
               idSB != null && !idSB.isEmpty();
    }
    
    /**
     * Verifica se o mapeamento é para criação (apenas ID de origem)
     */
    public boolean isForCreation() {
        return (idSGA != null && !idSGA.isEmpty()) && 
               (idSB == null || idSB.isEmpty());
    }
    
    @Override
    public String toString() {
        return String.format("EstudanteIdMapping{idCanonico='%s', idSGA='%s', idSB='%s', ultimaAtualizacao='%s'}",
                           idCanonico, idSGA, idSB, ultimaAtualizacao);
    }
}