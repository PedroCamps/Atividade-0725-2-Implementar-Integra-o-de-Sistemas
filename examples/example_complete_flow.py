#!/usr/bin/env python3
"""
Exemplo de fluxo completo de integração
Demonstra o processo end-to-end do sistema integrador
"""

import sys
import os
import time
import threading
import subprocess
from pathlib import Path

# Adiciona módulos ao path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "modulo1_orm"))
sys.path.append(str(project_root / "modulo3_integrador"))

from modulo1_orm.infrastructure.models import Database
from modulo1_orm.application.repository import EstudanteRepository
from modulo1_orm.domain.entities import Estudante, StatusEmprestimo

def check_services():
    """Verifica se Redis e MongoDB estão rodando"""
    print("🔍 Verificando serviços...")
    
    # Verificar Redis
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("✅ Redis: Conectado")
    except Exception as e:
        print(f"❌ Redis: {e}")
        return False
    
    # Verificar MongoDB
    try:
        import pymongo
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        client.admin.command('ping')
        print("✅ MongoDB: Conectado")
    except Exception as e:
        print(f"❌ MongoDB: {e}")
        return False
    
    return True

def start_services():
    """Inicia os serviços necessários em subprocessos"""
    print("🚀 Iniciando serviços...")
    
    processes = {}
    
    try:
        # Iniciar Sistema de Biblioteca
        print("📚 Iniciando Sistema de Biblioteca...")
        sb_process = subprocess.Popen([
            sys.executable, "main.py"
        ], cwd=project_root / "modulo2_odm")
        processes['sb'] = sb_process
        time.sleep(3)  # Aguarda inicialização
        
        # Iniciar Integrador
        print("🔧 Iniciando Integrador...")
        integrator_process = subprocess.Popen([
            sys.executable, "main.py"
        ], cwd=project_root / "modulo3_integrador")
        processes['integrator'] = integrator_process
        time.sleep(2)  # Aguarda inicialização
        
        return processes
    except Exception as e:
        print(f"❌ Erro ao iniciar serviços: {e}")
        # Cleanup
        for proc in processes.values():
            proc.terminate()
        return None

def create_sample_data():
    """Cria dados de exemplo no SGA"""
    print("📝 Criando dados de exemplo...")
    
    # Inicializa banco SGA
    db = Database("example_sga.db")
    estudante_repo = EstudanteRepository(db, enable_crud_publishing=True)
    
    # Estudantes de exemplo
    estudantes = [
        Estudante(
            nome_completo="João da Silva",
            data_de_nascimento="01/01/2000",
            matricula=123456,
            status_emprestimo_livros=StatusEmprestimo.QUITADO
        ),
        Estudante(
            nome_completo="Maria Santos",
            data_de_nascimento="15/03/1999",
            matricula=234567,
            status_emprestimo_livros=StatusEmprestimo.QUITADO
        ),
        Estudante(
            nome_completo="Pedro Oliveira",
            data_de_nascimento="22/08/2001",
            matricula=345678,
            status_emprestimo_livros=StatusEmprestimo.EM_ABERTO
        )
    ]
    
    created_estudantes = []
    for estudante in estudantes:
        print(f"🔍 Criando: {estudante.nome_completo}")
        created = estudante_repo.create(estudante)
        created_estudantes.append(created)
        print(f"✅ Criado ID: {created.id}")
        time.sleep(1)  # Pausa para visualizar o processamento
    
    db.close()
    return created_estudantes

def verify_integration():
    """Verifica se a integração funcionou"""
    print("\n🔍 Verificando resultados da integração...")
    
    try:
        import requests
        
        # Verificar API do SB
        response = requests.get("http://localhost:8080/usuarios")
        if response.status_code == 200:
            usuarios = response.json()
            print(f"✅ Usuários criados no SB: {len(usuarios)}")
            
            for usuario in usuarios:
                print(f"  📋 {usuario['prenome']} {usuario['sobrenome']} - {usuario['situacao_matricula']}")
        else:
            print(f"❌ Erro ao verificar API SB: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")

def main():
    """Execução principal do exemplo"""
    print("🎯 EXEMPLO: Fluxo Completo de Integração")
    print("=" * 50)
    
    # 1. Verificar pré-requisitos
    if not check_services():
        print("❌ Serviços necessários não estão disponíveis")
        print("💡 Certifique-se de que Redis e MongoDB estão rodando")
        return
    
    processes = None
    try:
        # 2. Iniciar serviços
        processes = start_services()
        if not processes:
            print("❌ Falha ao iniciar serviços")
            return
        
        print("\n⏳ Aguardando inicialização completa...")
        time.sleep(5)
        
        # 3. Criar dados de exemplo
        print("\n" + "=" * 50)
        created_estudantes = create_sample_data()
        
        # 4. Aguardar processamento
        print("\n⏳ Aguardando processamento da integração...")
        time.sleep(5)
        
        # 5. Verificar resultados
        verify_integration()
        
        print("\n🎉 Exemplo executado com sucesso!")
        print("📖 Verifique os logs dos serviços para detalhes")
        print("🌐 Acesse http://localhost:8080/docs para explorar a API")
        
        # Manter serviços rodando
        print("\n⏸️  Serviços continuarão rodando...")
        print("🛑 Pressione Ctrl+C para parar todos os serviços")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Parando serviços...")
    
    finally:
        # Cleanup
        if processes:
            for name, proc in processes.items():
                print(f"🧹 Parando {name}...")
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
        
        print("✅ Cleanup concluído")

if __name__ == "__main__":
    main()