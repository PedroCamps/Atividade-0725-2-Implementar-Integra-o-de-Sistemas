package br.ufg.inf.integrador.routes;

import br.ufg.inf.integrador.model.CrudOperation;
import br.ufg.inf.integrador.processor.CrudProcessor;
import br.ufg.inf.integrador.processor.PersistenciaCanonicoProcessor;
import com.google.gson.Gson;
import org.apache.camel.Exchange;
import org.apache.camel.builder.RouteBuilder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Rota principal de transformação CRUD usando Apache Camel
 * 
 * Implementa os Enterprise Integration Patterns:
 * - Message Router: Direcionamento baseado em condições
 * - Message Translator: Transformação de formatos de dados
 * - Content-Based Router: Roteamento baseado no conteúdo da mensagem
 * - Dynamic Router: Endpoint determinado dinamicamente
 * 
 * Fluxo da rota:
 * 1. Recebe mensagem do endpoint "direct:crud" (vinda do RedisListener)
 * 2. Configura headers HTTP e endpoint baseado na operação
 * 3. Processa e transforma dados (Message Translator)
 * 4. Roteia condicionalmente para HTTP endpoint
 * 5. Persiste dados canônicos e mapeamento de IDs
 */
public class CrudTransformRoute extends RouteBuilder {
    
    private static final Logger logger = LoggerFactory.getLogger(CrudTransformRoute.class);
    private final Gson gson = new Gson();
    
    @Override
    public void configure() throws Exception {
        
        // Configuração global de tratamento de erros
        onException(Exception.class)
            .handled(true)
            .log("❌ Erro no processamento: ${exception.message}")
            .to("log:error?level=ERROR");
        
        // ROTA PRINCIPAL DE TRANSFORMAÇÃO CRUD
        from("direct:crud")
            .routeId("crud-transformer")
            .log("📥 Mensagem recebida: ${body}")
            
            // 1. PREPARAR HEADERS E PROPRIEDADES
            // Extrai informações da operação CRUD e configura headers HTTP
            .process(this::setOperationHeaders)
            
            // 2. TRANSFORMAR DADOS (Message Translator Pattern)
            // Converte formato de origem para formato de destino
            .process(new CrudProcessor())
            
            // 3. ROTEAMENTO CONDICIONAL (Content-Based Router Pattern)
            .choice()
                // Se processamento foi bem-sucedido
                .when(exchangeProperty("CamelSkipSendToEndpoint").isNotEqualTo(true))
                    .log("✅ JSON processado: ${body}")
                    .setHeader("Content-Type", constant("application/json;charset=UTF-8"))
                    
                    // 4. ENVIO DINÂMICO PARA ENDPOINT (Dynamic Router Pattern)
                    // Endpoint é determinado dinamicamente baseado na entidade
                    .toD("${header.targetEndpoint}")
                    
                    // Log da resposta HTTP
                    .log("📤 Resposta HTTP: Status=${header.CamelHttpResponseCode}, Body=${body}")
                    
                    // 5. PERSISTÊNCIA CANÔNICA (apenas para Estudante/CREATE)
                    // Filtra e persiste dados canônicos + mapeamento de IDs
                    .filter().simple("${exchangeProperty.crudEntity.toLowerCase()} == 'estudante' && ${exchangeProperty.crudOperation} == 'CREATE'")
                        .process(new PersistenciaCanonicoProcessor())
                        .log("💾 Dados canônicos persistidos")
                    .end()
                
                // Se processamento falhou ou operação não suportada
                .otherwise()
                    .log("⚠️ Mensagem ignorada pelo processador")
            .end();
    }
    
    /**
     * Processa a mensagem original para extrair informações da operação CRUD
     * e configurar os headers apropriados para o método HTTP e endpoint
     * 
     * Implementa parte do Message Router Pattern
     */
    private void setOperationHeaders(Exchange exchange) throws Exception {
        String json = exchange.getIn().getBody(String.class);
        CrudOperation op = gson.fromJson(json, CrudOperation.class);
        
        logger.debug("🔍 Processando operação: {}", op);
        
        // Mapear operação CRUD para método HTTP
        String httpMethod = mapOperationToHttpMethod(op.getOperation());
        exchange.getIn().setHeader("CamelHttpMethod", httpMethod);
        
        // Mapear entidade para endpoint de destino
        String endpoint = mapEntityToEndpoint(op.getEntity(), op.getOperation());
        exchange.getIn().setHeader("targetEndpoint", endpoint);
        
        // Armazenar informações da operação para uso posterior nos processadores
        exchange.setProperty("crudOperation", op.getOperation().toString());
        exchange.setProperty("crudEntity", op.getEntity());
        exchange.setProperty("crudSource", op.getSource().toString());
        
        logger.info("🎯 Headers configurados - Método: {}, Endpoint: {}", httpMethod, endpoint);
    }
    
    /**
     * Mapeia operações CRUD para métodos HTTP
     */
    private String mapOperationToHttpMethod(CrudOperation.OperationType operation) {
        switch (operation) {
            case CREATE:
                return "POST";
            case UPDATE:
                return "PUT";
            case DELETE:
                return "DELETE";
            default:
                return "GET";
        }
    }
    
    /**
     * Mapeia entidades para endpoints HTTP de destino
     * 
     * Implementa lógica de roteamento para diferentes tipos de entidade
     */
    private String mapEntityToEndpoint(String entity, CrudOperation.OperationType operation) {
        String baseUrl = "http://localhost:8080";
        String endpoint;
        
        // Mapear entidade para endpoint específico
        switch (entity.toLowerCase()) {
            case "estudante":
                endpoint = baseUrl + "/usuarios";
                break;
            case "professor":
                endpoint = baseUrl + "/professores";
                break;
            case "disciplina":
                endpoint = baseUrl + "/disciplinas";
                break;
            case "obra":
                endpoint = baseUrl + "/obras";
                break;
            default:
                // Endpoint genérico baseado no nome da entidade
                endpoint = baseUrl + "/" + entity.toLowerCase() + "s";
        }
        
        // Configurações específicas do Apache Camel HTTP component
        return endpoint + "?throwExceptionOnFailure=false&bridgeEndpoint=true&charset=UTF-8";
    }
}