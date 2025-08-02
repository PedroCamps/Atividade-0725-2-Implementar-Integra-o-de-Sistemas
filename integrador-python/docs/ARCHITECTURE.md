# Decisões Arquiteturais (ADRs)

## ADR-001: Arquitetura Baseada em Enterprise Integration Patterns

**Status**: Aprovado  
**Data**: 2025-08-02  
**Contexto**: Necessidade de integrar sistemas com diferentes paradigmas de persistência (ORM/SQLite e ODM/MongoDB)

### Decisão
Adotar Enterprise Integration Patterns (EIP) como base arquitetural, especificamente:
- Publisher-Subscriber Channel (Redis)
- Message Router (routing condicional)  
- Message Translator (transformação de formatos)
- Canonical Data Model (modelo intermediário)

### Justificativa
- **Desacoplamento**: Sistemas não dependem diretamente uns dos outros
- **Escalabilidade**: Múltiplos consumidores podem processar eventos
- **Manutenibilidade**: Padrões bem documentados e testados
- **Extensibilidade**: Fácil adição de novos sistemas

### Consequências
- **Positivas**: Baixo acoplamento, alta coesão, arquitetura flexível
- **Negativas**: Complexidade adicional, latência de rede, eventual consistency

---

## ADR-002: Clean Architecture como Estrutura Base

**Status**: Aprovado  
**Data**: 2025-08-02  
**Contexto**: Necessidade de organizar código de forma sustentável e testável

### Decisão
Implementar Clean Architecture com separação clara de responsabilidades:
- **Domain**: Entidades e regras de negócio puras
- **Application**: Casos de uso e orquestração
- **Infrastructure**: Detalhes técnicos (DB, Redis, HTTP)
- **Presentation**: Controllers e APIs

### Justificativa
- **Testabilidade**: Núcleo independente de frameworks
- **Flexibilidade**: Fácil substituição de components externos
- **Clareza**: Responsabilidades bem definidas
- **Consistência**: Padrão aplicado em todos os módulos

### Consequências
- **Positivas**: Código mais testável e mantível
- **Negativas**: Estrutura inicial mais complexa

---

## ADR-003: Redis como Message Broker

**Status**: Aprovado  
**Data**: 2025-08-02  
**Contexto**: Necessidade de canal de comunicação assíncrona entre sistemas

### Decisão
Utilizar Redis Pub/Sub como canal de mensagens entre SGA, SB e Integrador.

### Alternativas Consideradas
1. **Apache Kafka**: Mais robusto, mas complexo para o escopo
2. **RabbitMQ**: Bom balanceamento, mas configuração adicional
3. **Direct HTTP**: Simples, mas forte acoplamento

### Justificativa
- **Simplicidade**: Configuração mínima
- **Performance**: Baixa latência para pub/sub
- **Aderência**: Mantém compatibilidade com tutorial original
- **Recursos**: Já disponível no ambiente de desenvolvimento

### Consequências
- **Positivas**: Setup rápido, performance adequada
- **Negativas**: Menos garantias de entrega que message queues dedicadas

---

## ADR-004: Modelo Canônico com Identificadores UUID

**Status**: Aprovado  
**Data**: 2025-08-02  
**Contexto**: Necessidade de correlacionar entidades entre sistemas com diferentes esquemas de ID

### Decisão
Implementar Canonical Data Model com:
- `id_canonico`: UUID4 como identificador universal
- `EstudanteIdMapping`: Tabela de correlação entre IDs dos sistemas
- Persistência em SQLite para dados canônicos

### Justificativa
- **Idempotência**: Evita processamento duplicado
- **Rastreabilidade**: Histórico completo de sincronizações
- **Extensibilidade**: Fácil adição de novos sistemas
- **Desacoplamento**: IDs independentes entre sistemas

### Consequências
- **Positivas**: Integração robusta e auditável
- **Negativas**: Overhead de storage e mapeamento

---

## ADR-005: FastAPI para Sistema de Biblioteca

**Status**: Aprovado  
**Data**: 2025-08-02  
**Contexto**: Necessidade de API REST para receber dados do integrador

### Decisão
Utilizar FastAPI como framework web para o Sistema de Biblioteca (SB).

### Alternativas Consideradas
1. **Flask**: Mais simples, mas menos features automáticas
2. **Django**: Mais completo, mas overhead desnecessário
3. **Tornado**: Assíncrono, mas API menos moderna

### Justificativa
- **Performance**: Assíncrono por padrão
- **Documentação**: OpenAPI automática
- **Type Hints**: Validação automática com Pydantic
- **Modernidade**: Padrões atuais do Python

### Consequências
- **Positivas**: API bem documentada e performante
- **Negativas**: Dependência adicional

---

## ADR-006: SQLAlchemy ORM + PyMongo ODM

**Status**: Aprovado  
**Data**: 2025-08-02  
**Contexto**: Demonstrar integração entre paradigmas relacionais e documentais

### Decisão
- **SGA**: SQLAlchemy + SQLite (paradigma relacional)
- **SB**: PyMongo + MongoDB (paradigma documental)
- **Integrador**: SQLAlchemy para dados canônicos

### Justificativa
- **Representatividade**: Mostra integração real entre paradigmas
- **Simplicidade**: Libraries maduras e estáveis
- **Compatibilidade**: Mantém essência do tutorial original
- **Aprendizado**: Demonstra diferenças práticas entre ORM e ODM

### Consequências
- **Positivas**: Exemplo realístico de integração
- **Negativas**: Múltiplas dependências de persistência

---

## ADR-007: Repository Pattern Genérico

**Status**: Aprovado  
**Data**: 2025-08-02  
**Contexto**: Necessidade de abstração consistente da camada de persistência

### Decisão
Implementar Repository Pattern genérico usando Python Generics:
- `Repository[T, M]` para ORM (entidade, modelo)
- `MongoRepository[T]` para ODM (entidade)

### Justificativa
- **Reutilização**: Código comum para todas as entidades
- **Consistência**: Interface uniforme para persistência
- **Type Safety**: Generics garantem tipagem correta
- **Extensibilidade**: Fácil adição de novas entidades

### Consequências
- **Positivas**: Menos duplicação de código
- **Negativas**: Abstração pode ocultar detalhes específicos

---

## ADR-008: Testes Unitários com Unittest + Mocks

**Status**: Aprovado  
**Data**: 2025-08-02  
**Contexto**: Necessidade de validar componentes isoladamente

### Decisão
Utilizar unittest (built-in) + unittest.mock para testes unitários.

### Alternativas Consideradas
1. **pytest**: Mais moderno, mas dependência externa
2. **nose2**: Compatível, mas menos suporte

### Justificativa
- **Zero Dependencies**: Biblioteca padrão do Python
- **Mocking Integrado**: unittest.mock para isolamento
- **Compatibilidade**: Funciona em qualquer ambiente Python
- **Simplicidade**: API familiar e documentada

### Consequências
- **Positivas**: Sem dependências externas para testes
- **Negativas**: API mais verbosa que pytest

---

## ADR-009: Logging Estruturado com Prints

**Status**: Aprovado (Temporário)  
**Data**: 2025-08-02  
**Contexto**: Necessidade de observabilidade durante desenvolvimento

### Decisão
Utilizar prints estruturados com emojis para logging inicial.

### Justificativa
- **Simplicidade**: Zero configuração
- **Visibilidade**: Emojis facilitam identificação visual
- **Compatibilidade**: Funciona em qualquer terminal
- **Prototipagem**: Adequado para fase de desenvolvimento

### Evolução Planejada
Migrar para logging estruturado (JSON) em produção com:
- Python logging module
- Correlation IDs
- Structured data (JSON)
- Integration com Prometheus/Grafana

### Consequências
- **Positivas**: Feedback imediato durante desenvolvimento
- **Negativas**: Não adequado para produção

---

## ADR-010: Tratamento de Erros Defensivo

**Status**: Aprovado  
**Data**: 2025-08-02  
**Contexto**: Sistema de integração deve ser resiliente a falhas

### Decisão
Implementar tratamento defensivo de erros:
- Try/catch em todos os pontos de integração
- Graceful degradation (não para o sistema)
- Logging detalhado de erros
- Continuidade do processamento

### Justificativa
- **Resiliência**: Sistema continua funcionando com falhas parciais
- **Observabilidade**: Erros são logados mas não param o fluxo
- **Manutenibilidade**: Fácil identificação de problemas
- **Produção**: Comportamento adequado para ambiente real

### Consequências
- **Positivas**: Sistema mais robusto
- **Negativas**: Possível mascaramento de erros críticos