package br.ufg.inf.integrador;

import br.ufg.inf.integrador.model.CrudOperation;
import br.ufg.inf.integrador.redis.RedisListener;
import com.google.gson.Gson;
import io.lettuce.core.RedisClient;
import io.lettuce.core.api.StatefulRedisConnection;
import io.lettuce.core.api.sync.RedisCommands;
import org.apache.camel.ProducerTemplate;
import org.apache.camel.impl.DefaultCamelContext;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * Classe para teste manual do integrador
 * 
 * Simula a criação de um estudante no SGA e publicação do evento no Redis,
 * permitindo testar o fluxo completo de integração sem precisar executar
 * o sistema SGA completo.
 */
public class MainTest {
    
    private static final Logger logger = LoggerFactory.getLogger(MainTest.class);
    private static final String REDIS_URL = "redis://localhost:6379";
    private static final String CRUD_CHANNEL = "crud-channel";
    
    private final Gson gson = new Gson();
    
    public static void main(String[] args) {
        MainTest test = new MainTest();
        test.executarTeste();
    }
    
    public void executarTeste() {
        logger.info("🧪 Teste Manual do Integrador Apache Camel");
        logger.info("📝 Este teste simula a criação de um estudante no SGA");
        
        try {
            // Verificar conectividade Redis
            if (!verificarRedis()) {
                logger.error("❌ Redis não está acessível. Certifique-se de que está rodando.");
                return;
            }
            
            // Criar evento CRUD simulado
            CrudOperation evento = criarEventoTeste();
            
            // Publicar evento no Redis
            publicarEvento(evento);
            
            logger.info("✅ Evento publicado com sucesso!");
            logger.info("🔄 O integrador deve processar este evento automaticamente");
            logger.info("📋 Verifique os logs do integrador e do Sistema de Biblioteca");
            
        } catch (Exception e) {
            logger.error("❌ Erro durante o teste: {}", e.getMessage(), e);
        }
    }
    
    /**
     * Verifica se o Redis está acessível
     */
    private boolean verificarRedis() {
        try {
            RedisClient client = RedisClient.create(REDIS_URL);
            StatefulRedisConnection<String, String> connection = client.connect();
            RedisCommands<String, String> commands = connection.sync();
            
            String response = commands.ping();
            
            connection.close();
            client.shutdown();
            
            logger.info("✅ Redis conectado: {}", response);
            return "PONG".equals(response);
            
        } catch (Exception e) {
            logger.error("❌ Erro ao conectar ao Redis: {}", e.getMessage());
            return false;
        }
    }
    
    /**
     * Cria um evento CRUD de teste simulando dados do SGA
     */
    private CrudOperation criarEventoTeste() {
        // Simular dados de um estudante do SGA
        String dadosEstudante = "{\n" +
            "  \"id\": 999,\n" +
            "  \"nome_completo\": \"João da Silva Teste\",\n" +
            "  \"data_de_nascimento\": \"01/01/2000\",\n" +
            "  \"matricula\": 123456,\n" +
            "  \"status_emprestimo_livros\": \"QUITADO\"\n" +
            "}";
        
        // Criar operação CRUD
        CrudOperation evento = new CrudOperation(
            "Estudante",                           // Entidade
            CrudOperation.OperationType.CREATE,   // Operação
            CrudOperation.Source.ORM,             // Fonte (SGA)
            dadosEstudante,                       // Dados JSON
            LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME) // Timestamp
        );
        
        logger.info("📋 Evento criado: {}", evento);
        logger.info("📊 Dados do estudante: {}", dadosEstudante);
        
        return evento;
    }
    
    /**
     * Publica o evento no canal Redis
     */
    private void publicarEvento(CrudOperation evento) {
        RedisClient client = null;
        StatefulRedisConnection<String, String> connection = null;
        
        try {
            logger.info("📡 Publicando evento no Redis...");
            
            // Conectar ao Redis
            client = RedisClient.create(REDIS_URL);
            connection = client.connect();
            RedisCommands<String, String> commands = connection.sync();
            
            // Serializar evento para JSON
            String eventoJson = gson.toJson(evento);
            
            // Publicar no canal
            Long subscribers = commands.publish(CRUD_CHANNEL, eventoJson);
            
            logger.info("📤 Evento publicado no canal '{}' para {} subscriber(s)", 
                       CRUD_CHANNEL, subscribers);
            logger.debug("📋 Conteúdo publicado: {}", eventoJson);
            
            if (subscribers == 0) {
                logger.warn("⚠️ Nenhum subscriber ativo no canal. " +
                           "Certifique-se de que o integrador está rodando.");
            }
            
        } catch (Exception e) {
            logger.error("❌ Erro ao publicar evento: {}", e.getMessage(), e);
            throw new RuntimeException("Falha na publicação do evento", e);
            
        } finally {
            // Cleanup
            if (connection != null) {
                connection.close();
            }
            if (client != null) {
                client.shutdown();
            }
        }
    }
}