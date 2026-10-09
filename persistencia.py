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
    try:
        with open(nome_db, 'r') as arq_leitura:
            dados_lista = json.load(arq_leitura)
            
            db_em_memoria = {}
            for item in dados_lista:
                chave_str = str(item['id'])
                db_em_memoria[chave_str] = item
                
            return db_em_memoria
            
    except FileNotFoundError:
        print("Aviso: arquivo do db não encontrado. Iniciando uma nova base vazia.")
        return {}
        
    except json.JSONDecodeError:
        print("Erro crítico: O arquivo do db está corrompido.")
        return {}
        
    except Exception as erro:
        print(f"Erro inesperado ao ler o arquivo do db: {erro}")
        return {}

def salvar_db(db_atualizado):
    try:
        with open(nome_db, 'w') as arq_escrita:
            dados_lista = list(db_atualizado.values())
            
            json.dump(dados_lista, arq_escrita, indent=4)
            
    except Exception as erro:
        print(f"Erro ao tentar gravar no arquivo do db: {erro}")