# Documentação da API

## Sistema de Biblioteca (SB) - API REST

O Sistema de Biblioteca expõe uma API REST usando FastAPI que serve como endpoint de destino para o integrador.

### Base URL
```
http://localhost:8080
```

### Documentação Interativa
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

---

## Endpoints de Usuários

### POST /usuarios
Cria um novo usuário no sistema de biblioteca.

**Request Body:**
```json
{
  "prenome": "string",
  "sobrenome": "string", 
  "situacao_matricula": "string"
}
```

**Response (201 Created):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "prenome": "João",
  "sobrenome": "Silva",
  "situacao_matricula": "ATIVO"
}
```

**Exemplo com curl:**
```bash
curl -X POST "http://localhost:8080/usuarios" \
  -H "Content-Type: application/json" \
  -d '{"prenome": "João", "sobrenome": "Silva", "situacao_matricula": "ATIVO"}'
```

### GET /usuarios
Lista todos os usuários cadastrados.

**Response (200 OK):**
```json
[
  {
    "id": "507f1f77bcf86cd799439011",
    "prenome": "João",
    "sobrenome": "Silva", 
    "situacao_matricula": "ATIVO"
  }
]
```

### GET /usuarios/{usuario_id}
Obtém um usuário específico por ID.

**Path Parameters:**
- `usuario_id`: ID do usuário (MongoDB ObjectId)

**Response (200 OK):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "prenome": "João",
  "sobrenome": "Silva",
  "situacao_matricula": "ATIVO"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Usuário não encontrado"
}
```

### PUT /usuarios/{usuario_id}
Atualiza um usuário existente.

**Path Parameters:**
- `usuario_id`: ID do usuário

**Request Body:**
```json
{
  "prenome": "João Carlos",
  "sobrenome": "Silva Santos",
  "situacao_matricula": "INATIVO"
}
```

**Response (200 OK):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "prenome": "João Carlos",
  "sobrenome": "Silva Santos",
  "situacao_matricula": "INATIVO"
}
```

### DELETE /usuarios/{usuario_id}
Remove um usuário do sistema.

**Path Parameters:**
- `usuario_id`: ID do usuário

**Response (200 OK):**
```json
{
  "message": "Usuário deletado com sucesso"
}
```

---

## Endpoints de Obras

### POST /obras
Cria uma nova obra na biblioteca.

**Request Body:**
```json
{
  "codigo": "string",
  "titulo_principal": "string",
  "autor_principal": "string", 
  "isbn": "string"
}
```

**Response (201 Created):**
```json
{
  "id": "507f1f77bcf86cd799439012",
  "codigo": "LIV001",
  "titulo_principal": "Clean Architecture",
  "autor_principal": "Robert Martin",
  "isbn": "978-0134494165"
}
```

### GET /obras
Lista todas as obras disponíveis.

**Response (200 OK):**
```json
[
  {
    "id": "507f1f77bcf86cd799439012",
    "codigo": "LIV001", 
    "titulo_principal": "Clean Architecture",
    "autor_principal": "Robert Martin",
    "isbn": "978-0134494165"
  }
]
```

---

## Endpoint de Saúde

### GET /health
Verifica o status da aplicação e conectividade com MongoDB.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

**Response (500 Internal Server Error) - quando MongoDB está inacessível:**
```json
{
  "status": "unhealthy", 
  "database": "disconnected"
}
```

---

## Códigos de Status HTTP

| Código | Descrição |
|--------|-----------|
| 200 | OK - Operação bem-sucedida |
| 201 | Created - Recurso criado com sucesso |
| 400 | Bad Request - Dados inválidos |
| 404 | Not Found - Recurso não encontrado |
| 500 | Internal Server Error - Erro interno |

---

## Formato de Erros

Todos os endpoints retornam erros no formato padrão FastAPI:

```json
{
  "detail": "Descrição do erro"
}
```

**Exemplos de erros comuns:**

- **400 Bad Request**: Dados inválidos no request body
- **404 Not Found**: ID não encontrado na base de dados
- **500 Internal Server Error**: Falha de conectividade com MongoDB

---

## Integração com o Sistema

### Fluxo de Integração
1. **SGA** cria um estudante → Publica evento Redis
2. **Integrador** consome evento → Transforma dados
3. **Integrador** chama `POST /usuarios` → Cria usuário no SB
4. **SB** retorna dados do usuário criado
5. **Integrador** persiste dados canônicos + mapeamento de IDs

### Headers Requeridos
O integrador sempre envia:
```
Content-Type: application/json
```

### Mapeamento de Campos

| Campo SGA (Estudante) | Campo SB (Usuario) | Transformação |
|-----------------------|-------------------|---------------|
| `nome_completo` | `prenome` + `sobrenome` | Split no primeiro espaço |
| `status_emprestimo_livros` | `situacao_matricula` | "QUITADO" → "ATIVO" |
| `id` (int) | `id` (ObjectId string) | Gerado pelo MongoDB |

### Exemplo de Transformação
**Entrada (SGA):**
```json
{
  "id": 1,
  "nome_completo": "João da Silva",
  "data_de_nascimento": "01/01/2000",
  "matricula": 123456,
  "status_emprestimo_livros": "QUITADO"
}
```

**Saída (SB):**
```json
{
  "prenome": "João",
  "sobrenome": "da Silva", 
  "situacao_matricula": "ATIVO"
}
```

---

## Monitoramento

### Logs da Aplicação
A API gera logs estruturados para:
- Requisições HTTP recebidas
- Operações CRUD realizadas
- Eventos Redis publicados (quando habilitado)
- Erros e exceções

### Métricas Disponíveis
- Total de usuários cadastrados: `GET /usuarios` (count)
- Total de obras cadastradas: `GET /obras` (count)
- Status da aplicação: `GET /health`

### Health Check
Para monitoramento automatizado:
```bash
curl -f http://localhost:8080/health || exit 1
```