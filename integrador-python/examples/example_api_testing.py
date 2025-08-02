#!/usr/bin/env python3
"""
Exemplo de teste da API do Sistema de Biblioteca
Demonstra como interagir com a API REST do SB
"""

import requests
import json
import time
from typing import Optional, Dict, Any


class SBApiClient:
    """Cliente para API do Sistema de Biblioteca"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json"
        })
    
    def health_check(self) -> bool:
        """Verifica se a API está funcionando"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception:
            return False
    
    def create_usuario(self, usuario_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Cria um novo usuário"""
        try:
            response = self.session.post(
                f"{self.base_url}/usuarios", 
                json=usuario_data
            )
            return response.json() if response.status_code == 201 else None
        except Exception as e:
            print(f"❌ Erro ao criar usuário: {e}")
            return None
    
    def get_usuarios(self) -> list:
        """Lista todos os usuários"""
        try:
            response = self.session.get(f"{self.base_url}/usuarios")
            return response.json() if response.status_code == 200 else []
        except Exception as e:
            print(f"❌ Erro ao listar usuários: {e}")
            return []
    
    def get_usuario(self, usuario_id: str) -> Optional[Dict[str, Any]]:
        """Obtém um usuário específico"""
        try:
            response = self.session.get(f"{self.base_url}/usuarios/{usuario_id}")
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"❌ Erro ao obter usuário: {e}")
            return None
    
    def update_usuario(self, usuario_id: str, usuario_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza um usuário"""
        try:
            response = self.session.put(
                f"{self.base_url}/usuarios/{usuario_id}",
                json=usuario_data
            )
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"❌ Erro ao atualizar usuário: {e}")
            return None
    
    def delete_usuario(self, usuario_id: str) -> bool:
        """Remove um usuário"""
        try:
            response = self.session.delete(f"{self.base_url}/usuarios/{usuario_id}")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Erro ao deletar usuário: {e}")
            return False


def test_api_connection():
    """Testa conectividade com a API"""
    print("🔍 Testando conectividade com API...")
    
    client = SBApiClient()
    
    if client.health_check():
        print("✅ API está respondendo")
        return client
    else:
        print("❌ API não está acessível")
        print("💡 Certifique-se de que o Sistema de Biblioteca está rodando:")
        print("   cd modulo2_odm && python main.py")
        return None


def example_crud_operations():
    """Exemplo de operações CRUD via API"""
    print("\n🔧 Exemplo: Operações CRUD via API")
    print("-" * 40)
    
    client = test_api_connection()
    if not client:
        return
    
    # CREATE - Criar usuários
    print("\n📝 1. Criando usuários...")
    usuarios_exemplo = [
        {
            "prenome": "João",
            "sobrenome": "Silva", 
            "situacao_matricula": "ATIVO"
        },
        {
            "prenome": "Maria",
            "sobrenome": "Santos",
            "situacao_matricula": "ATIVO"
        },
        {
            "prenome": "Pedro",
            "sobrenome": "Oliveira",
            "situacao_matricula": "INATIVO"
        }
    ]
    
    usuarios_criados = []
    for i, usuario_data in enumerate(usuarios_exemplo, 1):
        print(f"  Criando usuário {i}: {usuario_data['prenome']} {usuario_data['sobrenome']}")
        
        usuario_criado = client.create_usuario(usuario_data)
        if usuario_criado:
            usuarios_criados.append(usuario_criado)
            print(f"  ✅ Criado com ID: {usuario_criado['id']}")
        else:
            print(f"  ❌ Falha ao criar usuário")
    
    # READ - Listar usuários
    print(f"\n📋 2. Listando todos os usuários...")
    todos_usuarios = client.get_usuarios()
    print(f"  Total de usuários: {len(todos_usuarios)}")
    
    for usuario in todos_usuarios:
        print(f"  • {usuario['prenome']} {usuario['sobrenome']} - {usuario['situacao_matricula']} (ID: {usuario['id']})")
    
    if not usuarios_criados:
        print("⚠️ Nenhum usuário foi criado, pulando testes UPDATE/DELETE")
        return
    
    # READ - Obter usuário específico
    primeiro_usuario = usuarios_criados[0]
    print(f"\n🔍 3. Obtendo usuário específico (ID: {primeiro_usuario['id']})...")
    usuario_obtido = client.get_usuario(primeiro_usuario['id'])
    
    if usuario_obtido:
        print(f"  ✅ Usuário encontrado:")
        print(f"     Nome: {usuario_obtido['prenome']} {usuario_obtido['sobrenome']}")
        print(f"     Situação: {usuario_obtido['situacao_matricula']}")
    else:
        print(f"  ❌ Usuário não encontrado")
    
    # UPDATE - Atualizar usuário
    print(f"\n✏️ 4. Atualizando usuário (ID: {primeiro_usuario['id']})...")
    dados_atualizacao = {
        "prenome": primeiro_usuario['prenome'],
        "sobrenome": primeiro_usuario['sobrenome'],
        "situacao_matricula": "INATIVO"  # Mudando status
    }
    
    usuario_atualizado = client.update_usuario(primeiro_usuario['id'], dados_atualizacao)
    if usuario_atualizado:
        print(f"  ✅ Status atualizado para: {usuario_atualizado['situacao_matricula']}")
    else:
        print(f"  ❌ Falha ao atualizar usuário")
    
    # DELETE - Remover último usuário
    if len(usuarios_criados) > 1:
        ultimo_usuario = usuarios_criados[-1]
        print(f"\n🗑️ 5. Removendo usuário (ID: {ultimo_usuario['id']})...")
        
        if client.delete_usuario(ultimo_usuario['id']):
            print(f"  ✅ Usuário removido com sucesso")
            
            # Verificar se realmente foi removido
            verificacao = client.get_usuario(ultimo_usuario['id'])
            if not verificacao:
                print(f"  ✅ Confirmado: usuário não existe mais")
            else:
                print(f"  ⚠️ Usuário ainda existe após deleção")
        else:
            print(f"  ❌ Falha ao remover usuário")


def example_integration_simulation():
    """Simula o comportamento do integrador"""
    print("\n🔄 Exemplo: Simulação de Integração")
    print("-" * 42)
    
    client = test_api_connection()
    if not client:
        return
    
    # Simular dados que viriam do SGA
    estudante_sga = {
        "id": 999,
        "nome_completo": "Ana Carolina Costa",
        "data_de_nascimento": "10/05/1998",
        "matricula": 456789,
        "status_emprestimo_livros": "QUITADO"
    }
    
    print("📥 Dados recebidos do SGA:")
    print(json.dumps(estudante_sga, indent=2, ensure_ascii=False))
    
    # Simular transformação (igual ao EstudanteProcessor)
    nome_completo = estudante_sga["nome_completo"]
    partes = nome_completo.split(maxsplit=1)
    prenome = partes[0] if partes else ""
    sobrenome = partes[1] if len(partes) > 1 else ""
    
    usuario_sb = {
        "prenome": prenome,
        "sobrenome": sobrenome,
        "situacao_matricula": "ATIVO"  # Mapeamento padrão
    }
    
    print("\n🔄 Dados transformados para SB:")
    print(json.dumps(usuario_sb, indent=2, ensure_ascii=False))
    
    # Enviar para API (simular integrador)
    print("\n📤 Enviando para API do SB...")
    usuario_criado = client.create_usuario(usuario_sb)
    
    if usuario_criado:
        print("✅ Usuário criado com sucesso no SB:")
        print(f"   ID: {usuario_criado['id']}")
        print(f"   Nome: {usuario_criado['prenome']} {usuario_criado['sobrenome']}")
        print(f"   Situação: {usuario_criado['situacao_matricula']}")
        
        # Simular persistência canônica (logs)
        print("\n💾 Dados que seriam persistidos no modelo canônico:")
        print(f"   ID Canônico: {uuid.uuid4()}")
        print(f"   ID SGA: {estudante_sga['id']}")
        print(f"   ID SB: {usuario_criado['id']}")
        print(f"   Timestamp: {time.strftime('%Y-%m-%dT%H:%M:%S')}")
        
    else:
        print("❌ Falha ao criar usuário no SB")


def example_error_handling():
    """Exemplo de tratamento de erros da API"""
    print("\n❌ Exemplo: Tratamento de Erros")
    print("-" * 35)
    
    client = test_api_connection()
    if not client:
        return
    
    # Teste 1: ID inválido
    print("🔍 1. Testando ID inválido...")
    usuario_inexistente = client.get_usuario("id_invalido_123")
    if not usuario_inexistente:
        print("  ✅ Corretamente retornado None para ID inválido")
    
    # Teste 2: Dados inválidos para criação
    print("\n🔍 2. Testando dados inválidos...")
    dados_invalidos = {}  # Dados vazios
    usuario_invalido = client.create_usuario(dados_invalidos)
    if not usuario_invalido:
        print("  ✅ Corretamente rejeitado dados inválidos")
    
    # Teste 3: Atualização de usuário inexistente
    print("\n🔍 3. Testando atualização de usuário inexistente...")
    resultado_update = client.update_usuario("id_inexistente", {"prenome": "Teste"})
    if not resultado_update:
        print("  ✅ Corretamente falhou ao atualizar usuário inexistente")


def main():
    """Função principal"""
    print("🎯 EXEMPLO: Teste da API do Sistema de Biblioteca")
    print("=" * 55)
    
    # Executar exemplos
    example_crud_operations()
    example_integration_simulation()
    example_error_handling()
    
    print("\n🎉 Testes da API concluídos!")
    print("💡 Verifique a documentação em: http://localhost:8080/docs")


if __name__ == "__main__":
    # Import necessário para simulação
    import uuid
    main()