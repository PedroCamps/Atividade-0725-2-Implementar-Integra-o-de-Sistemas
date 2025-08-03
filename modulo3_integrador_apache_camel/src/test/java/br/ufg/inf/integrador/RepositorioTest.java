package br.ufg.inf.integrador;

import br.ufg.inf.integrador.model.EstudanteCanonico;
import br.ufg.inf.integrador.model.EstudanteIdMapping;
import br.ufg.inf.integrador.repository.Database;
import br.ufg.inf.integrador.repository.Repositorio;
import org.junit.jupiter.api.*;

import java.io.File;
import java.time.Instant;
import java.util.List;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Testes unitários para o repositório e banco de dados
 */
class RepositorioTest {
    
    private static final String TEST_DB_NAME = "test_integrador.db";
    
    private Database database;
    private Repositorio<EstudanteCanonico, String> estudanteRepo;
    private Repositorio<EstudanteIdMapping, String> mappingRepo;
    
    @BeforeEach
    void setUp() {
        // Remove arquivo de teste se existir
        File testFile = new File(TEST_DB_NAME);
        if (testFile.exists()) {
            testFile.delete();
        }
        
        // Criar banco de teste
        database = new Database(TEST_DB_NAME);
        estudanteRepo = new Repositorio<>(database, EstudanteCanonico.class);
        mappingRepo = new Repositorio<>(database, EstudanteIdMapping.class);
        
        // Desabilitar publicação CRUD para testes
        estudanteRepo.setEnableCrudPublishing(false);
        mappingRepo.setEnableCrudPublishing(false);
    }
    
    @AfterEach
    void tearDown() {
        if (database != null) {
            database.close();
        }
        
        // Remove arquivo de teste
        File testFile = new File(TEST_DB_NAME);
        if (testFile.exists()) {
            testFile.delete();
        }
    }
    
    @Test
    @DisplayName("Deve conectar ao banco de dados com sucesso")
    void testDatabaseConnection() {
        assertTrue(database.isConnected());
        assertEquals(TEST_DB_NAME, database.getDatabaseName());
        assertTrue(database.getDatabaseUrl().contains(TEST_DB_NAME));
    }
    
    @Test
    @DisplayName("Deve criar EstudanteCanonico corretamente")
    void testCreateEstudanteCanonico() {
        String idCanonico = UUID.randomUUID().toString();
        
        EstudanteCanonico estudante = new EstudanteCanonico(
            idCanonico,
            "João",
            "Silva",
            "João Silva",
            "01/01/2000",
            "123456",
            "ATIVO",
            "QUITADO"
        );
        
        EstudanteCanonico created = estudanteRepo.create(estudante);
        
        assertNotNull(created);
        assertEquals(idCanonico, created.getIdCanonico());
        assertEquals("João", created.getPrenome());
        assertEquals("Silva", created.getSobrenome());
        assertEquals("João Silva", created.getNomeCompleto());
    }
    
    @Test
    @DisplayName("Deve carregar EstudanteCanonico por ID")
    void testLoadEstudanteCanonicoById() {
        String idCanonico = UUID.randomUUID().toString();
        
        EstudanteCanonico estudante = new EstudanteCanonico(
            idCanonico,
            "Maria",
            "Santos",
            "Maria Santos",
            "15/03/1999",
            "234567",
            "ATIVO",
            "QUITADO"
        );
        
        estudanteRepo.create(estudante);
        
        EstudanteCanonico loaded = estudanteRepo.loadFromId(idCanonico);
        
        assertNotNull(loaded);
        assertEquals(idCanonico, loaded.getIdCanonico());
        assertEquals("Maria", loaded.getPrenome());
        assertEquals("Santos", loaded.getSobrenome());
    }
    
    @Test
    @DisplayName("Deve listar todos os estudantes canônicos")
    void testLoadAllEstudantesCanonicos() {
        // Criar alguns estudantes
        for (int i = 1; i <= 3; i++) {
            String id = UUID.randomUUID().toString();
            EstudanteCanonico estudante = new EstudanteCanonico(
                id,
                "Estudante" + i,
                "Teste",
                "Estudante" + i + " Teste",
                "01/01/200" + i,
                "12345" + i,
                "ATIVO",
                "QUITADO"
            );
            estudanteRepo.create(estudante);
        }
        
        List<EstudanteCanonico> todos = estudanteRepo.loadAll();
        
        assertEquals(3, todos.size());
    }
    
    @Test
    @DisplayName("Deve atualizar EstudanteCanonico existente")
    void testUpdateEstudanteCanonico() {
        String idCanonico = UUID.randomUUID().toString();
        
        EstudanteCanonico estudante = new EstudanteCanonico(
            idCanonico,
            "Pedro",
            "Oliveira",
            "Pedro Oliveira",
            "22/08/2001",
            "345678",
            "ATIVO",
            "QUITADO"
        );
        
        estudanteRepo.create(estudante);
        
        // Atualizar status
        estudante.setStatusBiblioteca("EM_ABERTO");
        estudanteRepo.update(estudante);
        
        EstudanteCanonico updated = estudanteRepo.loadFromId(idCanonico);
        assertEquals("EM_ABERTO", updated.getStatusBiblioteca());
    }
    
    @Test
    @DisplayName("Deve remover EstudanteCanonico")
    void testDeleteEstudanteCanonico() {
        String idCanonico = UUID.randomUUID().toString();
        
        EstudanteCanonico estudante = new EstudanteCanonico(
            idCanonico,
            "Ana",
            "Costa",
            "Ana Costa",
            "10/05/1998",
            "456789",
            "ATIVO",
            "QUITADO"
        );
        
        estudanteRepo.create(estudante);
        estudanteRepo.delete(estudante);
        
        EstudanteCanonico deleted = estudanteRepo.loadFromId(idCanonico);
        assertNull(deleted);
    }
    
    @Test
    @DisplayName("Deve criar mapeamento de IDs corretamente")
    void testCreateEstudanteIdMapping() {
        String idCanonico = UUID.randomUUID().toString();
        
        EstudanteIdMapping mapping = new EstudanteIdMapping(
            idCanonico,
            "123", // ID SGA
            "507f1f77bcf86cd799439011", // ID SB (MongoDB ObjectId)
            Instant.now().toString()
        );
        
        EstudanteIdMapping created = mappingRepo.create(mapping);
        
        assertNotNull(created);
        assertEquals(idCanonico, created.getIdCanonico());
        assertEquals("123", created.getIdSGA());
        assertEquals("507f1f77bcf86cd799439011", created.getIdSB());
        assertTrue(created.isComplete());
    }
    
    @Test
    @DisplayName("Deve verificar se mapeamento está completo")
    void testMappingComplete() {
        String idCanonico = UUID.randomUUID().toString();
        
        // Mapeamento completo
        EstudanteIdMapping completo = new EstudanteIdMapping(
            idCanonico,
            "123",
            "507f1f77bcf86cd799439011",
            Instant.now().toString()
        );
        assertTrue(completo.isComplete());
        assertFalse(completo.isForCreation());
        
        // Mapeamento para criação (só SGA)
        EstudanteIdMapping paraCriacao = new EstudanteIdMapping(
            idCanonico,
            "123",
            null,
            Instant.now().toString()
        );
        assertFalse(paraCriacao.isComplete());
        assertTrue(paraCriacao.isForCreation());
    }
    
    @Test
    @DisplayName("Deve contar entidades corretamente")
    void testCount() {
        assertEquals(0, estudanteRepo.count());
        
        // Criar algumas entidades
        for (int i = 1; i <= 5; i++) {
            String id = UUID.randomUUID().toString();
            EstudanteCanonico estudante = new EstudanteCanonico(
                id, "Nome" + i, "Sobrenome" + i, "Nome" + i + " Sobrenome" + i,
                "01/01/200" + i, "1234" + i, "ATIVO", "QUITADO"
            );
            estudanteRepo.create(estudante);
        }
        
        assertEquals(5, estudanteRepo.count());
    }
    
    @Test
    @DisplayName("Deve verificar existência de entidade")
    void testExists() {
        String idCanonico = UUID.randomUUID().toString();
        
        assertFalse(estudanteRepo.exists(idCanonico));
        
        EstudanteCanonico estudante = new EstudanteCanonico(
            idCanonico, "Teste", "Existe", "Teste Existe",
            "01/01/2000", "999999", "ATIVO", "QUITADO"
        );
        estudanteRepo.create(estudante);
        
        assertTrue(estudanteRepo.exists(idCanonico));
    }
    
    @Test
    @DisplayName("Deve remover entidade por ID")
    void testDeleteById() {
        String idCanonico = UUID.randomUUID().toString();
        
        EstudanteCanonico estudante = new EstudanteCanonico(
            idCanonico, "Deletar", "PorId", "Deletar PorId",
            "01/01/2000", "888888", "ATIVO", "QUITADO"
        );
        estudanteRepo.create(estudante);
        
        assertTrue(estudanteRepo.exists(idCanonico));
        
        estudanteRepo.deleteById(idCanonico);
        
        assertFalse(estudanteRepo.exists(idCanonico));
    }
}