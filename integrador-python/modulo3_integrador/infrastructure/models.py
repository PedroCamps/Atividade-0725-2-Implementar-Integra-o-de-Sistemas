from sqlalchemy import Column, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class EstudanteCanonicoModel(Base):
    __tablename__ = "estudante_canonico"
    
    id_canonico = Column(String(36), primary_key=True)
    prenome = Column(String(100))
    sobrenome = Column(String(100))
    nome_completo = Column(String(255))
    data_de_nascimento = Column(String(10))
    matricula = Column(String(20))
    status_academico = Column(String(20))
    status_biblioteca = Column(String(20))


class EstudanteIdMappingModel(Base):
    __tablename__ = "estudante_id_mapping"
    
    id_canonico = Column(String(36), primary_key=True)
    id_sga = Column(String(20))
    id_sb = Column(String(50))
    ultima_atualizacao = Column(String(30))


class IntegratorDatabase:
    def __init__(self, db_name: str = "integrador.db"):
        self.engine = create_engine(f"sqlite:///{db_name}")
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def get_session(self):
        return self.SessionLocal()
    
    def close(self):
        self.engine.dispose()