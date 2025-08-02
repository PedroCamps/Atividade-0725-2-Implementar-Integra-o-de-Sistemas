import redis
import json
from datetime import datetime
from enum import Enum
from typing import Any, Dict


class OperationType(Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class Source(Enum):
    ORM = "ORM"
    ODM = "ODM"


class CrudOperation:
    def __init__(self, entity: str, operation: OperationType, source: Source, data: str, timestamp: str = None):
        self.entity = entity
        self.operation = operation
        self.source = source
        self.data = data
        self.timestamp = timestamp or datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity": self.entity,
            "operation": self.operation.value,
            "source": self.source.value,
            "data": self.data,
            "timestamp": self.timestamp
        }


class RedisPublisher:
    def __init__(self, redis_url: str = "redis://localhost:6379", channel: str = "crud-channel"):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.channel = channel
    
    def publish_operation(self, operation: CrudOperation) -> None:
        """Publica uma operação CRUD no Redis"""
        try:
            message = json.dumps(operation.to_dict())
            self.redis_client.publish(self.channel, message)
            print(f"✅ Evento publicado: {operation.entity} - {operation.operation.value}")
        except Exception as e:
            print(f"❌ Erro ao publicar evento: {e}")
    
    def close(self):
        self.redis_client.close()