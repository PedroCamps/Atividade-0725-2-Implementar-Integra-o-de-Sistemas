from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class EstudanteModel(Base):
    __tablename__ = "estudantes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_completo = Column(String(255), nullable=False)
    data_de_nascimento = Column(String(10), nullable=False)
    matricula = Column(Integer, nullable=False, unique=True)
    status_emprestimo_livros = Column(String(20), default="QUITADO")
    
    matriculas = relationship("MatriculaModel", back_populates="estudante")


class DisciplinaModel(Base):
    __tablename__ = "disciplinas"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    codigo = Column(String(20), nullable=False, unique=True)
    creditos = Column(Integer, nullable=False)
    
    turmas = relationship("TurmaModel", back_populates="disciplina")


class TurmaModel(Base):
    __tablename__ = "turmas"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(20), nullable=False)
    disciplina_id = Column(Integer, ForeignKey("disciplinas.id"), nullable=False)
    semestre = Column(String(10), nullable=False)
    professor = Column(String(255), nullable=False)
    
    disciplina = relationship("DisciplinaModel", back_populates="turmas")
    matriculas = relationship("MatriculaModel", back_populates="turma")


class MatriculaModel(Base):
    __tablename__ = "matriculas"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    estudante_id = Column(Integer, ForeignKey("estudantes.id"), nullable=False)
    turma_id = Column(Integer, ForeignKey("turmas.id"), nullable=False)
    status = Column(String(20), default="ATIVA")
    data_matricula = Column(String(10), nullable=False)
    
    estudante = relationship("EstudanteModel", back_populates="matriculas")
    turma = relationship("TurmaModel", back_populates="matriculas")


class Database:
    def __init__(self, db_name: str = "sga.db"):
        self.engine = create_engine(f"sqlite:///{db_name}")
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def get_session(self):
        return self.SessionLocal()
    
    def close(self):
        self.engine.dispose()