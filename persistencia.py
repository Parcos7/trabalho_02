### =====================================================================
### NOTA DE NOMENCLATURA PESSOAL:
### 'db'  -> Simplificação de "banco_de_dados"
### 'arq' -> Simplificação de "arquivos" ou "arquivo"
### =====================================================================

import json
from enum import Enum

class TipoAtivo(Enum):
    NOTEBOOK = 1
    SERVIDOR = 2
    ROTEADOR = 3
    BANCO_DE_DADOS = 4

nome_db = 'inventario_db.json'

def ler_db():
    """
    Lê o banco de dados JSON (array de objetos) e retorna um dicionário 
    em memória com chave = id_str e valor = dicionário de dados do ativo.
    """
    try:
        with open(nome_db, 'r', encoding='utf-8') as arq_leitura:
            dados_lista = json.load(arq_leitura)
            
            db_em_memoria = {}
            for item in dados_lista:
                chave_str = str(item['id'])
                db_em_memoria[chave_str] = item
                
            return db_em_memoria
            
    except FileNotFoundError:
        # É normal não achar o arquivo na primeira vez que o programa roda.
        # Retorna dicionário vazio silenciosamente. A interface não precisa de erro aqui.
        return {}
        
    except json.JSONDecodeError as erro:
        # Lança a exceção para PARAR o programa. 
        # Impede que a interface sobrescreva um DB corrompido com uma base vazia.
        raise ValueError(f"Arquivo de banco de dados corrompido. Faça backup antes de continuar. Detalhes: {erro}")
        
    except Exception as erro:
        raise RuntimeError(f"Erro inesperado ao ler o arquivo do banco de dados: {erro}")

def salvar_db(db_atualizado):
    """
    Recebe o dicionário em memória, converte seus valores para uma lista
    (array de objetos) e salva no arquivo JSON.
    """
    try:
        # Extrai apenas os valores (os dicionários dos equipamentos) para formar a lista final
        dados_lista = list(db_atualizado.values())
        
        with open(nome_db, 'w', encoding='utf-8') as arq_escrita:
            # ensure_ascii=False garante que acentos fiquem legíveis no JSON
            json.dump(dados_lista, arq_escrita, indent=4, ensure_ascii=False)
            
    except Exception as erro:
        raise RuntimeError(f"Erro ao tentar gravar no arquivo do banco de dados: {erro}")