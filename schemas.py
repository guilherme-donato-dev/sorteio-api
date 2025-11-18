# schemas.py
from pydantic import BaseModel, EmailStr
from typing import List, Optional

# ----------------------------------------------------------------
# Schema do Participante
# ----------------------------------------------------------------
class ParticipanteBase(BaseModel):
    """Schema base para o participante."""
    nome: str
    email: EmailStr  # O Pydantic já valida o formato do email!

class ParticipanteCreate(ParticipanteBase):
    """Schema usado para ADICIONAR um participante (não tem ID ainda)."""
    pass

class Participante(ParticipanteBase):
    """Schema usado para EXIBIR um participante (pode ter um ID no futuro)."""
    # Se tivéssemos ID, viria aqui. Por agora, é igual ao Base.
    pass

    class Config:
        # Permite que o Pydantic funcione bem com ORMs (útil no futuro)
        orm_mode = True 

# ----------------------------------------------------------------
# Schema do Grupo
# ----------------------------------------------------------------
class GrupoBase(BaseModel):
    """Schema base para o grupo."""
    nome_grupo: str

class GrupoCreate(GrupoBase):
    """Schema usado para CRIAR um grupo."""
    pass

class Grupo(GrupoBase):
    """
    Schema principal do grupo, usado para RESPONDER ao cliente.
    Inclui o ID e a lista de participantes.
    """
    id_grupo: str
    participantes: List[Participante] = []

    class Config:
        orm_mode = True