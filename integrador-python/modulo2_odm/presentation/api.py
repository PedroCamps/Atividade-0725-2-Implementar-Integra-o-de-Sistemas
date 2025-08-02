from fastapi import FastAPI, HTTPException
from typing import List

from ..infrastructure.database import MongoDB
from ..application.repository import UsuarioRepository, ObraRepository, RegistroEmprestimoRepository
from ..domain.entities import Usuario, Obra, RegistroEmprestimo

app = FastAPI(title="Sistema de Biblioteca (SB)", version="1.0.0")

# Inicializa o banco de dados
mongodb = MongoDB()
usuario_repo = UsuarioRepository(mongodb)
obra_repo = ObraRepository(mongodb)
registro_repo = RegistroEmprestimoRepository(mongodb)


@app.get("/")
async def root():
    return {"message": "Sistema de Biblioteca (SB) - API REST"}


# Endpoints para Usuários
@app.post("/usuarios", response_model=dict)
async def criar_usuario(usuario_data: dict):
    """Cria um novo usuário"""
    try:
        usuario = Usuario(
            prenome=usuario_data.get("prenome", ""),
            sobrenome=usuario_data.get("sobrenome", ""),
            situacao_matricula=usuario_data.get("situacao_matricula", "ATIVO")
        )
        
        usuario_criado = usuario_repo.create(usuario)
        return {
            "id": usuario_criado.id,
            "prenome": usuario_criado.prenome,
            "sobrenome": usuario_criado.sobrenome,
            "situacao_matricula": usuario_criado.situacao_matricula
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/usuarios", response_model=List[dict])
async def listar_usuarios():
    """Lista todos os usuários"""
    try:
        usuarios = usuario_repo.find_all()
        return [
            {
                "id": u.id,
                "prenome": u.prenome,
                "sobrenome": u.sobrenome,
                "situacao_matricula": u.situacao_matricula
            }
            for u in usuarios
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/usuarios/{usuario_id}", response_model=dict)
async def obter_usuario(usuario_id: str):
    """Obtém um usuário por ID"""
    try:
        usuario = usuario_repo.find_by_id(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        return {
            "id": usuario.id,
            "prenome": usuario.prenome,
            "sobrenome": usuario.sobrenome,
            "situacao_matricula": usuario.situacao_matricula
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/usuarios/{usuario_id}", response_model=dict)
async def atualizar_usuario(usuario_id: str, usuario_data: dict):
    """Atualiza um usuário existente"""
    try:
        usuario = usuario_repo.find_by_id(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        usuario.prenome = usuario_data.get("prenome", usuario.prenome)
        usuario.sobrenome = usuario_data.get("sobrenome", usuario.sobrenome)
        usuario.situacao_matricula = usuario_data.get("situacao_matricula", usuario.situacao_matricula)
        
        usuario_atualizado = usuario_repo.update(usuario)
        return {
            "id": usuario_atualizado.id,
            "prenome": usuario_atualizado.prenome,
            "sobrenome": usuario_atualizado.sobrenome,
            "situacao_matricula": usuario_atualizado.situacao_matricula
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/usuarios/{usuario_id}")
async def deletar_usuario(usuario_id: str):
    """Deleta um usuário"""
    try:
        usuario = usuario_repo.find_by_id(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        usuario_repo.delete(usuario)
        return {"message": "Usuário deletado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoints para Obras
@app.post("/obras", response_model=dict)
async def criar_obra(obra_data: dict):
    """Cria uma nova obra"""
    try:
        obra = Obra(
            codigo=obra_data.get("codigo", ""),
            titulo_principal=obra_data.get("titulo_principal", ""),
            autor_principal=obra_data.get("autor_principal", ""),
            isbn=obra_data.get("isbn", "")
        )
        
        obra_criada = obra_repo.create(obra)
        return {
            "id": obra_criada.id,
            "codigo": obra_criada.codigo,
            "titulo_principal": obra_criada.titulo_principal,
            "autor_principal": obra_criada.autor_principal,
            "isbn": obra_criada.isbn
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/obras", response_model=List[dict])
async def listar_obras():
    """Lista todas as obras"""
    try:
        obras = obra_repo.find_all()
        return [
            {
                "id": o.id,
                "codigo": o.codigo,
                "titulo_principal": o.titulo_principal,
                "autor_principal": o.autor_principal,
                "isbn": o.isbn
            }
            for o in obras
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Health check
@app.get("/health")
async def health_check():
    """Verifica o status da aplicação"""
    try:
        db_status = mongodb.ping()
        return {
            "status": "healthy" if db_status else "unhealthy",
            "database": "connected" if db_status else "disconnected"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))