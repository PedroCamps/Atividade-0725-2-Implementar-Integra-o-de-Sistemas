from pymongo import MongoClient
from typing import Optional
import os


class MongoDB:
    def __init__(self, connection_string: str = None, database_name: str = "biblioteca"):
        if connection_string is None:
            connection_string = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        
        self.client = MongoClient(connection_string)
        self.database = self.client[database_name]
        
        # Cria índices se necessário
        self._create_indexes()
    
    def _create_indexes(self):
        """Cria índices para melhor performance"""
        try:
            # Índice único para código do empréstimo
            self.database.registros_emprestimo.create_index("codigo_emprestimo", unique=True)
            # Índice único para ISBN da obra
            self.database.obras.create_index("isbn", unique=True)
        except Exception as e:
            print(f"⚠️ Aviso ao criar índices: {e}")
    
    def get_collection(self, collection_name: str):
        """Retorna uma coleção específica"""
        return self.database[collection_name]
    
    def close(self):
        """Fecha a conexão com o MongoDB"""
        self.client.close()
    
    def ping(self) -> bool:
        """Verifica se a conexão está funcionando"""
        try:
            self.client.admin.command('ping')
            return True
        except Exception:
            return False