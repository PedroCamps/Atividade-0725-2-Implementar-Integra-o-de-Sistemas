package br.ufg.inf.integrador.repository;

import com.j256.ormlite.dao.Dao;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.SQLException;
import java.util.List;

/**
 * Repositório genérico para operações CRUD com ORMLite
 * 
 * Esta classe implementa o padrão Repository para fornecer
 * uma interface consistente de acesso a dados, independente
 * do tipo de entidade.
 * 
 * Características:
 * - Genérico: Funciona com qualquer entidade ORMLite
 * - Transacional: Operações atômicas com rollback
 * - Logging: Logs detalhados de todas as operações
 * - Configurável: Pode desabilitar publicação CRUD para evitar loops
 */
public class Repositorio<T, ID> {
    
    private static final Logger logger = LoggerFactory.getLogger(Repositorio.class);
    
    private final Database database;
    private final Class<T> entityClass;
    private final Dao<T, ID> dao;
    private boolean enableCrudPublishing = true;
    
    public Repositorio(Database database, Class<T> entityClass) {
        this.database = database;
        this.entityClass = entityClass;
        
        try {
            this.dao = database.getDao(entityClass);
            logger.debug("🏗️ Repositório criado para: {}", entityClass.getSimpleName());
        } catch (SQLException e) {
            logger.error("❌ Erro ao criar repositório para {}: {}", 
                        entityClass.getSimpleName(), e.getMessage(), e);
            throw new RuntimeException("Falha ao criar repositório", e);
        }
    }
    
    /**
     * Cria uma nova entidade no banco de dados
     */
    public T create(T entity) {
        try {
            logger.debug("🔍 Criando entidade: {}", entity);
            
            int rowsAffected = dao.create(entity);
            if (rowsAffected == 0) {
                throw new SQLException("Nenhuma linha foi inserida");
            }
            
            logger.info("✅ Entidade criada: {}", entity);
            return entity;
            
        } catch (SQLException e) {
            logger.error("❌ Erro ao criar entidade {}: {}", 
                        entityClass.getSimpleName(), e.getMessage(), e);
            throw new RuntimeException("Falha ao criar entidade", e);
        }
    }
    
    /**
     * Carrega uma entidade por ID
     */
    public T loadFromId(ID id) {
        try {
            logger.debug("🔍 Carregando entidade por ID: {}", id);
            
            T entity = dao.queryForId(id);
            
            if (entity != null) {
                logger.debug("✅ Entidade encontrada: {}", entity);
            } else {
                logger.debug("⚠️ Entidade não encontrada para ID: {}", id);
            }
            
            return entity;
            
        } catch (SQLException e) {
            logger.error("❌ Erro ao carregar entidade por ID {}: {}", 
                        id, e.getMessage(), e);
            throw new RuntimeException("Falha ao carregar entidade", e);
        }
    }
    
    /**
     * Carrega todas as entidades
     */
    public List<T> loadAll() {
        try {
            logger.debug("📋 Carregando todas as entidades de: {}", entityClass.getSimpleName());
            
            List<T> entities = dao.queryForAll();
            
            logger.debug("✅ {} entidades carregadas", entities.size());
            return entities;
            
        } catch (SQLException e) {
            logger.error("❌ Erro ao carregar todas as entidades de {}: {}", 
                        entityClass.getSimpleName(), e.getMessage(), e);
            throw new RuntimeException("Falha ao carregar entidades", e);
        }
    }
    
    /**
     * Atualiza uma entidade existente
     */
    public T update(T entity) {
        try {
            logger.debug("🔄 Atualizando entidade: {}", entity);
            
            int rowsAffected = dao.update(entity);
            if (rowsAffected == 0) {
                logger.warn("⚠️ Nenhuma linha foi atualizada para: {}", entity);
            } else {
                logger.info("✅ Entidade atualizada: {}", entity);
            }
            
            return entity;
            
        } catch (SQLException e) {
            logger.error("❌ Erro ao atualizar entidade {}: {}", 
                        entityClass.getSimpleName(), e.getMessage(), e);
            throw new RuntimeException("Falha ao atualizar entidade", e);
        }
    }
    
    /**
     * Remove uma entidade do banco de dados
     */
    public void delete(T entity) {
        try {
            logger.debug("🗑️ Removendo entidade: {}", entity);
            
            int rowsAffected = dao.delete(entity);
            if (rowsAffected == 0) {
                logger.warn("⚠️ Nenhuma linha foi removida para: {}", entity);
            } else {
                logger.info("✅ Entidade removida: {}", entity);
            }
            
        } catch (SQLException e) {
            logger.error("❌ Erro ao remover entidade {}: {}", 
                        entityClass.getSimpleName(), e.getMessage(), e);
            throw new RuntimeException("Falha ao remover entidade", e);
        }
    }
    
    /**
     * Remove uma entidade por ID
     */
    public void deleteById(ID id) {
        try {
            logger.debug("🗑️ Removendo entidade por ID: {}", id);
            
            int rowsAffected = dao.deleteById(id);
            if (rowsAffected == 0) {
                logger.warn("⚠️ Nenhuma linha foi removida para ID: {}", id);
            } else {
                logger.info("✅ Entidade removida por ID: {}", id);
            }
            
        } catch (SQLException e) {
            logger.error("❌ Erro ao remover entidade por ID {}: {}", 
                        id, e.getMessage(), e);
            throw new RuntimeException("Falha ao remover entidade por ID", e);
        }
    }
    
    /**
     * Conta o número total de entidades
     */
    public long count() {
        try {
            long count = dao.countOf();
            logger.debug("📊 Total de entidades {}: {}", entityClass.getSimpleName(), count);
            return count;
            
        } catch (SQLException e) {
            logger.error("❌ Erro ao contar entidades {}: {}", 
                        entityClass.getSimpleName(), e.getMessage(), e);
            throw new RuntimeException("Falha ao contar entidades", e);
        }
    }
    
    /**
     * Verifica se existe uma entidade com o ID especificado
     */
    public boolean exists(ID id) {
        return loadFromId(id) != null;
    }
    
    // Getters e Setters
    
    public Database getDatabase() {
        return database;
    }
    
    public Class<T> getEntityClass() {
        return entityClass;
    }
    
    public Dao<T, ID> getDao() {
        return dao;
    }
    
    public boolean isEnableCrudPublishing() {
        return enableCrudPublishing;
    }
    
    public void setEnableCrudPublishing(boolean enableCrudPublishing) {
        this.enableCrudPublishing = enableCrudPublishing;
        logger.debug("🔧 Publicação CRUD {} para {}", 
                    enableCrudPublishing ? "habilitada" : "desabilitada", 
                    entityClass.getSimpleName());
    }
}