import redis
import json
import threading
from typing import Callable, Any


class RedisListener:
    def __init__(self, redis_url: str = "redis://localhost:6379", channel: str = "crud-channel"):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.pubsub = self.redis_client.pubsub()
        self.channel = channel
        self.message_handler: Callable[[str, str], None] = None
        self.is_listening = False
        self.listener_thread = None
    
    def set_message_handler(self, handler: Callable[[str, str], None]):
        """Define o handler para processar mensagens recebidas"""
        self.message_handler = handler
    
    def start(self):
        """Inicia a escuta do canal Redis"""
        if self.is_listening:
            print("⚠️ Listener já está ativo")
            return
        
        if not self.message_handler:
            raise ValueError("Message handler deve ser definido antes de iniciar")
        
        self.pubsub.subscribe(self.channel)
        self.is_listening = True
        
        print(f"🟢 Escutando canal Redis: {self.channel}")
        
        # Inicia thread para escutar mensagens
        self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listener_thread.start()
    
    def _listen_loop(self):
        """Loop principal para escutar mensagens"""
        try:
            for message in self.pubsub.listen():
                if not self.is_listening:
                    break
                
                if message['type'] == 'message':
                    channel = message['channel']
                    data = message['data']
                    
                    print(f"🔔 [{channel}] {data}")
                    
                    # Chama o handler definido
                    if self.message_handler:
                        try:
                            self.message_handler(channel, data)
                        except Exception as e:
                            print(f"❌ Erro ao processar mensagem: {e}")
        except Exception as e:
            print(f"❌ Erro no loop de escuta: {e}")
        finally:
            self.is_listening = False
    
    def stop(self):
        """Para a escuta do canal Redis"""
        if not self.is_listening:
            return
        
        self.is_listening = False
        self.pubsub.unsubscribe(self.channel)
        self.pubsub.close()
        
        if self.listener_thread and self.listener_thread.is_alive():
            self.listener_thread.join(timeout=5)
        
        print("🛑 Listener Redis parado")
    
    def close(self):
        """Fecha a conexão Redis"""
        self.stop()
        self.redis_client.close()