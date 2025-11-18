# main.py
import uuid  # Para gerar IDs únicas para os grupos
from typing import Dict
from fastapi import FastAPI, HTTPException, status
from utils import realizar_sorteio_secreto

# Importamos nossos schemas
from schemas import Grupo, GrupoCreate, Participante, ParticipanteCreate

# ----------------------------------------------------------------
# Inicialização da API
# ----------------------------------------------------------------
app = FastAPI(
    title="API Amigo Secreto 🎅",
    description="API para criar e gerenciar grupos de amigo secreto.",
    version="1.0.0"
)

# ----------------------------------------------------------------
# Nosso "Banco de Dados" Falso (em memória)
# ----------------------------------------------------------------
# Usaremos um dicionário Python onde a CHAVE será o 'id_grupo' (string)
# e o VALOR será o objeto 'Grupo' completo.
db_grupos: Dict[str, Grupo] = {}


# ----------------------------------------------------------------
# Endpoints da API
# ----------------------------------------------------------------

@app.get("/")
async def root():
    """Endpoint raiz apenas para testar se a API está online."""
    return {"message": "Bem-vindo à API de Amigo Secreto! Acesse /docs para testar."}


@app.post("/grupos/", 
          response_model=Grupo, 
          status_code=status.HTTP_201_CREATED,
          summary="Cria um novo grupo de amigo secreto")
async def criar_grupo(grupo_in: GrupoCreate):
    """
    Cria um novo grupo.
    
    - **nome_grupo**: O nome do grupo (ex: "Natal da Família").
    - Retorna o objeto do grupo recém-criado, incluindo seu ID.
    """
    # Gera um ID único e seguro
    id_grupo = str(uuid.uuid4())
    
    # Cria o novo objeto do grupo usando o schema 'Grupo' (que inclui o ID)
    novo_grupo = Grupo(
        id_grupo=id_grupo,
        nome_grupo=grupo_in.nome_grupo,
        participantes=[]  # Começa sem participantes
    )
    
    # Salva no nosso "banco de dados"
    db_grupos[id_grupo] = novo_grupo
    
    return novo_grupo


@app.get("/grupos/{id_grupo}/", 
         response_model=Grupo,
         summary="Obtém detalhes de um grupo específico")
async def obter_grupo(id_grupo: str):
    """
    Obtém os detalhes de um grupo pelo seu ID.
    
    - Retorna 404 se o grupo não for encontrado.
    """
    grupo = db_grupos.get(id_grupo)
    if not grupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo não encontrado"
        )
    return grupo


@app.post("/grupos/{id_grupo}/participantes/", 
          response_model=Grupo,
          summary="Adiciona um novo participante a um grupo")
async def adicionar_participante(id_grupo: str, participante_in: ParticipanteCreate):
    """
    Adiciona um novo participante a um grupo existente.

    - Verifica se o grupo existe.
    - Verifica se o email já foi cadastrado nesse grupo.
    - Retorna o objeto do grupo ATUALIZADO com o novo participante.
    """
    # 1. Busca o grupo
    grupo = db_grupos.get(id_grupo)
    if not grupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo não encontrado"
        )

    # 2. Verifica se o email já existe nesse grupo
    for p in grupo.participantes:
        if p.email == participante_in.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"O email '{participante_in.email}' já está cadastrado neste grupo."
            )

    # 3. Cria o objeto Participante (convertendo de ParticipanteCreate)
    #    (Neste caso, os schemas são iguais, mas é uma boa prática)
    novo_participante = Participante(**participante_in.model_dump())

    # 4. Adiciona o participante à lista do grupo
    grupo.participantes.append(novo_participante)

@app.delete("/grupos/{id_grupo}/participantes/{email}", 
            response_model=Grupo,
            summary="Remove um participante do grupo")
async def remover_participante(id_grupo: str, email: str):
    """
    Remove um participante específico do grupo usando o e-mail dele.
    """
    # 1. Busca o grupo
    grupo = db_grupos.get(id_grupo)
    if not grupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo não encontrado"
        )

    # 2. Tenta encontrar o participante para ver se ele existe
    participante_encontrado = False
    
    # Vamos reconstruir a lista, mantendo apenas quem TEM o email DIFERENTE do que queremos apagar
    # Essa é uma forma muito "Pythonica" de filtrar listas
    nova_lista_participantes = []
    
    for p in grupo.participantes:
        if p.email == email:
            participante_encontrado = True # Achamos quem será deletado
        else:
            nova_lista_participantes.append(p) # Mantemos os outros

    # 3. Se não achou ninguém com esse email, dá erro
    if not participante_encontrado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Participante com email '{email}' não encontrado neste grupo."
        )

    # 4. Atualiza a lista do grupo e retorna o grupo atualizado
    grupo.participantes = nova_lista_participantes
    return grupo

@app.post("/grupos/{id_grupo}/sortear/", 
          summary="Realiza o sorteio do amigo secreto")
async def sortear_grupo(id_grupo: str):
    """
    Realiza o sorteio. 
    
    - Verifica se há pelo menos 3 participantes.
    - Embaralha e define os pares.
    - (Futuro: Envia os emails).
    - Retorna apenas uma mensagem de sucesso, sem revelar os pares.
    """
    grupo = db_grupos.get(id_grupo)
    if not grupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo não encontrado"
        )
        
    if len(grupo.participantes) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="É necessário ter pelo menos 3 participantes para realizar o sorteio."
        )
    
    # Chama a nossa função de lógica
    resultado_pares = realizar_sorteio_secreto(grupo.participantes)
    
    # --- AREA DE DEBUG (Para você ver no terminal) ---
    print("-" * 30)
    print(f"SORTEIO REALIZADO PARA O GRUPO: {grupo.nome_grupo}")
    for quem_da, quem_recebe_nome in resultado_pares.items():
        print(f"{quem_da} --> vai presentear --> {quem_recebe_nome}")
    print("-" * 30)
    # -------------------------------------------------
    
    return {"message": "Sorteio realizado com sucesso! Os participantes receberão o resultado por e-mail."}