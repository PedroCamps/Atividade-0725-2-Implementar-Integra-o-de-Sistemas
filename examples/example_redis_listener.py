#!/usr/bin/env python3
"""
Exemplo de listener Redis independente
Demonstra como escutar eventos CRUD sem o integrador completo
"""

import redis
import json
import signal
import sys
from datetime import datetime


class SimpleRedisListener:
    def __init__(self, redis_url="redis://localhost:6379", channel="crud-channel"):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.pubsub = self.redis_client.pubsub()
        self.channel = channel
        self.running = True
        
        # Configurar handler de sinal
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handler para Ctrl+C"""
        print(f"\n🛑 Recebido sinal {signum}, parando listener...")
        self.running = False
    
    def start(self):
        """Inicia a escuta do canal Redis"""
        print("🔊 Redis Listener Independente")
        print(f"📡 Canal: {self.channel}")
        print("🟢 Iniciando escuta...")
        print("🛑 Pressione Ctrl+C para parar\n")
        
        try:
            # Subscrever ao canal
            self.pubsub.subscribe(self.channel)
            
            # Loop de escuta
            for message in self.pubsub.listen():
                if not self.running:
                    break
                
                if message['type'] == 'message':
                    self._process_message(message)
        
        except Exception as e:
            print(f"❌ Erro no listener: {e}")
        finally:
            self._cleanup()
    
    def _process_message(self, message):
        """Processa uma mensagem recebida"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            channel = message['channel']
            data = message['data']
            
            print(f"🔔 [{timestamp}] [{channel}] {data}")
            
            # Parse do JSON para análise detalhada
            crud_data = json.loads(data)
            
            entity = crud_data.get('entity', 'Unknown')
            operation = crud_data.get('operation', 'Unknown')
            source = crud_data.get('source', 'Unknown')
            
            print(f"   📊 Entidade: {entity}")
            print(f"   ⚡ Operação: {operation}")
            print(f"   🏷️  Origem: {source}")
            
            # Parse dos dados da entidade
            entity_data = json.loads(crud_data.get('data', '{}'))
            if entity_data:
                print(f"   📋 Dados:")
                for key, value in entity_data.items():
                    print(f"      • {key}: {value}")
            
            print()  # Linha em branco para separar mensagens
            
        except json.JSONDecodeError:
            print(f"❌ Erro ao fazer parse do JSON: {data}")
        except Exception as e:
            print(f"❌ Erro ao processar mensagem: {e}")
    
    def _cleanup(self):
        """Limpa recursos"""
        print("🧹 Limpando recursos...")
        self.pubsub.unsubscribe(self.channel)
        self.pubsub.close()
        self.redis_client.close()
        print("✅ Redis listener parado")


def test_connection():
    """Testa a conexão com Redis"""
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("✅ Conexão Redis OK")
        return True
    except Exception as e:
        print(f"❌ Erro de conexão Redis: {e}")
        print("💡 Certifique-se de que o Redis está rodando: redis-server")
        return False


def main():
    """Função principal"""
    print("🎯 EXEMPLO: Redis Listener Independente")
    print("=" * 50)
    
    # Testar conexão
    if not test_connection():
        return
    
    # Criar e iniciar listener
    listener = SimpleRedisListener()
    listener.start()


if __name__ == "__main__":
    main()