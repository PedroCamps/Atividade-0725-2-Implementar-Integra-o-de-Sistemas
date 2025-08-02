import signal
import sys
import time
from infrastructure.redis_listener import RedisListener
from application.integration_router import IntegrationRouter


class IntegratorMain:
    def __init__(self):
        self.redis_listener = RedisListener()
        self.integration_router = IntegrationRouter()
        self.running = True
    
    def start(self):
        """Inicia o sistema integrador"""
        print("🚀 Sistema Integrador Python")
        print("🔧 Baseado nos padrões Enterprise Integration Patterns")
        print("📡 Conectando ao Redis...")
        
        # Configura o handler de mensagens
        self.redis_listener.set_message_handler(self.integration_router.route_message)
        
        # Configura handler para sinais do sistema
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            # Inicia o listener do Redis
            self.redis_listener.start()
            
            print("✅ Integrador iniciado com sucesso!")
            print("🔄 Aguardando eventos CRUD...")
            print("📖 Para parar, pressione Ctrl+C")
            
            # Loop principal
            while self.running:
                time.sleep(1)
                
        except Exception as e:
            print(f"❌ Erro ao iniciar integrador: {e}")
        finally:
            self._cleanup()
    
    def _signal_handler(self, signum, frame):
        """Handler para sinais do sistema"""
        print(f"\n🛑 Recebido sinal {signum}, parando integrador...")
        self.running = False
    
    def _cleanup(self):
        """Limpa recursos utilizados"""
        print("🧹 Limpando recursos...")
        
        if self.redis_listener:
            self.redis_listener.close()
        
        if self.integration_router:
            self.integration_router.close()
        
        print("✅ Integrador parado com sucesso")


def main():
    integrator = IntegratorMain()
    integrator.start()


if __name__ == "__main__":
    main()