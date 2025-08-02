#!/usr/bin/env python3
"""
Exemplo de transformação de dados
Demonstra como os processadores transformam dados entre formatos
"""

import json
import uuid
import sys
from pathlib import Path

# Adiciona módulo integrador ao path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "modulo3_integrador"))

from application.processors import EstudanteProcessor, CrudProcessor


def example_name_splitting():
    """Exemplo de divisão de nome completo"""
    print("📝 Exemplo: Divisão de Nome Completo")
    print("-" * 40)
    
    processor = EstudanteProcessor()
    
    test_names = [
        "João da Silva",
        "Maria",
        "Pedro Santos Oliveira",
        "Ana Carolina Costa e Silva",
        ""
    ]
    
    for nome in test_names:
        prenome, sobrenome = processor.extrair_prenome_e_sobrenome(nome)
        print(f"'{nome}' → Prenome: '{prenome}', Sobrenome: '{sobrenome}'")


def example_estudante_to_usuario():
    """Exemplo de transformação Estudante → Usuario"""
    print("\n👤 Exemplo: Transformação Estudante → Usuario")
    print("-" * 50)
    
    processor = EstudanteProcessor()
    
    # Dados de exemplo do SGA
    estudante_data = {
        "id": 1,
        "nome_completo": "João da Silva",
        "data_de_nascimento": "01/01/2000",
        "matricula": 123456,
        "status_emprestimo_livros": "QUITADO"
    }
    
    print("📋 Dados de entrada (SGA):")
    print(json.dumps(estudante_data, indent=2, ensure_ascii=False))
    
    # Transformação
    usuario_json = processor.estudante_para_usuario(json.dumps(estudante_data))
    usuario_data = json.loads(usuario_json)
    
    print("\n📋 Dados de saída (SB):")
    print(json.dumps(usuario_data, indent=2, ensure_ascii=False))
    
    print("\n🔄 Mapeamento de campos:")
    print(f"  nome_completo → prenome: '{estudante_data['nome_completo']}' → '{usuario_data['prenome']}'")
    print(f"  nome_completo → sobrenome: '{estudante_data['nome_completo']}' → '{usuario_data['sobrenome']}'")
    print(f"  (default) → situacao_matricula: → '{usuario_data['situacao_matricula']}'")


def example_canonical_model():
    """Exemplo de criação do modelo canônico"""
    print("\n🏛️ Exemplo: Modelo Canônico")
    print("-" * 40)
    
    processor = EstudanteProcessor()
    
    # Dados de exemplo
    estudante_data = {
        "id": 1,
        "nome_completo": "Maria Santos",
        "data_de_nascimento": "15/03/1999",
        "matricula": 234567,
        "status_emprestimo_livros": "QUITADO"
    }
    
    print("📋 Dados originais:")
    print(json.dumps(estudante_data, indent=2, ensure_ascii=False))
    
    # Criar modelo canônico
    canonico = processor.estudante_para_estudante_canonico(
        json.dumps(estudante_data)
    )
    
    print("\n🏛️ Modelo canônico:")
    print(f"  ID Canônico: {canonico.id_canonico}")
    print(f"  Prenome: {canonico.prenome}")
    print(f"  Sobrenome: {canonico.sobrenome}")
    print(f"  Nome Completo: {canonico.nome_completo}")
    print(f"  Data Nascimento: {canonico.data_de_nascimento}")
    print(f"  Matrícula: {canonico.matricula}")
    print(f"  Status Acadêmico: {canonico.status_academico}")
    print(f"  Status Biblioteca: {canonico.status_biblioteca}")


def example_crud_processing():
    """Exemplo de processamento completo de CRUD"""
    print("\n⚙️ Exemplo: Processamento CRUD Completo")
    print("-" * 50)
    
    processor = CrudProcessor()
    
    # Simulação de mensagem Redis
    crud_message = {
        "entity": "Estudante",
        "operation": "CREATE",
        "source": "ORM",
        "data": json.dumps({
            "id": 1,
            "nome_completo": "Pedro Oliveira",
            "data_de_nascimento": "22/08/2001",
            "matricula": 345678,
            "status_emprestimo_livros": "EM_ABERTO"
        }),
        "timestamp": "2024-01-01T10:00:00"
    }
    
    print("📥 Mensagem CRUD recebida:")
    print(json.dumps(crud_message, indent=2, ensure_ascii=False))
    
    # Processar mensagem
    result = processor.process(json.dumps(crud_message))
    
    if result:
        print("\n📤 Resultado do processamento:")
        print(f"  Método HTTP: {result['http_method']}")
        print(f"  Endpoint: {result['target_endpoint']}")
        print(f"  Headers: {result['headers']}")
        print(f"  Body: {result['body']}")
        
        # Parse do body para visualização
        body_data = json.loads(result['body'])
        print("\n📋 Dados transformados:")
        print(json.dumps(body_data, indent=2, ensure_ascii=False))
    else:
        print("\n⚠️ Mensagem não foi processada (operação não suportada)")


def example_unsupported_operations():
    """Exemplo de operações não suportadas"""
    print("\n❌ Exemplo: Operações Não Suportadas")
    print("-" * 45)
    
    processor = CrudProcessor()
    
    unsupported_cases = [
        {
            "case": "Operação UPDATE",
            "message": {
                "entity": "Estudante",
                "operation": "UPDATE",
                "source": "ORM",
                "data": '{"id": 1}',
                "timestamp": "2024-01-01T10:00:00"
            }
        },
        {
            "case": "Fonte ODM",
            "message": {
                "entity": "Estudante", 
                "operation": "CREATE",
                "source": "ODM",
                "data": '{"id": "507f1f77bcf86cd799439011"}',
                "timestamp": "2024-01-01T10:00:00"
            }
        },
        {
            "case": "Entidade Professor",
            "message": {
                "entity": "Professor",
                "operation": "CREATE", 
                "source": "ORM",
                "data": '{"id": 1, "nome": "Dr. Silva"}',
                "timestamp": "2024-01-01T10:00:00"
            }
        }
    ]
    
    for case in unsupported_cases:
        print(f"\n🔍 Testando: {case['case']}")
        result = processor.process(json.dumps(case['message']))
        
        if result:
            print(f"  ✅ Processado: {result['http_method']} {result['target_endpoint']}")
        else:
            print(f"  ❌ Não processado (esperado)")


def main():
    """Função principal"""
    print("🎯 EXEMPLO: Transformação de Dados")
    print("=" * 50)
    
    # Executar exemplos
    example_name_splitting()
    example_estudante_to_usuario() 
    example_canonical_model()
    example_crud_processing()
    example_unsupported_operations()
    
    print("\n🎉 Exemplos de transformação concluídos!")
    print("💡 Estes são os mesmos processadores usados pelo integrador real")


if __name__ == "__main__":
    main()