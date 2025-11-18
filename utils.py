# utils.py
import random
from typing import List, Dict
from schemas import Participante

def realizar_sorteio_secreto(participantes: List[Participante]) -> Dict[str, str]:
    """
    Recebe uma lista de objetos Participante e retorna um dicionário
    onde a CHAVE é o email de quem dá o presente e o VALOR é o email de quem recebe.
    """
    # Criamos uma cópia da lista para não alterar a original do grupo
    lista_misturada = participantes.copy()
    
    # Embaralhamos a lista aleatoriamente
    random.shuffle(lista_misturada)
    
    resultado = {}
    quantidade = len(lista_misturada)
    
    for i in range(quantidade):
        # A Lógica do Círculo:
        # O participante atual (i) tira o próximo da lista (i + 1).
        # Se for o último da lista, ele tira o primeiro (índice 0).
        
        quem_da = lista_misturada[i]
        
        # Se for o último índice, o índice do recebedor volta para 0
        indice_recebedor = (i + 1) % quantidade
        quem_recebe = lista_misturada[indice_recebedor]
        
        resultado[quem_da.email] = quem_recebe.nome
        
        # NOTA: No futuro, aqui enviaremos o e-mail!
        
    return resultado