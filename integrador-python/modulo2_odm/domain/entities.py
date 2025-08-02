from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Usuario:
    id: Optional[str] = None
    prenome: str = ""
    sobrenome: str = ""
    situacao_matricula: str = "ATIVO"


@dataclass
class Obra:
    id: Optional[str] = None
    codigo: str = ""
    titulo_principal: str = ""
    autor_principal: str = ""
    isbn: str = ""


@dataclass
class RegistroEmprestimo:
    id: Optional[str] = None
    usuario_id: str = ""
    obra_id: str = ""
    codigo_emprestimo: str = ""
    data_inicio: str = ""
    data_previsao_devolucao: str = ""