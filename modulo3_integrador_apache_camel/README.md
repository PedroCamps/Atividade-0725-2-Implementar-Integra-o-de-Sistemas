# Módulo 3: Integrador Apache Camel

Sistema integrador implementado em Java com Apache Camel, seguindo os Enterprise Integration Patterns do tutorial original.

## 🎯 Visão Geral

Este módulo implementa o sistema integrador usando **Apache Camel** para demonstrar os padrões de integração corporativa em sua forma mais autêntica. O Apache Camel é a biblioteca de referência para EIP (Enterprise Integration Patterns) no ecossistema Java.

## 🏗️ Arquitetura Apache Camel

### Enterprise Integration Patterns Implementados

1. **Publisher-Subscriber Channel**
   - Redis Pub/Sub como canal de mensagens
   - `RedisListener` subscreve ao canal `crud-channel`

2. **Message Router** 
   - Camel Routes com DSL declarativa
   - Roteamento condicional baseado em conteúdo

3. **Message Translator**
   - Processadores específicos por entidade
   - Transformação `Estudante` → `Usuario`

4. **Canonical Data Model**
   - `EstudanteCanonico` como modelo intermediário
   - `EstudanteIdMapping` para correlação de IDs

### Fluxo Apache Camel

```java
from("direct:crud")
    .log("📥 Mensagem recebida: ${body}")
    .process(this::setOperationHeaders)      // Message Router
    .process(new CrudProcessor())            // Message Translator  
    .choice()                                // Content-Based Router
        .when(exchangeProperty("CamelSkipSendToEndpoint").isNotEqualTo(true))
            .toD("${header.targetEndpoint}") // Dynamic Router
            .filter().simple("${exchangeProperty.crudEntity.toLowerCase()} == 'estudante'")
                .process(new PersistenciaCanonicoProcessor()) // Canonical Data Model
        .otherwise()
            .log("⚠️ Mensagem ignorada")
```

## 📁 Estrutura do Projeto

```
src/main/java/br/ufg/inf/integrador/
├── Main.java                           # Aplicação principal
├── MainTest.java                       # Teste manual do fluxo
├── model/                              # Modelos de dados
│   ├── CrudOperation.java             # Operação CRUD do Redis
│   ├── EstudanteCanonico.java         # Modelo canônico
│   └── EstudanteIdMapping.java        # Mapeamento de IDs
├── processor/                          # Processadores Camel
│   ├── CrudProcessor.java             # Processador principal
│   ├── EstudanteProcessor.java        # Transformações específicas
│   └── PersistenciaCanonicoProcessor.java # Persistência canônica
├── redis/                             # Integração Redis
│   └── RedisListener.java             # Listener pub/sub
├── repository/                        # Persistência
│   ├── Database.java                  # Conexão SQLite
│   └── Repositorio.java               # Repository pattern
└── routes/                            # Rotas Camel
    └── CrudTransformRoute.java        # Rota principal de transformação
```

## 🚀 Execução

### Pré-requisitos

- Java 11+
- Maven 3.6+
- Redis Server rodando
- MongoDB rodando (para o Sistema de Biblioteca)

### Compilação

```bash
# Compilar o projeto
mvn clean compile

# Executar testes
mvn test

# Gerar JAR executável
mvn clean package
```

### Execução do Integrador

```bash
# Método 1: Via Maven
mvn exec:java -Dexec.mainClass="br.ufg.inf.integrador.Main"

# Método 2: Via JAR
java -jar target/integrador-apache-camel-1.0.0.jar

# Método 3: IDE
# Execute a classe br.ufg.inf.integrador.Main
```

### Teste Manual

```bash
# Publicar evento de teste no Redis
mvn exec:java -Dexec.mainClass="br.ufg.inf.integrador.MainTest"
```

## 🔧 Configuração

### Endpoints Configuráveis

Edite `CrudTransformRoute.java` para alterar URLs:

```java
private String mapEntityToEndpoint(String entity, CrudOperation.OperationType operation) {
    String baseUrl = "http://localhost:8080"; // ← Alterar se necessário
    // ...
}
```

### Redis Configuration

Edite `RedisListener.java` para alterar conexão:

```java
private static final String REDIS_URL = "redis://localhost:6379"; // ← Configurar
private static final String CRUD_CHANNEL = "crud-channel";         // ← Canal
```

### Database Configuration

Edite `PersistenciaCanonicoProcessor.java` para alterar banco:

```java
Database db = new Database("integrador.db"); // ← Nome do arquivo SQLite
```

## 🧪 Testes

### Testes Unitários

```bash
# Executar todos os testes
mvn test

# Executar teste específico
mvn test -Dtest=CrudEventsTest

# Executar com logs detalhados
mvn test -Dtest=RepositorioTest -Dorg.slf4j.simpleLogger.defaultLogLevel=DEBUG
```

### Teste de Integração E2E

1. **Iniciar Sistema de Biblioteca** (módulo2_odm):
```bash
cd ../modulo2_odm
python main.py
```

2. **Iniciar Integrador**:
```bash
mvn exec:java -Dexec.mainClass="br.ufg.inf.integrador.Main"
```

3. **Publicar Evento de Teste**:
```bash
mvn exec:java -Dexec.mainClass="br.ufg.inf.integrador.MainTest"
```

4. **Verificar Resultado**:
```bash
curl http://localhost:8080/usuarios
```

## 🔍 Logs e Debugging

### Configuração de Logs

O projeto usa SLF4J com implementação simples. Para logs mais verbosos:

```bash
# Executar com logs DEBUG
mvn exec:java -Dexec.mainClass="br.ufg.inf.integrador.Main" \
  -Dorg.slf4j.simpleLogger.defaultLogLevel=DEBUG

# Logs apenas de uma classe
mvn exec:java -Dexec.mainClass="br.ufg.inf.integrador.Main" \
  -Dorg.slf4j.simpleLogger.log.br.ufg.inf.integrador.processor=DEBUG
```

### Logs Esperados

**Inicialização:**
```
🚀 Sistema Integrador Apache Camel
🔧 Baseado nos padrões Enterprise Integration Patterns
✅ Contexto Apache Camel iniciado
🔗 Conectando ao Redis: redis://localhost:6379
✅ Subscrito ao canal: crud-channel (total: 1)
🟢 Escutando canal Redis: crud-channel
✅ Integrador iniciado com sucesso!
```

**Processamento de Evento:**
```
🔔 [crud-channel] {"entity":"Estudante","operation":"CREATE"...}
📥 Mensagem recebida: {"entity":"Estudante"...}
🎯 Headers configurados - Método: POST, Endpoint: http://localhost:8080/usuarios
✅ JSON processado: {"prenome":"João","sobrenome":"da Silva","situacao_matricula":"ATIVO"}
📤 Resposta HTTP: Status=201, Body={"id":"507f1f77bcf86cd799439011"...}
💾 Dados canônicos persistidos
```

## ⚡ Performance e Escalabilidade

### Apache Camel Benefits

- **Thread Management**: Camel gerencia pools de threads automaticamente
- **Error Handling**: Retry automático e dead letter queues
- **Monitoring**: JMX metrics out-of-the-box
- **Circuit Breaker**: Tolerância a falhas integrada

### Configurações de Performance

```java
// No CrudTransformRoute.java
from("direct:crud")
    .threads(10, 20)                    // Pool de threads
    .onException(Exception.class)
        .maximumRedeliveries(3)         // Retry automático
        .redeliveryDelay(1000)
        .handled(true)
    // ... resto da rota
```

## 🚀 Produção

### Docker

```dockerfile
FROM openjdk:11-jre-slim

COPY target/integrador-apache-camel-1.0.0.jar app.jar

ENV REDIS_URL=redis://redis:6379
ENV SB_API_URL=http://biblioteca-api:8080

ENTRYPOINT ["java", "-jar", "/app.jar"]
```

### Health Checks

```java
// Adicionar endpoint de health
from("timer://health?period=30000")
    .to("log:health?level=INFO")
    .setBody(constant("OK"));
```

### Monitoramento JMX

```bash
# Executar com JMX habilitado
java -Dcom.sun.management.jmxremote \
     -Dcom.sun.management.jmxremote.port=9999 \
     -Dcom.sun.management.jmxremote.authenticate=false \
     -Dcom.sun.management.jmxremote.ssl=false \
     -jar target/integrador-apache-camel-1.0.0.jar
```

## 🔗 Comparação com Versão Python

| Aspecto | Apache Camel (Java) | Python Nativo |
|---------|-------------------|---------------|
| **DSL** | Declarativa, fluente | Imperativa, orientada a objetos |
| **Error Handling** | Automático com retry | Manual com try/catch |
| **Monitoring** | JMX integrado | Logs customizados |
| **Performance** | JVM otimizada | Interpretado |
| **Ecosystem** | 300+ componentes | Bibliotecas específicas |
| **Learning Curve** | EIP patterns | Python patterns |

## 📚 Referências

- [Apache Camel Documentation](https://camel.apache.org/manual/)
- [Enterprise Integration Patterns](https://www.enterpriseintegrationpatterns.com/)
- [Camel in Action](https://www.manning.com/books/camel-in-action-second-edition)
- [Tutorial Original Integrador Redis II](../README.md)