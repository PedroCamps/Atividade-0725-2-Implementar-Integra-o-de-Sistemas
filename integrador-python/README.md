# Integrador Python: Integração entre Camadas de Persistência

Sistema de integração baseado em Enterprise Integration Patterns (EIP) implementado em Python, inspirado no tutorial **Integrador Redis II** original em Java.

## 🎯 Visão Geral

Este projeto demonstra como integrar sistemas com diferentes paradigmas de persistência (ORM/SQLite e ODM/MongoDB) usando padrões de integração corporativa, com foco em:

- **Clean Architecture** com separação clara de responsabilidades
- **Enterprise Integration Patterns** (Message Router, Message Translator, Canonical Data Model)
- **Publisher-Subscriber** com Redis como canal de mensagens
- **Transformação de dados** entre formatos relacionais e documentais
- **Modelo canônico** para desacoplamento entre sistemas

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Módulo 1      │    │   Módulo 3      │    │   Módulo 2      │
│   SGA (ORM)     │◄──►│   Integrador    │◄──►│   SB (ODM)      │
│                 │    │                 │    │                 │
│ SQLAlchemy      │    │ Redis Listener  │    │ PyMongo         │
│ SQLite          │    │ Message Router  │    │ MongoDB         │
│ Redis Publisher │    │ Data Transform  │    │ FastAPI         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
                           ┌─────────────┐
                           │    Redis    │
                           │   Pub/Sub   │
                           └─────────────┘
```

## 🚀 Quick Start

### Pré-requisitos
- Python 3.9+
- Redis Server
- MongoDB
- SQLite (incluído no Python)

### Instalação Rápida

```bash
# 1. Clone o repositório
git clone <repository-url>
cd integrador-python

# 2. Instale dependências de cada módulo
cd modulo1_orm && pip install -r requirements.txt && cd ..
cd modulo2_odm && pip install -r requirements.txt && cd ..
cd modulo3_integrador && pip install -r requirements.txt && cd ..

# 3. Inicie serviços (terminais separados)
redis-server                    # Terminal 1
mongod                         # Terminal 2

# 4. Execute o sistema (terminais separados)
cd modulo2_odm && python main.py                # Terminal 3: API SB
cd modulo3_integrador && python main.py         # Terminal 4: Integrador

# 5. Teste a integração
cd modulo3_integrador && python test_manual.py # Terminal 5: Teste
```

### Verificação Rápida

```bash
# Executar todos os testes
python run_tests.py

# Exemplo de transformação de dados
python examples/example_data_transformation.py

# Teste da API
python examples/example_api_testing.py
```

## 📁 Estrutura do Projeto

```
integrador-python/
├── modulo1_orm/                 # Sistema SGA (ORM/SQLite)
│   ├── domain/entities.py      # Entidades de negócio
│   ├── infrastructure/         # Modelos SQLAlchemy + Redis
│   ├── application/repository.py # Repositórios CRUD
│   └── main.py                 # Ponto de entrada
├── modulo2_odm/                 # Sistema SB (ODM/MongoDB)
│   ├── domain/entities.py      # Entidades de negócio  
│   ├── infrastructure/         # MongoDB + Redis
│   ├── application/repository.py # Repositórios MongoDB
│   ├── presentation/api.py     # API REST FastAPI
│   └── main.py                 # Servidor web
├── modulo3_integrador/          # Sistema Integrador
│   ├── domain/canonical_model.py # Modelo canônico
│   ├── infrastructure/         # Redis listener + persistência
│   ├── application/             # Processadores + roteador
│   └── main.py                 # Integrador principal
├── examples/                    # Exemplos de uso
├── docs/                        # Documentação completa
└── run_tests.py                # Script de testes
```

## 🔧 Módulos

### Módulo 1: SGA (ORM/SQLite)
- **Tecnologia**: SQLAlchemy + SQLite + Redis
- **Entidades**: Estudante, Disciplina, Turma, Matrícula
- **Funcionalidade**: Publica eventos CRUD no Redis

### Módulo 2: SB (ODM/MongoDB)
- **Tecnologia**: PyMongo + MongoDB + FastAPI
- **Entidades**: Usuario, Obra, RegistroEmprestimo  
- **Funcionalidade**: API REST para receber dados integrados

### Módulo 3: Integrador
- **Tecnologia**: Redis + Requests + SQLAlchemy
- **Funcionalidade**: Consome eventos, transforma dados, chama APIs
- **Padrões**: Message Router, Message Translator, Canonical Data Model

## 🔄 Fluxo de Integração

1. **Evento CRUD**: SGA cria um estudante → Publica no Redis
2. **Consumo**: Integrador recebe evento do canal `crud-channel`
3. **Transformação**: `Estudante` (SGA) → `Usuario` (SB)
4. **Roteamento**: HTTP POST para API do SB
5. **Persistência**: Dados canônicos + mapeamento de IDs

**Exemplo de transformação:**
```python
# Entrada (SGA)
{
  "nome_completo": "João da Silva",
  "matricula": 123456,
  "status_emprestimo_livros": "QUITADO"
}

# Saída (SB)  
{
  "prenome": "João",
  "sobrenome": "da Silva",
  "situacao_matricula": "ATIVO"
}
```

## 📊 Enterprise Integration Patterns

### 1. Publisher-Subscriber Channel
```python
# Publicação automática em operações CRUD
def create(self, entity):
    # ... salvar entidade
    self.redis_publisher.publish_operation(
        CrudOperation("Estudante", "CREATE", "ORM", entity_json)
    )
```

### 2. Message Router
```python
# Roteamento baseado em entidade e operação
def route_message(self, channel, message):
    request_data = self.crud_processor.process(message)
    if request_data:
        response = self.http_processor.send_request(request_data)
```

### 3. Message Translator
```python
# Transformação entre formatos
def estudante_para_usuario(self, dados_json):
    dados = json.loads(dados_json)
    prenome, sobrenome = self.extrair_prenome_e_sobrenome(dados["nome_completo"])
    return json.dumps({"prenome": prenome, "sobrenome": sobrenome})
```

### 4. Canonical Data Model
```python
@dataclass
class EstudanteCanonico:
    id_canonico: str        # UUID universal
    prenome: str
    sobrenome: str
    nome_completo: str
    # ... outros campos normalizados
```

## 🧪 Testes

### Testes Unitários
```bash
# Todos os módulos
python run_tests.py

# Módulo específico
cd modulo1_orm && python -m unittest test_repository.py -v
cd modulo2_odm && python -m unittest test_repository.py -v  
cd modulo3_integrador && python -m unittest test_integration.py -v
```

### Testes de Integração
```bash
# Fluxo completo E2E
python examples/example_complete_flow.py

# Listener Redis independente
python examples/example_redis_listener.py

# Transformação de dados
python examples/example_data_transformation.py

# API testing
python examples/example_api_testing.py
```

## 📖 Documentação

- [**Setup Completo**](docs/SETUP.md) - Instalação e configuração detalhada
- [**Decisões Arquiteturais**](docs/ARCHITECTURE.md) - ADRs e justificativas técnicas
- [**Documentação da API**](docs/API.md) - Endpoints e exemplos de uso
- [**README Principal**](docs/README.md) - Documentação técnica completa

## 🔍 Monitoramento

### Logs Estruturados
O sistema gera logs detalhados para debugging:
```
🔔 [crud-channel] {"entity":"Estudante","operation":"CREATE",...}
📥 Mensagem recebida do canal crud-channel  
✅ JSON processado: {"prenome":"João","sobrenome":"Silva"}
📤 Enviando POST para http://localhost:8080/usuarios
📥 Resposta HTTP: Status=201, Body={"id":"507f..."}
✅ EstudanteCanonico persistido: a1b2c3d4-...
```

### APIs de Status
```bash
# Health check do SB
curl http://localhost:8080/health

# Listar usuários integrados
curl http://localhost:8080/usuarios

# Documentação interativa
open http://localhost:8080/docs
```

## 🛠️ Comandos Úteis

```bash
# Inicialização completa
./scripts/start_all.sh              # Se disponível

# Parar todos os serviços  
pkill -f "python main.py"
sudo systemctl stop redis-server mongod

# Reset completo
rm -f *.db && mongo --eval "db.dropDatabase()" biblioteca

# Debugging
python -c "import redis; print(redis.Redis().ping())"
python -c "import pymongo; print(pymongo.MongoClient().admin.command('ping'))"
```

## 🎯 Casos de Uso

### 1. Sincronização de Estudantes
Quando um estudante é criado no SGA, automaticamente vira usuário no SB.

### 2. Modelo Canônico
Mantém visão unificada de estudantes independente do sistema origem.

### 3. Rastreabilidade
Histórico completo de sincronizações via mapeamento de IDs.

### 4. Extensibilidade
Fácil adição de novos sistemas e entidades.

## 🚀 Próximos Passos

- [ ] Sincronização bidirecional (SB → SGA)
- [ ] Suporte a mais entidades (Professor, Disciplina)
- [ ] Message queues (Kafka/RabbitMQ)
- [ ] Monitoramento (Prometheus/Grafana)
- [ ] Containerização (Docker/Kubernetes)
- [ ] CI/CD pipeline

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto é licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- Tutorial original **Integrador Redis II** em Java
- [Enterprise Integration Patterns](https://www.enterpriseintegrationpatterns.com/) por Gregor Hohpe
- Comunidade Python por bibliotecas excepcionais