from dataclasses import dataclass
from typing import Optional


@dataclass
class EstudanteCanonico:
    id_canonico: str
    prenome: str = ""
    sobrenome: str = ""
    nome_completo: str = ""
    data_de_nascimento: str = ""
    matricula: str = ""
    status_academico: str = ""
    status_biblioteca: str = ""


@dataclass
class EstudanteIdMapping:
    id_canonico: str
    id_sga: Optional[str] = None
    id_sb: Optional[str] = None
    ultima_atualizacao: str = ""