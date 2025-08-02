#!/usr/bin/env python3
"""
Script para executar todos os testes do projeto
Facilita a execução de testes unitários e de integração
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, cwd=None, description=""):
    """Executa um comando e retorna o resultado"""
    print(f"🔧 {description}")
    print(f"📁 Diretório: {cwd or 'atual'}")
    print(f"⚡ Comando: {' '.join(command)}")
    
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        
        print("✅ Sucesso")
        if result.stdout:
            print("📄 Saída:")
            print(result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        print("❌ Falha")
        print(f"💥 Código de saída: {e.returncode}")
        if e.stdout:
            print("📄 Saída:")
            print(e.stdout)
        if e.stderr:
            print("🚨 Erro:")
            print(e.stderr)
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False


def test_module1_orm():
    """Testa o módulo 1 (SGA - ORM)"""
    print("\n" + "=" * 50)
    print("🧪 TESTES: Módulo 1 - SGA (ORM/SQLite)")
    print("=" * 50)
    
    project_root = Path(__file__).parent
    module_path = project_root / "modulo1_orm"
    
    if not module_path.exists():
        print("❌ Diretório modulo1_orm não encontrado")
        return False
    
    # Verificar se arquivo de teste existe
    test_file = module_path / "test_repository.py"
    if not test_file.exists():
        print("❌ Arquivo test_repository.py não encontrado")
        return False
    
    # Executar testes
    return run_command(
        [sys.executable, "-m", "unittest", "test_repository.py", "-v"],
        cwd=module_path,
        description="Executando testes unitários do repositório ORM"
    )


def test_module2_odm():
    """Testa o módulo 2 (SB - ODM)"""
    print("\n" + "=" * 50)
    print("🧪 TESTES: Módulo 2 - SB (ODM/MongoDB)")
    print("=" * 50)
    
    project_root = Path(__file__).parent
    module_path = project_root / "modulo2_odm"
    
    if not module_path.exists():
        print("❌ Diretório modulo2_odm não encontrado")
        return False
    
    # Verificar MongoDB
    print("🔍 Verificando conectividade MongoDB...")
    try:
        import pymongo
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        print("✅ MongoDB conectado")
    except Exception as e:
        print(f"❌ MongoDB não acessível: {e}")
        print("💡 Certifique-se de que o MongoDB está rodando")
        return False
    
    # Verificar se arquivo de teste existe
    test_file = module_path / "test_repository.py"
    if not test_file.exists():
        print("❌ Arquivo test_repository.py não encontrado")
        return False
    
    # Executar testes
    return run_command(
        [sys.executable, "-m", "unittest", "test_repository.py", "-v"],
        cwd=module_path,
        description="Executando testes unitários do repositório ODM"
    )


def test_module3_integrador():
    """Testa o módulo 3 (Integrador)"""
    print("\n" + "=" * 50)
    print("🧪 TESTES: Módulo 3 - Integrador")
    print("=" * 50)
    
    project_root = Path(__file__).parent
    module_path = project_root / "modulo3_integrador"
    
    if not module_path.exists():
        print("❌ Diretório modulo3_integrador não encontrado")
        return False
    
    # Verificar Redis
    print("🔍 Verificando conectividade Redis...")
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("✅ Redis conectado")
    except Exception as e:
        print(f"❌ Redis não acessível: {e}")
        print("💡 Certifique-se de que o Redis está rodando")
        return False
    
    # Verificar se arquivo de teste existe
    test_file = module_path / "test_integration.py"
    if not test_file.exists():
        print("❌ Arquivo test_integration.py não encontrado")
        return False
    
    # Executar testes
    return run_command(
        [sys.executable, "-m", "unittest", "test_integration.py", "-v"],
        cwd=module_path,
        description="Executando testes unitários do integrador"
    )


def test_examples():
    """Testa os exemplos"""
    print("\n" + "=" * 50)
    print("🧪 TESTES: Exemplos")
    print("=" * 50)
    
    project_root = Path(__file__).parent
    examples_path = project_root / "examples"
    
    if not examples_path.exists():
        print("❌ Diretório examples não encontrado")
        return False
    
    # Lista de exemplos para testar (que não requerem serviços externos)
    examples_to_test = [
        "example_data_transformation.py"
    ]
    
    success = True
    for example in examples_to_test:
        example_file = examples_path / example
        if example_file.exists():
            print(f"\n🔍 Testando exemplo: {example}")
            result = run_command(
                [sys.executable, str(example_file)],
                cwd=examples_path,
                description=f"Executando {example}"
            )
            success = success and result
        else:
            print(f"⚠️ Exemplo {example} não encontrado")
    
    return success


def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    print("\n" + "=" * 50)
    print("🔍 VERIFICAÇÃO: Dependências")
    print("=" * 50)
    
    # Dependências principais
    dependencies = [
        ("sqlalchemy", "SQLAlchemy"),
        ("redis", "Redis"),
        ("pymongo", "PyMongo"),
        ("fastapi", "FastAPI"),
        ("requests", "Requests"),
        ("pydantic", "Pydantic")
    ]
    
    missing = []
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - não instalado")
            missing.append(name)
    
    if missing:
        print(f"\n⚠️ Dependências faltando: {', '.join(missing)}")
        print("💡 Execute: pip install -r requirements.txt em cada módulo")
        return False
    
    print("\n✅ Todas as dependências estão instaladas")
    return True


def check_services():
    """Verifica se os serviços necessários estão rodando"""
    print("\n" + "=" * 50)
    print("🔍 VERIFICAÇÃO: Serviços")
    print("=" * 50)
    
    services_ok = True
    
    # Redis
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("✅ Redis - rodando")
    except Exception:
        print("❌ Redis - não acessível")
        services_ok = False
    
    # MongoDB
    try:
        import pymongo
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        print("✅ MongoDB - rodando")
    except Exception:
        print("❌ MongoDB - não acessível")
        services_ok = False
    
    if not services_ok:
        print("\n💡 Para iniciar os serviços:")
        print("   Redis: redis-server")
        print("   MongoDB: mongod")
    
    return services_ok


def main():
    """Função principal"""
    print("🎯 EXECUÇÃO DE TESTES - Integrador Python")
    print("=" * 60)
    
    # Verificações iniciais
    deps_ok = check_dependencies()
    services_ok = check_services()
    
    if not deps_ok:
        print("\n❌ Dependências faltando. Execute os testes após instalar.")
        return False
    
    # Executar testes (mesmo sem serviços para testes que não precisam)
    results = []
    
    # Testes que não precisam de serviços externos
    print("\n🧪 Executando testes unitários...")
    results.append(("Exemplos", test_examples()))
    
    # Testes que precisam de serviços
    if services_ok:
        results.append(("Módulo 1 (ORM)", test_module1_orm()))
        results.append(("Módulo 2 (ODM)", test_module2_odm())) 
        results.append(("Módulo 3 (Integrador)", test_module3_integrador()))
    else:
        print("\n⚠️ Pulando testes que requerem Redis/MongoDB")
    
    # Resumo dos resultados
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    success_count = 0
    total_count = len(results)
    
    for test_name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{test_name:25} {status}")
        if success:
            success_count += 1
    
    print(f"\n📈 Total: {success_count}/{total_count} testes passaram")
    
    if success_count == total_count:
        print("🎉 Todos os testes passaram!")
        return True
    else:
        print("⚠️ Alguns testes falharam")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)