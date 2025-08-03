package br.ufg.inf.integrador;

import br.ufg.inf.integrador.model.CrudOperation;
import br.ufg.inf.integrador.processor.EstudanteProcessor;
import br.ufg.inf.integrador.processor.CrudProcessor;
import com.google.gson.Gson;
import org.apache.camel.Exchange;
import org.apache.camel.impl.DefaultCamelContext;
import org.apache.camel.support.DefaultExchange;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Testes unitários para processamento de eventos CRUD
 */
class CrudEventsTest {
    
    private Gson gson;
    private EstudanteProcessor estudanteProcessor;
    private CrudProcessor crudProcessor;
    private DefaultCamelContext camelContext;
    
    @BeforeEach
    void setUp() {
        gson = new Gson();
        estudanteProcessor = new EstudanteProcessor();
        crudProcessor = new CrudProcessor();
        camelContext = new DefaultCamelContext();
    }
    
    @Test
    @DisplayName("Deve extrair prenome e sobrenome corretamente")
    void testExtrairPrenomeESobrenome() {
        // Teste com nome completo
        String[] resultado = estudanteProcessor.extrairPrenomeESobrenome("João da Silva");
        assertEquals("João", resultado[0]);
        assertEquals("da Silva", resultado[1]);
        
        // Teste com nome simples
        resultado = estudanteProcessor.extrairPrenomeESobrenome("Maria");
        assertEquals("Maria", resultado[0]);
        assertEquals("", resultado[1]);
        
        // Teste com nome vazio
        resultado = estudanteProcessor.extrairPrenomeESobrenome("");
        assertEquals("", resultado[0]);
        assertEquals("", resultado[1]);
        
        // Teste com null
        resultado = estudanteProcessor.extrairPrenomeESobrenome(null);
        assertEquals("", resultado[0]);
        assertEquals("", resultado[1]);
    }
    
    @Test
    @DisplayName("Deve transformar Estudante para Usuario corretamente")
    void testEstudanteParaUsuario() {
        // Dados de entrada (formato SGA)
        String dadosEstudante = "{\n" +
            "  \"id\": 1,\n" +
            "  \"nome_completo\": \"Pedro Santos Oliveira\",\n" +
            "  \"data_de_nascimento\": \"22/08/2001\",\n" +
            "  \"matricula\": 345678,\n" +
            "  \"status_emprestimo_livros\": \"QUITADO\"\n" +
            "}";
        
        // Executar transformação
        String resultado = estudanteProcessor.estudanteParaUsuario(dadosEstudante);
        
        // Verificar resultado
        assertNotNull(resultado);
        assertTrue(resultado.contains("\"prenome\":\"Pedro\""));
        assertTrue(resultado.contains("\"sobrenome\":\"Santos Oliveira\""));
        assertTrue(resultado.contains("\"situacao_matricula\":\"ATIVO\""));
    }
    
    @Test
    @DisplayName("Deve criar EstudanteCanonico corretamente")
    void testEstudanteParaEstudanteCanonico() {
        String dadosEstudante = "{\n" +
            "  \"id\": 2,\n" +
            "  \"nome_completo\": \"Ana Carolina Costa\",\n" +
            "  \"data_de_nascimento\": \"10/05/1998\",\n" +
            "  \"matricula\": 456789,\n" +
            "  \"status_emprestimo_livros\": \"EM_ABERTO\"\n" +
            "}";
        
        String idCanonico = "test-uuid-123";
        
        var canonico = estudanteProcessor.estudanteParaEstudanteCanonico(dadosEstudante, idCanonico);
        
        assertNotNull(canonico);
        assertEquals(idCanonico, canonico.getIdCanonico());
        assertEquals("Ana", canonico.getPrenome());
        assertEquals("Carolina Costa", canonico.getSobrenome());
        assertEquals("Ana Carolina Costa", canonico.getNomeCompleto());
        assertEquals("10/05/1998", canonico.getDataDeNascimento());
        assertEquals("456789", canonico.getMatricula());
        assertEquals("ATIVO", canonico.getStatusAcademico());
        assertEquals("EM_ABERTO", canonico.getStatusBiblioteca());
    }
    
    @Test
    @DisplayName("Deve processar operação CREATE do ORM corretamente")
    void testCrudProcessorCreate() throws Exception {
        // Mensagem CRUD de entrada
        CrudOperation operation = new CrudOperation(
            "Estudante",
            CrudOperation.OperationType.CREATE,
            CrudOperation.Source.ORM,
            "{\"id\": 1, \"nome_completo\": \"João Silva\", \"matricula\": 123456}",
            "2024-01-01T10:00:00"
        );
        
        String mensagemJson = gson.toJson(operation);
        
        // Criar exchange do Camel
        Exchange exchange = new DefaultExchange(camelContext);
        exchange.getIn().setBody(mensagemJson);
        
        // Processar
        crudProcessor.process(exchange);
        
        // Verificar resultado
        String corpo = exchange.getIn().getBody(String.class);
        assertNotNull(corpo);
        assertTrue(corpo.contains("\"prenome\":\"João\""));
        assertTrue(corpo.contains("\"sobrenome\":\"Silva\""));
        
        // Verificar propriedades do exchange
        CrudOperation opOriginal = (CrudOperation) exchange.getProperty("CrudOriginal");
        assertNotNull(opOriginal);
        assertEquals("Estudante", opOriginal.getEntity());
    }
    
    @Test
    @DisplayName("Deve ignorar operações não suportadas")
    void testCrudProcessorUnsupported() throws Exception {
        // Operação UPDATE (não suportada)
        CrudOperation operation = new CrudOperation(
            "Estudante",
            CrudOperation.OperationType.UPDATE,
            CrudOperation.Source.ORM,
            "{\"id\": 1}",
            "2024-01-01T10:00:00"
        );
        
        String mensagemJson = gson.toJson(operation);
        
        Exchange exchange = new DefaultExchange(camelContext);
        exchange.getIn().setBody(mensagemJson);
        
        crudProcessor.process(exchange);
        
        // Deve marcar para pular envio
        Boolean skip = (Boolean) exchange.getProperty("CamelSkipSendToEndpoint");
        assertTrue(skip);
    }
    
    @Test
    @DisplayName("Deve ignorar operações de fonte ODM")
    void testCrudProcessorODMSource() throws Exception {
        // Operação CREATE mas de fonte ODM (não suportada)
        CrudOperation operation = new CrudOperation(
            "Estudante",
            CrudOperation.OperationType.CREATE,
            CrudOperation.Source.ODM,
            "{\"id\": \"507f1f77bcf86cd799439011\"}",
            "2024-01-01T10:00:00"
        );
        
        String mensagemJson = gson.toJson(operation);
        
        Exchange exchange = new DefaultExchange(camelContext);
        exchange.getIn().setBody(mensagemJson);
        
        crudProcessor.process(exchange);
        
        // Deve marcar para pular envio
        Boolean skip = (Boolean) exchange.getProperty("CamelSkipSendToEndpoint");
        assertTrue(skip);
    }
    
    @Test
    @DisplayName("Deve lidar com dados JSON inválidos")
    void testJsonInvalido() throws Exception {
        String jsonInvalido = "{nome_completo: 'João Silva'"; // JSON malformado
        
        Exchange exchange = new DefaultExchange(camelContext);
        exchange.getIn().setBody(jsonInvalido);
        
        // Deve lançar exceção
        assertThrows(Exception.class, () -> {
            crudProcessor.process(exchange);
        });
    }
    
    @Test
    @DisplayName("Deve gerar UUID automático para modelo canônico")
    void testUUIDAutomatico() {
        String dadosEstudante = "{\n" +
            "  \"nome_completo\": \"Teste Automático\",\n" +
            "  \"matricula\": 999999\n" +
            "}";
        
        var canonico = estudanteProcessor.estudanteParaEstudanteCanonico(dadosEstudante);
        
        assertNotNull(canonico);
        assertNotNull(canonico.getIdCanonico());
        assertFalse(canonico.getIdCanonico().isEmpty());
        assertEquals("Teste", canonico.getPrenome());
        assertEquals("Automático", canonico.getSobrenome());
    }
}