package br.ufg.inf.integrador.processor;

import br.ufg.inf.integrador.model.CrudOperation;
import com.google.gson.Gson;
import org.apache.camel.Exchange;
import org.apache.camel.Processor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Processador principal de operações CRUD
 * 
 * Implementa o padrão Message Translator:
 * - Analisa operações CRUD recebidas via Redis
 * - Direciona para processadores específicos por entidade
 * - Transforma dados entre formatos de sistemas diferentes
 * - Define se a mensagem deve ser enviada para endpoint HTTP
 */
public class CrudProcessor implements Processor {
    
    private static final Logger logger = LoggerFactory.getLogger(CrudProcessor.class);
    private final Gson gson = new Gson();
    private final EstudanteProcessor estudanteProcessor = new EstudanteProcessor();
    
    @Override
    public void process(Exchange exchange) throws Exception {
        String json = exchange.getIn().getBody(String.class);
        
        try {
            CrudOperation op = gson.fromJson(json, CrudOperation.class);
            logger.debug("🔍 Processando operação CRUD: {}", op);
            
            // Armazena a operação original no Exchange para uso posterior
            exchange.setProperty("CrudOriginal", op);
            
            // Verifica se é uma operação CREATE do ORM (SGA)
            if (op.getOperation() == CrudOperation.OperationType.CREATE && 
                op.getSource() == CrudOperation.Source.ORM) {
                
                logger.info("✅ Operação CREATE do ORM detectada para entidade: {}", op.getEntity());
                
                // Processar baseado no tipo de entidade
                String resultado = processarEntidade(op);
                
                if (resultado != null) {
                    // Definir o corpo da mensagem com os dados transformados
                    exchange.getIn().setBody(resultado);
                    logger.info("🔄 Dados transformados com sucesso");
                } else {
                    // Marcar para pular o envio HTTP
                    exchange.setProperty("CamelSkipSendToEndpoint", true);
                    logger.warn("⚠️ Falha na transformação de dados");
                }
                
            } else {
                // Operação não suportada - pular processamento
                exchange.setProperty("CamelSkipSendToEndpoint", true);
                logger.info("⚠️ Operação ignorada - Tipo: {}, Fonte: {}", 
                           op.getOperation(), op.getSource());
            }
            
        } catch (Exception e) {
            logger.error("❌ Erro ao processar operação CRUD: {}", e.getMessage(), e);
            exchange.setProperty("CamelSkipSendToEndpoint", true);
            throw e;
        }
    }
    
    /**
     * Direciona o processamento de acordo com o tipo de entidade
     * 
     * Este método implementa o padrão Strategy, delegando para
     * processadores específicos baseado no tipo da entidade.
     */
    private String processarEntidade(CrudOperation op) {
        String entidade = op.getEntity();
        
        logger.debug("🎯 Processando entidade: {}", entidade);
        
        switch (entidade.toLowerCase()) {
            case "estudante":
                return estudanteProcessor.estudanteParaUsuario(op.getData());
                
            case "professor":
                // TODO: Implementar processador para Professor
                logger.warn("⚠️ Processador para Professor não implementado");
                return null;
                
            case "disciplina":
                // TODO: Implementar processador para Disciplina  
                logger.warn("⚠️ Processador para Disciplina não implementado");
                return null;
                
            default:
                logger.warn("⚠️ Entidade não suportada: {}", entidade);
                return null;
        }
    }
}