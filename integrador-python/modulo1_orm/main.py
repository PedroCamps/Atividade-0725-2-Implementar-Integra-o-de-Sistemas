from infrastructure.models import Database
from application.repository import EstudanteRepository
from domain.entities import Estudante, StatusEmprestimo


def main():
    print("🚀 Sistema de Gestão Acadêmica (SGA) - Módulo ORM")
    
    # Inicializa o banco de dados
    db = Database("sga.db")
    
    # Cria repositório
    estudante_repo = EstudanteRepository(db, enable_crud_publishing=True)
    
    # Exemplo de criação de estudante
    estudante = Estudante(
        nome_completo="João da Silva",
        data_de_nascimento="01/01/2000",
        matricula=123456,
        status_emprestimo_livros=StatusEmprestimo.QUITADO
    )
    
    # Cria o estudante (vai publicar evento no Redis)
    estudante_criado = estudante_repo.create(estudante)
    print(f"📝 Estudante criado com ID: {estudante_criado.id}")
    
    # Lista todos os estudantes
    estudantes = estudante_repo.load_all()
    print(f"📋 Total de estudantes cadastrados: {len(estudantes)}")
    
    # Fecha o banco de dados
    db.close()


if __name__ == "__main__":
    main()