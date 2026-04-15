from sqlalchemy import Column, Integer, String
from app.database import Base

cpf_cnpj = Column(String, unique=True, index=True)

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    cpf_cnpj = Column(String, unique=True, index=True)

