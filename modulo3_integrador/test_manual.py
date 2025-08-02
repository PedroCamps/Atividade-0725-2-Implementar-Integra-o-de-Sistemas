"""
Script para teste manual do integrador
Similar ao MainTest.java do projeto original
"""

import sys
import os

# Adiciona o módulo ORM ao path para importar as classes
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'modulo1_orm'))

from modulo1_orm.infrastructure.models import Database
from modulo1_orm.application.repository import EstudanteRepository
from modulo1_orm.domain.entities import Estudante, StatusEmprestimo


def main():
    print("🧪 Teste Manual do Integrador - Criação de Estudante")
    print("📝 Este teste irá criar um estudante no SGA e publicar evento no Redis")
    
    # Inicializa o banco de dados SGA
    db = Database("sga_test.db")
    
    # Cria repositório com publicação habilitada
    estudante_repo = EstudanteRepository(db, enable_crud_publishing=True)
    
    # Cria um estudante de exemplo
    estudante = Estudante(
        nome_completo="João da Silva",
        data_de_nascimento="01/01/2000",
        matricula=123456,
        status_emprestimo_livros=StatusEmprestimo.QUITADO
    )
    
    print(f"🔍 Criando estudante: {estudante}")
    
    # Cria o estudante (deve publicar evento no Redis)
    estudante_criado = estudante_repo.create(estudante)
    
    print(f"✅ Estudante criado com ID: {estudante_criado.id}")
    print("📡 Evento CRUD publicado no Redis")
    print("🔄 O integrador deve processar este evento automaticamente")
    print("📋 Verifique os logs do integrador e do Sistema de Biblioteca")
    
    # Fecha o banco de dados
    db.close()


if __name__ == "__main__":
    main()