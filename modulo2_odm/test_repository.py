import unittest
from infrastructure.database import MongoDB
from application.repository import UsuarioRepository
from domain.entities import Usuario


class TestUsuarioRepository(unittest.TestCase):
    def setUp(self):
        # Usa uma base de dados de teste
        self.mongodb = MongoDB(database_name="biblioteca_test")
        self.repo = UsuarioRepository(self.mongodb, enable_crud_publishing=True)
        
        # Limpa a coleção de teste
        self.mongodb.get_collection("usuarios").delete_many({})
    
    def tearDown(self):
        # Limpa a coleção de teste
        self.mongodb.get_collection("usuarios").delete_many({})
        self.mongodb.close()
    
    def test_create_usuario(self):
        """Testa a criação de um usuário"""
        usuario = Usuario(
            prenome="João",
            sobrenome="Silva",
            situacao_matricula="ATIVO"
        )
        
        created = self.repo.create(usuario)
        
        self.assertIsNotNone(created)
        self.assertIsNotNone(created.id)
        self.assertEqual("João", created.prenome)
        self.assertEqual("Silva", created.sobrenome)
    
    def test_find_by_id(self):
        """Testa a busca de usuário por ID"""
        usuario = Usuario(
            prenome="Maria",
            sobrenome="Santos",
            situacao_matricula="ATIVO"
        )
        
        created = self.repo.create(usuario)
        found = self.repo.find_by_id(created.id)
        
        self.assertIsNotNone(found)
        self.assertEqual(created.id, found.id)
        self.assertEqual("Maria", found.prenome)
    
    def test_find_all(self):
        """Testa a busca de todos os usuários"""
        # Cria alguns usuários
        for i in range(3):
            usuario = Usuario(
                prenome=f"Usuario{i+1}",
                sobrenome="Teste",
                situacao_matricula="ATIVO"
            )
            self.repo.create(usuario)
        
        usuarios = self.repo.find_all()
        self.assertEqual(3, len(usuarios))
    
    def test_update(self):
        """Testa a atualização de um usuário"""
        usuario = Usuario(
            prenome="Pedro",
            sobrenome="Oliveira",
            situacao_matricula="ATIVO"
        )
        
        created = self.repo.create(usuario)
        created.prenome = "Pedro Henrique"
        self.repo.update(created)
        
        found = self.repo.find_by_id(created.id)
        self.assertEqual("Pedro Henrique", found.prenome)
    
    def test_delete(self):
        """Testa a exclusão de um usuário"""
        usuario = Usuario(
            prenome="Ana",
            sobrenome="Costa",
            situacao_matricula="ATIVO"
        )
        
        created = self.repo.create(usuario)
        user_id = created.id
        
        self.repo.delete(created)
        
        found = self.repo.find_by_id(user_id)
        self.assertIsNone(found)


if __name__ == '__main__':
    unittest.main()