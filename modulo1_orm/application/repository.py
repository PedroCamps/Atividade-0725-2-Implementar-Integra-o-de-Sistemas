import json
from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy.orm import Session

from ..domain.entities import Estudante, Disciplina, Turma, Matricula
from ..infrastructure.models import Database, EstudanteModel, DisciplinaModel, TurmaModel, MatriculaModel
from ..infrastructure.redis_publisher import RedisPublisher, CrudOperation, OperationType, Source

T = TypeVar('T')
M = TypeVar('M')


class Repository(Generic[T, M]):
    def __init__(self, database: Database, entity_class: Type[T], model_class: Type[M], enable_crud_publishing: bool = True):
        self.database = database
        self.entity_class = entity_class
        self.model_class = model_class
        self.enable_crud_publishing = enable_crud_publishing
        self.redis_publisher = RedisPublisher() if enable_crud_publishing else None
    
    def _entity_to_model(self, entity: T) -> M:
        """Converte entidade de domínio para modelo de banco de dados"""
        entity_dict = entity.__dict__.copy()
        if hasattr(entity, 'status_emprestimo_livros') and entity.status_emprestimo_livros:
            entity_dict['status_emprestimo_livros'] = entity.status_emprestimo_livros.value
        if hasattr(entity, 'status') and entity.status:
            entity_dict['status'] = entity.status.value
        return self.model_class(**entity_dict)
    
    def _model_to_entity(self, model: M) -> T:
        """Converte modelo de banco de dados para entidade de domínio"""
        model_dict = {c.name: getattr(model, c.name) for c in model.__table__.columns}
        return self.entity_class(**model_dict)
    
    def _publish_crud_operation(self, operation_type: OperationType, entity: T) -> None:
        """Publica operação CRUD no Redis"""
        if not self.enable_crud_publishing or not self.redis_publisher:
            return
        
        try:
            entity_name = self.entity_class.__name__
            entity_json = json.dumps(entity.__dict__, default=str)
            
            operation = CrudOperation(
                entity=entity_name,
                operation=operation_type,
                source=Source.ORM,
                data=entity_json
            )
            
            self.redis_publisher.publish_operation(operation)
        except Exception as e:
            print(f"❌ Erro ao publicar operação no Redis: {e}")
    
    def create(self, entity: T) -> T:
        """Cria uma nova entidade no banco de dados"""
        session = self.database.get_session()
        try:
            print(f"🔍 Criando entidade: {entity}")
            model = self._entity_to_model(entity)
            session.add(model)
            session.commit()
            session.refresh(model)
            
            # Atualiza o ID da entidade
            entity.id = model.id
            
            if self.enable_crud_publishing:
                print(f"✅ Entidade criada: {entity}")
                print(f"  - Operation: CREATE")
                self._publish_crud_operation(OperationType.CREATE, entity)
            
            return entity
        except Exception as e:
            session.rollback()
            print(f"❌ Erro ao criar entidade: {e}")
            raise
        finally:
            session.close()
    
    def load_from_id(self, entity_id: int) -> Optional[T]:
        """Carrega entidade por ID"""
        session = self.database.get_session()
        try:
            model = session.query(self.model_class).filter_by(id=entity_id).first()
            return self._model_to_entity(model) if model else None
        finally:
            session.close()
    
    def load_all(self) -> List[T]:
        """Carrega todas as entidades"""
        session = self.database.get_session()
        try:
            models = session.query(self.model_class).all()
            return [self._model_to_entity(model) for model in models]
        finally:
            session.close()
    
    def update(self, entity: T) -> T:
        """Atualiza uma entidade existente"""
        session = self.database.get_session()
        try:
            model = session.query(self.model_class).filter_by(id=entity.id).first()
            if not model:
                raise ValueError(f"Entidade com ID {entity.id} não encontrada")
            
            # Atualiza os campos do modelo
            for key, value in entity.__dict__.items():
                if hasattr(model, key) and key != 'id':
                    if hasattr(value, 'value'):  # Para enums
                        setattr(model, key, value.value)
                    else:
                        setattr(model, key, value)
            
            session.commit()
            
            if self.enable_crud_publishing:
                self._publish_crud_operation(OperationType.UPDATE, entity)
            
            return entity
        except Exception as e:
            session.rollback()
            print(f"❌ Erro ao atualizar entidade: {e}")
            raise
        finally:
            session.close()
    
    def delete(self, entity: T) -> None:
        """Remove uma entidade do banco de dados"""
        session = self.database.get_session()
        try:
            model = session.query(self.model_class).filter_by(id=entity.id).first()
            if model:
                session.delete(model)
                session.commit()
                
                if self.enable_crud_publishing:
                    self._publish_crud_operation(OperationType.DELETE, entity)
        except Exception as e:
            session.rollback()
            print(f"❌ Erro ao deletar entidade: {e}")
            raise
        finally:
            session.close()
    
    def set_enable_crud_publishing(self, enable: bool) -> None:
        """Habilita ou desabilita a publicação de eventos CRUD"""
        self.enable_crud_publishing = enable
        if enable and not self.redis_publisher:
            self.redis_publisher = RedisPublisher()
        elif not enable and self.redis_publisher:
            self.redis_publisher.close()
            self.redis_publisher = None


# Repositórios específicos
class EstudanteRepository(Repository[Estudante, EstudanteModel]):
    def __init__(self, database: Database, enable_crud_publishing: bool = True):
        super().__init__(database, Estudante, EstudanteModel, enable_crud_publishing)


class DisciplinaRepository(Repository[Disciplina, DisciplinaModel]):
    def __init__(self, database: Database, enable_crud_publishing: bool = True):
        super().__init__(database, Disciplina, DisciplinaModel, enable_crud_publishing)


class TurmaRepository(Repository[Turma, TurmaModel]):
    def __init__(self, database: Database, enable_crud_publishing: bool = True):
        super().__init__(database, Turma, TurmaModel, enable_crud_publishing)


class MatriculaRepository(Repository[Matricula, MatriculaModel]):
    def __init__(self, database: Database, enable_crud_publishing: bool = True):
        super().__init__(database, Matricula, MatriculaModel, enable_crud_publishing)