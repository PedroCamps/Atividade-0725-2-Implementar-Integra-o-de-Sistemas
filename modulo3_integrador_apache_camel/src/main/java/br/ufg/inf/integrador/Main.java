package br.ufg.inf.integrador;

import br.ufg.inf.integrador.redis.RedisListener;
import br.ufg.inf.integrador.routes.CrudTransformRoute;
import org.apache.camel.CamelContext;
import org.apache.camel.impl.DefaultCamelContext;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Classe principal do Sistema Integrador usando Apache Camel
 * 
 * Este integrador implementa os Enterprise Integration Patterns:
 * - Publisher-Subscriber Channel (Redis)
 * - Message Router (Camel Routes) 
 * - Message Translator (Processors)
 * - Canonical Data Model (EstudanteCanonico)
 */
public class Main {
    
    private static final Logger logger = LoggerFactory.getLogger(Main.class);
    
    public static void main(String[] args) throws Exception {
        logger.info("🚀 Sistema Integrador Apache Camel");
        logger.info("🔧 Baseado nos padrões Enterprise Integration Patterns");
        
        try {
            // Criar contexto do Camel
            CamelContext context = new DefaultCamelContext();
            
            // Adicionar rotas de transformação
            context.addRoutes(new CrudTransformRoute());
            
            // Iniciar contexto do Camel
            context.start();
            logger.info("✅ Contexto Apache Camel iniciado");
            
            // Iniciar listener Redis que alimenta o Camel
            logger.info("📡 Conectando ao Redis...");
            RedisListener redisListener = new RedisListener(context.createProducerTemplate());
            redisListener.start();
            
            logger.info("✅ Integrador iniciado com sucesso!");
            logger.info("🔄 Aguardando eventos CRUD do Redis...");
            logger.info("📖 Para parar, pressione Ctrl+C");
            
            // Manter aplicação viva
            Thread.currentThread().join();
            
        } catch (Exception e) {
            logger.error("❌ Erro ao iniciar integrador: {}", e.getMessage(), e);
            throw e;
        }
    }
}