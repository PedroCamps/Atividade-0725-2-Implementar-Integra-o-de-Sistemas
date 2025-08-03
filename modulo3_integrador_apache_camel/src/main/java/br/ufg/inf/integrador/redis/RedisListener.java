package br.ufg.inf.integrador.redis;

import io.lettuce.core.RedisClient;
import io.lettuce.core.pubsub.RedisPubSubAdapter;
import io.lettuce.core.pubsub.StatefulRedisPubSubConnection;
import org.apache.camel.ProducerTemplate;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Listener Redis que consome eventos CRUD e os envia para o Apache Camel
 * 
 * Implementa o padrão Publisher-Subscriber Channel:
 * - Subscreve ao canal 'crud-channel' do Redis
 * - Recebe eventos de operações CRUD dos sistemas SGA/SB
 * - Encaminha mensagens para o Apache Camel via ProducerTemplate
 */
public class RedisListener {
    
    private static final Logger logger = LoggerFactory.getLogger(RedisListener.class);
    private static final String REDIS_URL = "redis://localhost:6379";
    private static final String CRUD_CHANNEL = "crud-channel";
    private static final String CAMEL_ENDPOINT = "direct:crud";
    
    private final ProducerTemplate producer;
    private RedisClient redisClient;
    private StatefulRedisPubSubConnection<String, String> connection;
    
    public RedisListener(ProducerTemplate producer) {
        this.producer = producer;
    }
    
    /**
     * Inicia a escuta do canal Redis
     */
    public void start() {
        try {
            logger.info("🔗 Conectando ao Redis: {}", REDIS_URL);
            
            // Criar cliente Redis
            redisClient = RedisClient.create(REDIS_URL);
            connection = redisClient.connectPubSub();
            
            // Configurar listener para mensagens
            connection.addListener(new RedisPubSubAdapter<String, String>() {
                @Override
                public void message(String channel, String message) {
                    logger.info("🔔 [{}] {}", channel, message);
                    
                    try {
                        // Enviar mensagem para o Apache Camel
                        producer.sendBody(CAMEL_ENDPOINT, message);
                        logger.debug("📤 Mensagem enviada para Camel: {}", CAMEL_ENDPOINT);
                        
                    } catch (Exception e) {
                        logger.error("❌ Erro ao enviar mensagem para Camel: {}", e.getMessage(), e);
                    }
                }
                
                @Override
                public void subscribed(String channel, long count) {
                    logger.info("✅ Subscrito ao canal: {} (total: {})", channel, count);
                }
                
                @Override
                public void unsubscribed(String channel, long count) {
                    logger.info("🔕 Desconectado do canal: {} (restantes: {})", channel, count);
                }
            });
            
            // Subscrever ao canal CRUD
            connection.sync().subscribe(CRUD_CHANNEL);
            logger.info("🟢 Escutando canal Redis: {}", CRUD_CHANNEL);
            
        } catch (Exception e) {
            logger.error("❌ Erro ao iniciar Redis listener: {}", e.getMessage(), e);
            throw new RuntimeException("Falha ao conectar ao Redis", e);
        }
    }
    
    /**
     * Para a escuta e fecha conexões
     */
    public void stop() {
        try {
            if (connection != null) {
                connection.sync().unsubscribe(CRUD_CHANNEL);
                connection.close();
                logger.info("🔕 Conexão Redis fechada");
            }
            
            if (redisClient != null) {
                redisClient.shutdown();
                logger.info("🛑 Cliente Redis finalizado");
            }
            
        } catch (Exception e) {
            logger.error("⚠️ Erro ao parar Redis listener: {}", e.getMessage(), e);
        }
    }
}