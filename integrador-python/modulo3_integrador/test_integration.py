import unittest
import json
import time
from unittest.mock import Mock, patch
from application.processors import CrudProcessor, EstudanteProcessor, HttpProcessor
from application.integration_router import IntegrationRouter


class TestEstudanteProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = EstudanteProcessor()
    
    def test_extrair_prenome_e_sobrenome(self):
        """Testa a extração de prenome e sobrenome"""
        prenome, sobrenome = self.processor.extrair_prenome_e_sobrenome("João da Silva")
        self.assertEqual("João", prenome)
        self.assertEqual("da Silva", sobrenome)
        
        prenome, sobrenome = self.processor.extrair_prenome_e_sobrenome("Maria")
        self.assertEqual("Maria", prenome)
        self.assertEqual("", sobrenome)
    
    def test_estudante_para_usuario(self):
        """Testa a transformação de Estudante para Usuario"""
        dados_estudante = {
            "id": 1,
            "nome_completo": "Pedro Santos",
            "data_de_nascimento": "01/01/1995",
            "matricula": 123456
        }
        
        resultado = self.processor.estudante_para_usuario(json.dumps(dados_estudante))
        usuario = json.loads(resultado)
        
        self.assertEqual("Pedro", usuario["prenome"])
        self.assertEqual("Santos", usuario["sobrenome"])
        self.assertEqual("ATIVO", usuario["situacao_matricula"])
    
    def test_estudante_para_estudante_canonico(self):
        """Testa a criação do modelo canônico"""
        dados_estudante = {
            "id": 1,
            "nome_completo": "Ana Costa",
            "data_de_nascimento": "15/03/1990",
            "matricula": 654321,
            "status_emprestimo_livros": "QUITADO"
        }
        
        canonico = self.processor.estudante_para_estudante_canonico(
            json.dumps(dados_estudante)
        )
        
        self.assertIsNotNone(canonico)
        self.assertEqual("Ana", canonico.prenome)
        self.assertEqual("Costa", canonico.sobrenome)
        self.assertEqual("Ana Costa", canonico.nome_completo)
        self.assertEqual("654321", canonico.matricula)


class TestCrudProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = CrudProcessor()
    
    def test_process_create_estudante(self):
        """Testa o processamento de CREATE de Estudante"""
        message_data = {
            "entity": "Estudante",
            "operation": "CREATE",
            "source": "ORM",
            "data": '{"id": 1, "nome_completo": "João Silva", "matricula": 123456}',
            "timestamp": "2024-01-01T10:00:00"
        }
        
        result = self.processor.process(json.dumps(message_data))
        
        self.assertIsNotNone(result)
        self.assertEqual("POST", result["http_method"])
        self.assertEqual("http://localhost:8080/usuarios", result["target_endpoint"])
        self.assertIn("prenome", result["body"])
    
    def test_process_unsupported_operation(self):
        """Testa operação não suportada"""
        message_data = {
            "entity": "Estudante",
            "operation": "UPDATE",
            "source": "ORM",
            "data": '{"id": 1}',
            "timestamp": "2024-01-01T10:00:00"
        }
        
        result = self.processor.process(json.dumps(message_data))
        self.assertIsNone(result)


class TestHttpProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = HttpProcessor()
    
    @patch('requests.post')
    def test_send_post_request(self, mock_post):
        """Testa envio de requisição POST"""
        # Mock da resposta
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.text = '{"id": "507f1f77bcf86cd799439011"}'
        mock_post.return_value = mock_response
        
        request_data = {
            "http_method": "POST",
            "target_endpoint": "http://localhost:8080/usuarios",
            "headers": {"Content-Type": "application/json"},
            "body": '{"prenome": "João", "sobrenome": "Silva"}'
        }
        
        response = self.processor.send_request(request_data)
        
        self.assertIsNotNone(response)
        self.assertIn("507f1f77bcf86cd799439011", response)
        mock_post.assert_called_once()


class TestIntegrationRouter(unittest.TestCase):
    def setUp(self):
        self.router = IntegrationRouter()
    
    @patch('requests.post')
    def test_route_message_complete_flow(self, mock_post):
        """Testa o fluxo completo de roteamento de mensagem"""
        # Mock da resposta HTTP
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.text = '{"id": "507f1f77bcf86cd799439011", "prenome": "João", "sobrenome": "Silva"}'
        mock_post.return_value = mock_response
        
        # Mensagem de teste
        message = json.dumps({
            "entity": "Estudante",
            "operation": "CREATE",
            "source": "ORM",
            "data": '{"id": 1, "nome_completo": "João Silva", "matricula": 123456}',
            "timestamp": "2024-01-01T10:00:00"
        })
        
        # Executa o roteamento
        self.router.route_message("crud-channel", message)
        
        # Verifica se a requisição HTTP foi chamada
        mock_post.assert_called_once()
        
        # Verifica os argumentos da chamada
        call_args = mock_post.call_args
        self.assertEqual("http://localhost:8080/usuarios", call_args[1]['url'])
        self.assertIn('{"prenome": "João", "sobrenome": "Silva"', call_args[1]['data'])


if __name__ == '__main__':
    # Executa os testes
    unittest.main()