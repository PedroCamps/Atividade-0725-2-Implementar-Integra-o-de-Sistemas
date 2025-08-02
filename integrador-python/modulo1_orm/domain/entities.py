from dataclasses import dataclass
from typing import Optional
from enum import Enum


class StatusEmprestimo(Enum):
    QUITADO = "QUITADO"
    EM_ABERTO = "EM_ABERTO"


class StatusMatricula(Enum):
    ATIVA = "ATIVA"
    TRANCADA = "TRANCADA"
    CANCELADA = "CANCELADA"


@dataclass
class Estudante:
    id: Optional[int] = None
    nome_completo: str = ""
    data_de_nascimento: str = ""
    matricula: int = 0
    status_emprestimo_livros: StatusEmprestimo = StatusEmprestimo.QUITADO


@dataclass
class Disciplina:
    id: Optional[int] = None
    nome: str = ""
    codigo: str = ""
    creditos: int = 0


@dataclass
class Turma:
    id: Optional[int] = None
    codigo: str = ""
    disciplina_id: int = 0
    semestre: str = ""
    professor: str = ""


@dataclass
class Matricula:
    id: Optional[int] = None
    estudante_id: int = 0
    turma_id: int = 0
    status: StatusMatricula = StatusMatricula.ATIVA
    data_matricula: str = ""