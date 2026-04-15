from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, Usuario
from fastapi.middleware.cors import CORSMiddleware
import requests
import re

Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def limpar_doc(doc: str):
    return re.sub(r'\D', '', doc)

def validar_cpf_cnpj(doc: str):
    doc = limpar_doc(doc)
    return len(doc) in [11, 14]

def consultar_cpf_cnpj(doc: str):
    try:
        url = f"https://brasilapi.com.br/api/cnpj/v1/{doc}"
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/usuarios")
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuario).all()

@app.post("/usuarios")
def criar_usuario(nome: str, cpf_cnpj: str, db: Session = Depends(get_db)):

    cpf_cnpj = limpar_doc(cpf_cnpj)

    if not validar_cpf_cnpj(cpf_cnpj):
        return {"erro": "CPF/CNPJ inválido"}

    dados_api = consultar_cpf_cnpj(cpf_cnpj)

    usuario = Usuario(
        nome=nome,
        cpf_cnpj=cpf_cnpj
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return {
        "usuario": usuario,
        "dados_externos": dados_api
    }

@app.put("/usuarios/{usuario_id}")
def atualizar_usuario(usuario_id: int, nome: str, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        return {"erro": "Usuário não encontrado"}

    usuario.nome = nome
    db.commit()
    return usuario


@app.delete("/usuarios/{usuario_id}")
def deletar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        return {"erro": "Usuário não encontrado"}

    db.delete(usuario)
    db.commit()
    return {"msg": "Usuário deletado"}
