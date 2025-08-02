import uvicorn
from presentation.api import app


def main():
    print("🚀 Sistema de Biblioteca (SB) - Módulo ODM")
    print("📚 Servidor FastAPI iniciando...")
    print("🌐 Acesse: http://localhost:8080")
    print("📖 Documentação: http://localhost:8080/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main()