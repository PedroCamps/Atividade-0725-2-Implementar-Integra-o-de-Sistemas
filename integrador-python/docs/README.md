# Integrador Python: Sistema de Integração entre Camadas de Persistência

## Visão Geral

Este projeto implementa um sistema de integração entre diferentes camadas de persistência utilizando padrões Enterprise Integration Patterns (EIP), baseado no tutorial **Integrador Redis II** original em Java. A implementação em Python mantém os mesmos princípios arquiteturais e padrões de integração, adaptando-os para o ecossistema Python.

## Arquitetura

O sistema é composto por três módulos principais que seguem os princípios da Clean Architecture:

### Módulo 1: Sistema de Gestão Acadêmica (SGA) - ORM/SQLite
- **Tecnologia**: SQLAlchemy + SQLite
- **Responsabilidade**: Gerenciamento de entidades acadêmicas (Estudantes, Disciplinas, Turmas, Matrículas)
- **Padrão**: ORM (Object-Relational Mapping)

### Módulo 2: Sistema de Biblioteca (SB) - ODM/MongoDB  
- **Tecnologia**: PyMongo + FastAPI
- **Responsabilidade**: Gerenciamento de usuários, obras e empréstimos
- **Padrão**: ODM (Object-Document Mapping)

### Módulo 3: Sistema Integrador
- **Tecnologia**: Redis + Requests
- **Responsabilidade**: Integração entre SGA e SB usando padrões EIP
- **Padrões**: Message Router, Message Translator, Canonical Data Model

## Enterprise Integration Patterns Implementados

### 1. Publisher-Subscriber Channel
- **Redis** atua como canal de mensagens pub/sub
- Sistemas SGA e SB publicam eventos CRUD automaticamente
- Integrador subscreve e processa eventos em tempo real

### 2. Message Router
- Direciona mensagens para processadores específicos baseado na entidade e operação
- Implementado na classe `IntegrationRouter`

### 3. Message Translator
- Transforma dados entre formatos SGA (ORM) e SB (ODM)
- Implementado na classe `EstudanteProcessor`

### 4. Canonical Data Model
- Modelo universal intermediário (`EstudanteCanonico`)
- Mapeamento de IDs entre sistemas (`EstudanteIdMapping`)
- Identificador canônico baseado em UUID

## Estrutura do Projeto

```
integrador-python/
├── modulo1_orm/                 # Sistema SGA (ORM/SQLite)
│   ├── domain/
│   │   └── entities.py         # Entidades de domínio
│   ├── infrastructure/
│   │   ├── models.py           # Modelos SQLAlchemy
│   │   └── redis_publisher.py  # Publicador Redis
│   └── application/
│       └── repository.py       # Repositórios genéricos
├── modulo2_odm/                 # Sistema SB (ODM/MongoDB)
│   ├── domain/
│   │   └── entities.py         # Entidades de domínio
│   ├── infrastructure/
│   │   ├── database.py         # Conexão MongoDB
│   │   └── redis_publisher.py  # Publicador Redis
│   ├── application/
│   │   └── repository.py       # Repositórios MongoDB
│   └── presentation/
│       └── api.py              # API REST FastAPI
├── modulo3_integrador/          # Sistema Integrador
│   ├── domain/
│   │   └── canonical_model.py  # Modelo canônico
│   ├── infrastructure/
│   │   ├── models.py           # Modelos persistência canônica
│   │   └── redis_listener.py   # Listener Redis
│   └── application/
│       ├── processors.py       # Processadores de transformação
│       └── integration_router.py # Roteador principal
└── docs/                        # Documentação
    ├── README.md               # Este arquivo
    ├── ARCHITECTURE.md         # Decisões arquiteturais
    ├── API.md                  # Documentação da API
    └── SETUP.md                # Configuração e instalação
```

## Quick Start

### Pré-requisitos
- Python 3.9+
- Redis Server
- MongoDB
- SQLite

### Instalação

1. **Clone o repositório**
```bash
git clone <repository-url>
cd integrador-python
```

2. **Configure cada módulo**
```bash
# Módulo 1 (SGA)
cd modulo1_orm
pip install -r requirements.txt

# Módulo 2 (SB)  
cd ../modulo2_odm
pip install -r requirements.txt

# Módulo 3 (Integrador)
cd ../modulo3_integrador
pip install -r requirements.txt
```

3. **Inicie os serviços**
```bash
# Terminal 1: Redis
redis-server

# Terminal 2: MongoDB
mongod

# Terminal 3: Sistema de Biblioteca (SB)
cd modulo2_odm
python main.py

# Terminal 4: Sistema Integrador
cd modulo3_integrador  
python main.py
```

4. **Teste a integração**
```bash
# Terminal 5: Teste manual
cd modulo3_integrador
python test_manual.py
```

## Fluxo de Integração

1. **Evento CRUD**: SGA cria um estudante
2. **Publicação**: Evento é publicado no Redis (canal `crud-channel`)
3. **Consumo**: Integrador recebe e processa o evento
4. **Transformação**: Dados são transformados de `Estudante` para `Usuario`
5. **Roteamento**: Requisição HTTP é enviada para API do SB
6. **Persistência**: Dados canônicos e mapeamento de IDs são persistidos

## Testes

### Testes Unitários
```bash
# Módulo 1
cd modulo1_orm
python -m pytest test_repository.py

# Módulo 2  
cd modulo2_odm
python -m pytest test_repository.py

# Módulo 3
cd modulo3_integrador
python -m pytest test_integration.py
```

### Teste de Integração E2E
```bash
cd modulo3_integrador
python test_manual.py
```

## Características Técnicas

### Clean Architecture
- **Separação de responsabilidades** por camadas (Domain, Application, Infrastructure, Presentation)
- **Inversão de dependências** através de interfaces abstratas
- **Independência de frameworks** no núcleo de negócio

### Padrões de Design
- **Repository Pattern**: Abstração da camada de persistência
- **Publisher-Observer**: Para eventos CRUD assíncronos  
- **Strategy Pattern**: Processadores específicos por entidade
- **Template Method**: Processamento genérico de mensagens

### Escalabilidade
- **Processamento assíncrono** via Redis pub/sub
- **Múltiplas instâncias** do integrador podem executar em paralelo
- **Tolerância a falhas** com retry automático
- **Monitoramento** através de logs estruturados

## Próximos Passos

Para expandir o sistema, considere:

1. **Novas entidades**: Suporte a Professor, Disciplina, etc.
2. **Sincronização bidirecional**: SB → SGA
3. **Tratamento de conflitos**: Resolução de inconsistências
4. **Métricas**: Monitoring com Prometheus/Grafana
5. **Message queues**: Migração para Apache Kafka ou RabbitMQ

## Referências

- [Enterprise Integration Patterns](https://www.enterpriseintegrationpatterns.com/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Tutorial Original Java](../integrador-redis2/README.md)