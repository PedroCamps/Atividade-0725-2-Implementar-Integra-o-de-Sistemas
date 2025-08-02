import json
from typing import Generic, TypeVar, Type, List, Optional
from bson import ObjectId
from pymongo.collection import Collection

from ..domain.entities import Usuario, Obra, RegistroEmprestimo
from ..infrastructure.database import MongoDB
from ..infrastructure.redis_publisher import RedisPublisher, CrudOperation, OperationType, Source

T = TypeVar('T')


class MongoRepository(Generic[T]):
    def __init__(self, mongodb: MongoDB, collection_name: str, entity_class: Type[T], enable_crud_publishing: bool = True):
        self.mongodb = mongodb
        self.collection: Collection = mongodb.get_collection(collection_name)
        self.entity_class = entity_class
        self.enable_crud_publishing = enable_crud_publishing
        self.redis_publisher = RedisPublisher() if enable_crud_publishing else None
    
    def _entity_to_dict(self, entity: T) -> dict:
        """Converte entidade para dicionário MongoDB"""
        entity_dict = entity.__dict__.copy()
        # Remove o ID se for None para inserção
        if entity_dict.get('id') is None:
            entity_dict.pop('id', None)
        # Converte string ID para ObjectId se necessário
        elif isinstance(entity_dict.get('id'), str) and entity_dict['id']:
            try:
                entity_dict['_id'] = ObjectId(entity_dict['id'])
                del entity_dict['id']
            except:
                pass
        return entity_dict
    
    def _dict_to_entity(self, doc: dict) -> T:
        """Converte documento MongoDB para entidade"""
        if doc is None:
            return None
        
        # Converte ObjectId para string
        if '_id' in doc:
            doc['id'] = str(doc['_id'])
            del doc['_id']
        
        return self.entity_class(**doc)
    
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
                source=Source.ODM,
                data=entity_json
            )
            
            self.redis_publisher.publish_operation(operation)
        except Exception as e:
            print(f"❌ Erro ao publicar operação no Redis: {e}")
    
    def create(self, entity: T) -> T:
        """Cria uma nova entidade no MongoDB"""
        try:
            print(f"🔍 Criando entidade: {entity}")
            entity_dict = self._entity_to_dict(entity)
            result = self.collection.insert_one(entity_dict)
            
            # Atualiza o ID da entidade
            entity.id = str(result.inserted_id)
            
            if self.enable_crud_publishing:
                print(f"✅ Entidade criada: {entity}")
                print(f"  - Operation: CREATE")
                self._publish_crud_operation(OperationType.CREATE, entity)
            
            return entity
        except Exception as e:
            print(f"❌ Erro ao criar entidade: {e}")
            raise
    
    def find_by_id(self, entity_id: str) -> Optional[T]:
        """Busca entidade por ID"""
        try:
            doc = self.collection.find_one({"_id": ObjectId(entity_id)})
            return self._dict_to_entity(doc)
        except Exception as e:
            print(f"❌ Erro ao buscar entidade por ID: {e}")
            return None
    
    def find_all(self) -> List[T]:
        """Busca todas as entidades"""
        try:
            docs = self.collection.find()
            return [self._dict_to_entity(doc) for doc in docs]
        except Exception as e:
            print(f"❌ Erro ao buscar todas as entidades: {e}")
            return []
    
    def update(self, entity: T) -> T:
        """Atualiza uma entidade existente"""
        try:
            if not entity.id:
                raise ValueError("ID da entidade é obrigatório para atualização")
            
            entity_dict = self._entity_to_dict(entity)
            # Remove o _id do dict para update
            entity_dict.pop('_id', None)
            
            result = self.collection.update_one(
                {"_id": ObjectId(entity.id)},
                {"$set": entity_dict}
            )
            
            if result.matched_count == 0:
                raise ValueError(f"Entidade com ID {entity.id} não encontrada")
            
            if self.enable_crud_publishing:
                self._publish_crud_operation(OperationType.UPDATE, entity)
            
            return entity
        except Exception as e:
            print(f"❌ Erro ao atualizar entidade: {e}")
            raise
    
    def delete(self, entity: T) -> None:
        """Remove uma entidade do MongoDB"""
        try:
            if not entity.id:
                raise ValueError("ID da entidade é obrigatório para exclusão")
            
            result = self.collection.delete_one({"_id": ObjectId(entity.id)})
            
            if result.deleted_count > 0 and self.enable_crud_publishing:
                self._publish_crud_operation(OperationType.DELETE, entity)
        except Exception as e:
            print(f"❌ Erro ao deletar entidade: {e}")
            raise
    
    def set_enable_crud_publishing(self, enable: bool) -> None:
        """Habilita ou desabilita a publicação de eventos CRUD"""
        self.enable_crud_publishing = enable
        if enable and not self.redis_publisher:
            self.redis_publisher = RedisPublisher()
        elif not enable and self.redis_publisher:
            self.redis_publisher.close()
            self.redis_publisher = None


# Repositórios específicos
class UsuarioRepository(MongoRepository[Usuario]):
    def __init__(self, mongodb: MongoDB, enable_crud_publishing: bool = True):
        super().__init__(mongodb, "usuarios", Usuario, enable_crud_publishing)


class ObraRepository(MongoRepository[Obra]):
    def __init__(self, mongodb: MongoDB, enable_crud_publishing: bool = True):
        super().__init__(mongodb, "obras", Obra, enable_crud_publishing)


class RegistroEmprestimoRepository(MongoRepository[RegistroEmprestimo]):
    def __init__(self, mongodb: MongoDB, enable_crud_publishing: bool = True):
        super().__init__(mongodb, "registros_emprestimo", RegistroEmprestimo, enable_crud_publishing)