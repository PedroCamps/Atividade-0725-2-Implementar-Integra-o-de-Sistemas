# Guia de Configuração e Instalação

## Pré-requisitos

### Software Necessário
- **Python 3.9+** - Linguagem principal
- **Redis Server** - Message broker para pub/sub
- **MongoDB** - Base de dados documental para SB
- **SQLite** - Incluído com Python (para SGA e dados canônicos)
- **Git** - Para clonagem do repositório

### Verificação do Ambiente
```bash
# Verificar versões
python --version          # Deve ser 3.9+
redis-cli --version       # Deve estar instalado
mongod --version          # Deve estar instalado

# Testar conectividade
redis-cli ping            # Deve retornar PONG
mongo --eval "db.version()"  # Deve mostrar versão MongoDB
```

---

## Instalação dos Serviços

### Redis (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Testar
redis-cli ping
```

### Redis (macOS)
```bash
brew install redis
brew services start redis

# Testar
redis-cli ping
```

### MongoDB (Ubuntu/Debian)
```bash
# Importar chave pública
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -

# Adicionar repositório
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

# Instalar
sudo apt update
sudo apt install mongodb-org

# Iniciar
sudo systemctl start mongod
sudo systemctl enable mongod

# Testar
mongo --eval "db.version()"
```

### MongoDB (macOS)
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community

# Testar
mongo --eval "db.version()"
```

---

## Configuração do Projeto

### 1. Clonagem e Estrutura
```bash
# Clonar repositório
git clone <repository-url>
cd integrador-python

# Verificar estrutura
tree -L 2
```

### 2. Configuração Módulo 1 (SGA - ORM)
```bash
cd modulo1_orm

# Criar ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Testar instalação
python -c "import sqlalchemy, redis; print('✅ Dependências OK')"
```

### 3. Configuração Módulo 2 (SB - ODM)
```bash
cd ../modulo2_odm

# Ambiente virtual (se não usando global)
python -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Testar instalação
python -c "import pymongo, fastapi; print('✅ Dependências OK')"
```

### 4. Configuração Módulo 3 (Integrador)
```bash
cd ../modulo3_integrador

# Ambiente virtual (se não usando global)
python -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Testar instalação
python -c "import redis, requests; print('✅ Dependências OK')"
```

---

## Configuração de Ambiente

### Variáveis de Ambiente (Opcional)

Crie arquivo `.env` na raiz de cada módulo:

**modulo1_orm/.env:**
```env
REDIS_URL=redis://localhost:6379
DATABASE_URL=sqlite:///sga.db
CRUD_PUBLISHING_ENABLED=true
```

**modulo2_odm/.env:**
```env
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=biblioteca
REDIS_URL=redis://localhost:6379
API_HOST=0.0.0.0
API_PORT=8080
```

**modulo3_integrador/.env:**
```env
REDIS_URL=redis://localhost:6379
REDIS_CHANNEL=crud-channel
INTEGRATOR_DB=integrador.db
SB_API_BASE_URL=http://localhost:8080
```

### Configuração Redis

**redis.conf** (opcional, para ajustes):
```ini
# Configurações básicas para desenvolvimento
port 6379
bind 127.0.0.1
maxmemory 256mb
maxmemory-policy allkeys-lru
```

### Configuração MongoDB

**mongod.conf** (opcional):
```yaml
systemLog:
  destination: file
  path: /var/log/mongodb/mongod.log
  logAppend: true
storage:
  dbPath: /var/lib/mongodb
  journal:
    enabled: true
net:
  port: 27017
  bindIp: 127.0.0.1
```

---

## Verificação da Instalação

### Testes Unitários

**Módulo 1 (SGA):**
```bash
cd modulo1_orm
python -m unittest test_repository.py -v
```

**Módulo 2 (SB):**
```bash
cd modulo2_odm
python -m unittest test_repository.py -v
```

**Módulo 3 (Integrador):**
```bash
cd modulo3_integrador
python -m unittest test_integration.py -v
```

### Teste de Conectividade

**Script de verificação completa:**
```bash
# salvar como check_setup.py
import redis
import pymongo
import sqlite3
from sqlalchemy import create_engine

def check_redis():
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("✅ Redis: Conectado")
        return True
    except Exception as e:
        print(f"❌ Redis: Erro - {e}")
        return False

def check_mongodb():
    try:
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        client.admin.command('ping')
        print("✅ MongoDB: Conectado")
        return True
    except Exception as e:
        print(f"❌ MongoDB: Erro - {e}")
        return False

def check_sqlite():
    try:
        engine = create_engine('sqlite:///test.db')
        with engine.connect() as conn:
            conn.execute('SELECT 1')
        print("✅ SQLite: Funcionando")
        return True
    except Exception as e:
        print(f"❌ SQLite: Erro - {e}")
        return False

if __name__ == "__main__":
    print("🔍 Verificando conectividade...")
    redis_ok = check_redis()
    mongo_ok = check_mongodb()
    sqlite_ok = check_sqlite()
    
    if all([redis_ok, mongo_ok, sqlite_ok]):
        print("\n🎉 Todos os serviços estão funcionando!")
    else:
        print("\n⚠️ Alguns serviços precisam de atenção")
```

```bash
python check_setup.py
```

---

## Execução do Sistema

### Ordem de Inicialização

1. **Serviços Base** (em terminais separados):
```bash
# Terminal 1: Redis
redis-server

# Terminal 2: MongoDB  
mongod
```

2. **Sistema de Biblioteca** (SB):
```bash
# Terminal 3
cd modulo2_odm
python main.py
```

3. **Sistema Integrador**:
```bash
# Terminal 4
cd modulo3_integrador
python main.py
```

4. **Teste Manual**:
```bash
# Terminal 5
cd modulo3_integrador
python test_manual.py
```

### Verificação da Execução

**Logs esperados:**

**SB (Terminal 3):**
```
🚀 Sistema de Biblioteca (SB) - Módulo ODM
📚 Servidor FastAPI iniciando...
🌐 Acesse: http://localhost:8080
📖 Documentação: http://localhost:8080/docs
INFO: Uvicorn running on http://0.0.0.0:8080
```

**Integrador (Terminal 4):**
```
🚀 Sistema Integrador Python
🔧 Baseado nos padrões Enterprise Integration Patterns
📡 Conectando ao Redis...
🟢 Escutando canal Redis: crud-channel
✅ Integrador iniciado com sucesso!
🔄 Aguardando eventos CRUD...
```

**Teste Manual (Terminal 5):**
```
🧪 Teste Manual do Integrador - Criação de Estudante
📝 Este teste irá criar um estudante no SGA e publicar evento no Redis
🔍 Criando entidade: Estudante(id=None, nome_completo='João da Silva', ...)
✅ Entidade criada: Estudante(id=1, ...)
✅ Evento publicado: Estudante - CREATE
📡 Evento CRUD publicado no Redis
```

---

## Troubleshooting

### Problemas Comuns

**1. Redis Connection Refused**
```bash
# Verificar se Redis está rodando
sudo systemctl status redis-server

# Tentar iniciar
sudo systemctl start redis-server

# Verificar porta
netstat -tlnp | grep :6379
```

**2. MongoDB Connection Failed**
```bash
# Verificar se MongoDB está rodando
sudo systemctl status mongod

# Tentar iniciar
sudo systemctl start mongod

# Verificar logs
sudo tail -f /var/log/mongodb/mongod.log
```

**3. Python Module Not Found**
```bash
# Verificar se está no ambiente virtual correto
which python
pip list

# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

**4. Port Already in Use**
```bash
# Encontrar processo usando porta 8080
sudo lsof -i :8080

# Parar processo se necessário
sudo kill -9 <PID>
```

**5. Permission Denied (SQLite)**
```bash
# Verificar permissões do diretório
ls -la *.db

# Corrigir permissões se necessário
chmod 644 *.db
```

### Logs de Debug

Para logs mais verbosos, modifique temporariamente:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Reset do Ambiente

Para recomeçar do zero:
```bash
# Parar todos os serviços
pkill -f "python main.py"
sudo systemctl stop redis-server mongod

# Limpar dados
rm -f *.db
mongo --eval "db.dropDatabase()" biblioteca

# Reiniciar serviços
sudo systemctl start redis-server mongod
```

---

## Configuração para Produção

### Considerações de Segurança

1. **Redis Authentication:**
```
requirepass sua_senha_forte
```

2. **MongoDB Authentication:**
```javascript
use admin
db.createUser({
  user: "integrator",
  pwd: "senha_forte", 
  roles: ["readWrite"]
})
```

3. **HTTPS para API:**
```python
# No FastAPI
app.add_middleware(HTTPSRedirectMiddleware)
```

### Configuração de Ambiente
```env
# Production .env
REDIS_URL=redis://:password@redis-host:6379
MONGODB_URI=mongodb://user:pass@mongo-host:27017/
API_HOST=0.0.0.0
LOG_LEVEL=INFO
```

### Monitoramento
- Configurar logs estruturados (JSON)
- Implementar health checks
- Configurar alertas para falhas de conectividade
- Monitorar latência Redis e MongoDB