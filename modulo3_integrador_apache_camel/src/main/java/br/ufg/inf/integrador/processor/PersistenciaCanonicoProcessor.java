package br.ufg.inf.integrador.processor;

import br.ufg.inf.integrador.model.CrudOperation;
import br.ufg.inf.integrador.model.EstudanteCanonico;
import br.ufg.inf.integrador.model.EstudanteIdMapping;
import br.ufg.inf.integrador.repository.Database;
import br.ufg.inf.integrador.repository.Repositorio;
import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import org.apache.camel.Exchange;
import org.apache.camel.Processor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Instant;
import java.util.UUID;

/**
 * Processador responsável pela persistência de dados canônicos e mapeamento de IDs
 * 
 * Implementa o padrão Canonical Data Model:
 * - Persiste dados no formato canônico (EstudanteCanonico)
 * - Mantém mapeamento de IDs entre sistemas (EstudanteIdMapping)
 * - Garante rastreabilidade e idempotência das operações
 * 
 * Este processador é executado APÓS o envio HTTP bem-sucedido,
 * garantindo que os dados foram aceitos pelo sistema de destino.
 */
public class PersistenciaCanonicoProcessor implements Processor {
    
    private static final Logger logger = LoggerFactory.getLogger(PersistenciaCanonicoProcessor.class);
    private final Gson gson = new Gson();
    private final EstudanteProcessor estudanteProcessor = new EstudanteProcessor();
    
    // Repositórios para persistência canônica
    private final Repositorio<EstudanteCanonico, String> estudanteRepo;
    private final Repositorio<EstudanteIdMapping, String> mappingRepo;
    
    public PersistenciaCanonicoProcessor() {
        // Inicializar banco de dados do integrador
        Database db = new Database("integrador.db");
        
        // Criar repositórios com publicação CRUD desabilitada para evitar loops
        this.estudanteRepo = new Repositorio<>(db, EstudanteCanonico.class);
        this.estudanteRepo.setEnableCrudPublishing(false);
        
        this.mappingRepo = new Repositorio<>(db, EstudanteIdMapping.class);
        this.mappingRepo.setEnableCrudPublishing(false);
        
        logger.info("💾 Repositórios canônicos inicializados");
    }
    
    @Override
    public void process(Exchange exchange) throws Exception {
        try {
            // Verificar se deve processar (apenas Estudante/CREATE)
            String entidade = (String) exchange.getProperty("crudEntity");
            String operacao = (String) exchange.getProperty("crudOperation");
            
            if (!"estudante".equalsIgnoreCase(entidade) || !"CREATE".equals(operacao)) {
                logger.debug("⏭️ Pulando persistência canônica para {}/{}", entidade, operacao);
                return;
            }
            
            logger.info("💾 Iniciando persistência canônica para Estudante/CREATE");
            
            // Extrair dados da resposta HTTP (do SB)
            String respostaHttp = exchange.getMessage().getBody(String.class);
            JsonObject jsonResposta = JsonParser.parseString(respostaHttp).getAsJsonObject();
            String idSB = jsonResposta.has("id") ? jsonResposta.get("id").getAsString() : null;
            
            if (idSB == null) {
                logger.warn("⚠️ ID do SB não encontrado na resposta HTTP");
                return;
            }
            
            // Extrair dados da operação original (do SGA)
            CrudOperation operacaoOriginal = (CrudOperation) exchange.getProperty("CrudOriginal");
            String dadosOriginais = operacaoOriginal.getData();
            
            JsonObject jsonOriginal = JsonParser.parseString(dadosOriginais).getAsJsonObject();
            String idSGA = jsonOriginal.has("id") ? jsonOriginal.get("id").getAsString() : null;
            
            if (idSGA == null) {
                logger.warn("⚠️ ID do SGA não encontrado nos dados originais");
                return;
            }
            
            // Gerar ID canônico único
            String idCanonico = UUID.randomUUID().toString();
            
            logger.info("🔗 Correlacionando IDs: Canônico={}, SGA={}, SB={}", 
                       idCanonico, idSGA, idSB);
            
            // Criar e persistir EstudanteCanonico
            EstudanteCanonico estudanteCanonico = estudanteProcessor.estudanteParaEstudanteCanonico(
                dadosOriginais, idCanonico
            );
            
            if (estudanteCanonico == null) {
                logger.error("❌ Falha ao criar EstudanteCanonico");
                return;
            }
            
            estudanteRepo.create(estudanteCanonico);
            logger.info("✅ EstudanteCanonico persistido: {}", estudanteCanonico.getIdCanonico());
            
            // Criar e persistir mapeamento de IDs
            EstudanteIdMapping mapeamento = new EstudanteIdMapping();
            mapeamento.setIdCanonico(idCanonico);
            mapeamento.setIdSGA(idSGA);
            mapeamento.setIdSB(idSB);
            mapeamento.setUltimaAtualizacao(Instant.now().toString());
            
            mappingRepo.create(mapeamento);
            logger.info("✅ Mapeamento de IDs persistido: {}", mapeamento);
            
            // Log resumo da operação
            logger.info("🎉 Persistência canônica concluída com sucesso:");
            logger.info("   🏛️ Modelo canônico: {}", estudanteCanonico.getNomeCompleto());
            logger.info("   🔗 Correlação: SGA({}) ↔ Canônico({}) ↔ SB({})", 
                       idSGA, idCanonico, idSB);
            
        } catch (Exception e) {
            logger.error("❌ Erro na persistência canônica: {}", e.getMessage(), e);
            // Não propagar erro para não quebrar o fluxo principal
            // A integração principal já foi bem-sucedida
        }
    }
    
    /**
     * Cleanup de recursos (chamado na finalização da aplicação)
     */
    public void cleanup() {
        try {
            if (estudanteRepo != null) {
                estudanteRepo.getDatabase().close();
            }
            logger.info("🧹 Recursos de persistência canônica liberados");
        } catch (Exception e) {
            logger.warn("⚠️ Erro ao liberar recursos: {}", e.getMessage());
        }
    }
}