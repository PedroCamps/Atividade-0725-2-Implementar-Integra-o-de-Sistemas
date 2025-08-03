package br.ufg.inf.integrador.repository;

import com.j256.ormlite.dao.Dao;
import com.j256.ormlite.dao.DaoManager;
import com.j256.ormlite.jdbc.JdbcConnectionSource;
import com.j256.ormlite.support.ConnectionSource;
import com.j256.ormlite.table.TableUtils;
import br.ufg.inf.integrador.model.EstudanteCanonico;
import br.ufg.inf.integrador.model.EstudanteIdMapping;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.SQLException;

/**
 * Classe de acesso ao banco de dados SQLite do integrador
 * 
 * Responsabilidades:
 * - Gerenciar conexão com SQLite
 * - Criar tabelas automaticamente
 * - Fornecer DAOs para acesso aos dados
 * - Cleanup de recursos
 * 
 * Este banco é usado para persistir:
 * - Dados canônicos (EstudanteCanonico)
 * - Mapeamento de IDs entre sistemas (EstudanteIdMapping)
 */
public class Database {
    
    private static final Logger logger = LoggerFactory.getLogger(Database.class);
    private static final String DATABASE_URL_PREFIX = "jdbc:sqlite:";
    
    private final String databaseName;
    private final String databaseUrl;
    private ConnectionSource connectionSource;
    
    public Database(String databaseName) {
        this.databaseName = databaseName;
        this.databaseUrl = DATABASE_URL_PREFIX + databaseName;
        
        try {
            initializeDatabase();
            logger.info("✅ Banco de dados inicializado: {}", databaseName);
        } catch (SQLException e) {
            logger.error("❌ Erro ao inicializar banco de dados: {}", e.getMessage(), e);
            throw new RuntimeException("Falha na inicialização do banco de dados", e);
        }
    }
    
    /**
     * Inicializa a conexão com o banco de dados e cria as tabelas
     */
    private void initializeDatabase() throws SQLException {
        // Criar conexão
        connectionSource = new JdbcConnectionSource(databaseUrl);
        
        // Criar tabelas se não existirem
        createTablesIfNotExists();
        
        logger.debug("🔗 Conexão estabelecida com: {}", databaseUrl);
    }
    
    /**
     * Cria as tabelas necessárias se elas não existirem
     */
    private void createTablesIfNotExists() throws SQLException {
        try {
            // Criar tabela EstudanteCanonico
            TableUtils.createTableIfNotExists(connectionSource, EstudanteCanonico.class);
            logger.debug("📋 Tabela EstudanteCanonico verificada/criada");
            
            // Criar tabela EstudanteIdMapping
            TableUtils.createTableIfNotExists(connectionSource, EstudanteIdMapping.class);
            logger.debug("📋 Tabela EstudanteIdMapping verificada/criada");
            
        } catch (SQLException e) {
            logger.error("❌ Erro ao criar tabelas: {}", e.getMessage(), e);
            throw e;
        }
    }
    
    /**
     * Obtém um DAO para a classe especificada
     */
    public <T, ID> Dao<T, ID> getDao(Class<T> clazz) throws SQLException {
        return DaoManager.createDao(connectionSource, clazz);
    }
    
    /**
     * Obtém a fonte de conexão (para uso em repositórios)
     */
    public ConnectionSource getConnectionSource() {
        return connectionSource;
    }
    
    /**
     * Obtém o nome do banco de dados
     */
    public String getDatabaseName() {
        return databaseName;
    }
    
    /**
     * Obtém a URL completa do banco de dados
     */
    public String getDatabaseUrl() {
        return databaseUrl;
    }
    
    /**
     * Verifica se a conexão está ativa
     */
    public boolean isConnected() {
        try {
            return connectionSource != null && connectionSource.isOpen("");
        } catch (SQLException e) {
            logger.debug("Erro ao verificar conexão: {}", e.getMessage());
            return false;
        }
    }
    
    /**
     * Fecha a conexão com o banco de dados
     */
    public void close() {
        if (connectionSource != null) {
            try {
                connectionSource.close();
                logger.info("🔐 Conexão com banco de dados fechada: {}", databaseName);
            } catch (Exception e) {
                logger.warn("⚠️ Erro ao fechar conexão: {}", e.getMessage());
            }
        }
    }
    
    /**
     * Cleanup automático quando o objeto é coletado pelo GC
     */
    @Override
    protected void finalize() throws Throwable {
        close();
        super.finalize();
    }
}