from typing import Dict, Any, Optional
from .processors import CrudProcessor, HttpProcessor, PersistenciaCanonicoProcessor


class IntegrationRouter:
    """
    Roteador principal que implementa os padrões de integração:
    - Message Router: direciona mensagens para processadores corretos
    - Message Translator: transforma dados entre formatos
    - Canonical Data Model: mantém modelo canônico
    """
    
    def __init__(self):
        self.crud_processor = CrudProcessor()
        self.http_processor = HttpProcessor()
        self.persistencia_processor = PersistenciaCanonicoProcessor()
    
    def route_message(self, channel: str, message: str) -> None:
        """
        Rota principal que processa mensagens do Redis
        Implementa o padrão Message Router
        """
        try:
            print(f"📥 Mensagem recebida do canal {channel}")
            
            # 1. Processa a mensagem CRUD (Message Translator)
            request_data = self.crud_processor.process(message)
            
            if not request_data:
                print("⚠️ Mensagem ignorada pelo processador")
                return
            
            print(f"✅ JSON processado: {request_data['body']}")
            
            # 2. Envia requisição HTTP para sistema de destino
            response = self.http_processor.send_request(request_data)
            
            if response:
                # 3. Persiste dados canônicos e mapeamento (apenas para Estudante/CREATE)
                self.persistencia_processor.process(request_data, response)
            
        except Exception as e:
            print(f"❌ Erro no roteamento da mensagem: {e}")
    
    def close(self):
        """Fecha recursos utilizados pelos processadores"""
        if hasattr(self.persistencia_processor, 'db'):
            self.persistencia_processor.db.close()