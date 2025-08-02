import json
import uuid
import requests
from datetime import datetime
from typing import Dict, Any, Optional

from ..domain.canonical_model import EstudanteCanonico, EstudanteIdMapping
from ..infrastructure.models import IntegratorDatabase, EstudanteCanonicoModel, EstudanteIdMappingModel


class CrudOperation:
    def __init__(self, data: Dict[str, Any]):
        self.entity = data.get("entity", "")
        self.operation = data.get("operation", "")
        self.source = data.get("source", "")
        self.data = data.get("data", "")
        self.timestamp = data.get("timestamp", "")


class EstudanteProcessor:
    """Processa transformações relacionadas à entidade Estudante"""
    
    def estudante_para_usuario(self, dados_json: str) -> Optional[str]:
        """Transforma dados de Estudante (SGA) para Usuario (SB)"""
        try:
            dados = json.loads(dados_json)
            
            # Extrai nome completo e separa em prenome/sobrenome
            nome_completo = dados.get("nome_completo", "")
            prenome, sobrenome = self.extrair_prenome_e_sobrenome(nome_completo)
            
            # Cria objeto Usuario para SB
            usuario = {
                "prenome": prenome,
                "sobrenome": sobrenome,
                "situacao_matricula": "ATIVO"  # Default para novos usuários
            }
            
            return json.dumps(usuario)
        except Exception as e:
            print(f"❌ Erro ao transformar estudante para usuário: {e}")
            return None
    
    def estudante_para_estudante_canonico(self, dados_json: str, id_canonico: str = None) -> Optional[EstudanteCanonico]:
        """Transforma dados de Estudante para modelo canônico"""
        try:
            dados = json.loads(dados_json)
            
            if not id_canonico:
                id_canonico = str(uuid.uuid4())
            
            nome_completo = dados.get("nome_completo", "")
            prenome, sobrenome = self.extrair_prenome_e_sobrenome(nome_completo)
            
            return EstudanteCanonico(
                id_canonico=id_canonico,
                prenome=prenome,
                sobrenome=sobrenome,
                nome_completo=nome_completo,
                data_de_nascimento=dados.get("data_de_nascimento", ""),
                matricula=str(dados.get("matricula", "")),
                status_academico="ATIVO",  # Derivado dos dados
                status_biblioteca=dados.get("status_emprestimo_livros", "QUITADO")
            )
        except Exception as e:
            print(f"❌ Erro ao criar EstudanteCanonico: {e}")
            return None
    
    def extrair_prenome_e_sobrenome(self, nome_completo: str) -> tuple[str, str]:
        """Extrai prenome e sobrenome do nome completo"""
        if not nome_completo:
            return "", ""
        
        partes = nome_completo.strip().split(maxsplit=1)
        prenome = partes[0] if partes else ""
        sobrenome = partes[1] if len(partes) > 1 else ""
        
        return prenome, sobrenome


class CrudProcessor:
    """Processador principal de operações CRUD"""
    
    def __init__(self):
        self.estudante_processor = EstudanteProcessor()
    
    def process(self, message_data: str) -> Optional[Dict[str, Any]]:
        """Processa uma mensagem CRUD recebida"""
        try:
            operation = CrudOperation(json.loads(message_data))
            
            # Verifica se é uma operação CREATE do ORM
            if operation.operation == "CREATE" and operation.source == "ORM":
                return self._processar_entidade(operation)
            
            print(f"⚠️ Operação não suportada: {operation.operation} - {operation.source}")
            return None
        except Exception as e:
            print(f"❌ Erro ao processar mensagem CRUD: {e}")
            return None
    
    def _processar_entidade(self, operation: CrudOperation) -> Optional[Dict[str, Any]]:
        """Direciona o processamento baseado no tipo de entidade"""
        if operation.entity.lower() == "estudante":
            return self._processar_estudante(operation)
        
        print(f"⚠️ Entidade não suportada: {operation.entity}")
        return None
    
    def _processar_estudante(self, operation: CrudOperation) -> Optional[Dict[str, Any]]:
        """Processa especificamente entidades Estudante"""
        try:
            # Transforma para formato Usuario (SB)
            usuario_json = self.estudante_processor.estudante_para_usuario(operation.data)
            if not usuario_json:
                return None
            
            # Mapeia para endpoint HTTP
            http_method = "POST"  # Para CREATE
            target_endpoint = "http://localhost:8080/usuarios"
            
            return {
                "http_method": http_method,
                "target_endpoint": target_endpoint,
                "body": usuario_json,
                "operation": operation,
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            print(f"❌ Erro ao processar estudante: {e}")
            return None


class PersistenciaCanonicoProcessor:
    """Processa a persistência de dados canônicos e mapeamento de IDs"""
    
    def __init__(self):
        self.db = IntegratorDatabase()
        self.estudante_processor = EstudanteProcessor()
    
    def process(self, operation_data: Dict[str, Any], response_data: str) -> None:
        """Persiste dados canônicos e mapeamento após resposta HTTP"""
        try:
            operation = operation_data["operation"]
            
            # Verifica se deve processar (apenas Estudante/CREATE)
            if (operation.entity.lower() != "estudante" or 
                operation.operation != "CREATE"):
                return
            
            # Extrai IDs
            response_json = json.loads(response_data)
            id_sb = response_json.get("id")
            
            operation_json = json.loads(operation.data)
            id_sga = str(operation_json.get("id", ""))
            
            # Gera ID canônico
            id_canonico = str(uuid.uuid4())
            
            # Cria EstudanteCanonico
            estudante_canonico = self.estudante_processor.estudante_para_estudante_canonico(
                operation.data, id_canonico
            )
            
            if not estudante_canonico:
                print("❌ Erro ao criar EstudanteCanonico")
                return
            
            # Cria mapeamento de IDs
            id_mapping = EstudanteIdMapping(
                id_canonico=id_canonico,
                id_sga=id_sga,
                id_sb=id_sb,
                ultima_atualizacao=datetime.now().isoformat()
            )
            
            # Persiste no banco de dados
            self._persistir_canonico(estudante_canonico)
            self._persistir_mapping(id_mapping)
            
            print(f"✅ EstudanteCanonico persistido: {id_canonico}")
            print(f"✅ Mapeamento ID persistido: SGA={id_sga}, SB={id_sb}")
            
        except Exception as e:
            print(f"❌ Erro ao persistir dados canônicos: {e}")
    
    def _persistir_canonico(self, estudante_canonico: EstudanteCanonico) -> None:
        """Persiste EstudanteCanonico no banco"""
        session = self.db.get_session()
        try:
            model = EstudanteCanonicoModel(
                id_canonico=estudante_canonico.id_canonico,
                prenome=estudante_canonico.prenome,
                sobrenome=estudante_canonico.sobrenome,
                nome_completo=estudante_canonico.nome_completo,
                data_de_nascimento=estudante_canonico.data_de_nascimento,
                matricula=estudante_canonico.matricula,
                status_academico=estudante_canonico.status_academico,
                status_biblioteca=estudante_canonico.status_biblioteca
            )
            session.add(model)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def _persistir_mapping(self, id_mapping: EstudanteIdMapping) -> None:
        """Persiste mapeamento de IDs no banco"""
        session = self.db.get_session()
        try:
            model = EstudanteIdMappingModel(
                id_canonico=id_mapping.id_canonico,
                id_sga=id_mapping.id_sga,
                id_sb=id_mapping.id_sb,
                ultima_atualizacao=id_mapping.ultima_atualizacao
            )
            session.add(model)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


class HttpProcessor:
    """Processa requisições HTTP para endpoints externos"""
    
    def send_request(self, request_data: Dict[str, Any]) -> Optional[str]:
        """Envia requisição HTTP e retorna a resposta"""
        try:
            method = request_data["http_method"]
            url = request_data["target_endpoint"]
            headers = request_data.get("headers", {})
            body = request_data.get("body")
            
            print(f"📤 Enviando {method} para {url}")
            print(f"📋 Body: {body}")
            
            if method == "POST":
                response = requests.post(url, data=body, headers=headers)
            elif method == "PUT":
                response = requests.put(url, data=body, headers=headers)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                response = requests.get(url, headers=headers)
            
            print(f"📥 Resposta HTTP: Status={response.status_code}, Body={response.text}")
            
            if response.status_code in [200, 201]:
                return response.text
            else:
                print(f"⚠️ Resposta HTTP não esperada: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao enviar requisição HTTP: {e}")
            return None