package br.ufg.inf.integrador.model;

/**
 * Representa uma operação CRUD recebida via Redis
 * 
 * Esta classe modela o formato das mensagens publicadas pelos sistemas
 * SGA e SB quando realizam operações de banco de dados.
 */
public class CrudOperation {
    
    /**
     * Tipos de operação CRUD suportados
     */
    public enum OperationType {
        CREATE("CREATE"),
        UPDATE("UPDATE"), 
        DELETE("DELETE");
        
        private final String value;
        
        OperationType(String value) {
            this.value = value;
        }
        
        public String getValue() {
            return value;
        }
        
        public static OperationType fromString(String value) {
            for (OperationType type : values()) {
                if (type.value.equalsIgnoreCase(value)) {
                    return type;
                }
            }
            throw new IllegalArgumentException("Tipo de operação inválido: " + value);
        }
    }
    
    /**
     * Sistemas origem das operações
     */
    public enum Source {
        ORM("ORM"),   // Sistema SGA (ORM/SQLite)
        ODM("ODM");   // Sistema SB (ODM/MongoDB)
        
        private final String value;
        
        Source(String value) {
            this.value = value;
        }
        
        public String getValue() {
            return value;
        }
        
        public static Source fromString(String value) {
            for (Source source : values()) {
                if (source.value.equalsIgnoreCase(value)) {
                    return source;
                }
            }
            throw new IllegalArgumentException("Fonte inválida: " + value);
        }
    }
    
    private String entity;          // Nome da entidade (ex: "Estudante")
    private OperationType operation; // Tipo da operação (CREATE, UPDATE, DELETE)
    private Source source;          // Sistema origem (ORM, ODM)
    private String data;            // Dados da entidade em JSON
    private String timestamp;       // Timestamp da operação
    
    // Construtor padrão (necessário para deserialização JSON)
    public CrudOperation() {}
    
    public CrudOperation(String entity, OperationType operation, Source source, String data, String timestamp) {
        this.entity = entity;
        this.operation = operation;
        this.source = source;
        this.data = data;
        this.timestamp = timestamp;
    }
    
    // Getters e Setters
    public String getEntity() {
        return entity;
    }
    
    public void setEntity(String entity) {
        this.entity = entity;
    }
    
    public OperationType getOperation() {
        return operation;
    }
    
    public void setOperation(OperationType operation) {
        this.operation = operation;
    }
    
    public Source getSource() {
        return source;
    }
    
    public void setSource(Source source) {
        this.source = source;
    }
    
    public String getData() {
        return data;
    }
    
    public void setData(String data) {
        this.data = data;
    }
    
    public String getTimestamp() {
        return timestamp;
    }
    
    public void setTimestamp(String timestamp) {
        this.timestamp = timestamp;
    }
    
    @Override
    public String toString() {
        return String.format("CrudOperation{entity='%s', operation=%s, source=%s, timestamp='%s'}",
                entity, operation, source, timestamp);
    }
}