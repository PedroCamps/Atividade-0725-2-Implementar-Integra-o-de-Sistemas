import unittest
import os
from infrastructure.models import Database
from application.repository import EstudanteRepository
from domain.entities import Estudante, StatusEmprestimo


class TestEstudanteRepository(unittest.TestCase):
    def setUp(self):
        self.test_db_name = "test_sga.db"
        # Remove arquivo de teste se existir
        if os.path.exists(self.test_db_name):
            os.remove(self.test_db_name)
        
        self.db = Database(self.test_db_name)
        self.repo = EstudanteRepository(self.db, enable_crud_publishing=True)
    
    def tearDown(self):
        self.db.close()
        # Remove arquivo de teste
        if os.path.exists(self.test_db_name):
            os.remove(self.test_db_name)
    
    def test_create_estudante(self):
        """Testa a criação de um estudante"""
        estudante = Estudante(
            nome_completo="Teste Silva",
            data_de_nascimento="01/01/2000",
            matricula=123456
        )
        
        created = self.repo.create(estudante)
        
        self.assertIsNotNone(created)
        self.assertIsNotNone(created.id)
        self.assertEqual("Teste Silva", created.nome_completo)
    
    def test_load_from_id(self):
        """Testa o carregamento de estudante por ID"""
        estudante = Estudante(
            nome_completo="Teste Load",
            data_de_nascimento="01/01/2000",
            matricula=654321
        )
        
        created = self.repo.create(estudante)
        loaded = self.repo.load_from_id(created.id)
        
        self.assertIsNotNone(loaded)
        self.assertEqual(created.id, loaded.id)
        self.assertEqual("Teste Load", loaded.nome_completo)
    
    def test_load_all(self):
        """Testa o carregamento de todos os estudantes"""
        # Cria alguns estudantes
        for i in range(3):
            estudante = Estudante(
                nome_completo=f"Estudante {i+1}",
                data_de_nascimento="01/01/2000",
                matricula=100000 + i
            )
            self.repo.create(estudante)
        
        estudantes = self.repo.load_all()
        self.assertEqual(3, len(estudantes))
    
    def test_update(self):
        """Testa a atualização de um estudante"""
        estudante = Estudante(
            nome_completo="Nome Original",
            data_de_nascimento="01/01/2000",
            matricula=999999
        )
        
        created = self.repo.create(estudante)
        created.nome_completo = "Nome Atualizado"
        self.repo.update(created)
        
        loaded = self.repo.load_from_id(created.id)
        self.assertEqual("Nome Atualizado", loaded.nome_completo)
    
    def test_delete(self):
        """Testa a exclusão de um estudante"""
        estudante = Estudante(
            nome_completo="Para Deletar",
            data_de_nascimento="01/01/2000",
            matricula=888888
        )
        
        created = self.repo.create(estudante)
        entity_id = created.id
        
        self.repo.delete(created)
        
        loaded = self.repo.load_from_id(entity_id)
        self.assertIsNone(loaded)


if __name__ == '__main__':
    unittest.main()