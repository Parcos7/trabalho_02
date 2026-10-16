### =====================================================================
### NOTA DE NOMENCLATURA PESSOAL:
### 'db'  -> Simplificação de "banco_de_dados"
### 'arq' -> Simplificação de "arquivos" ou "arquivo"
### =====================================================================

import json

nome_db = 'inventario_db.json'

def ler_db():
    try:
        with open(nome_db, 'r', encoding='utf-8') as arq_leitura:
            dados_lista = json.load(arq_leitura)
            
            db_em_memoria = {}
            for item in dados_lista:
                chave_str = str(item['id'])
                db_em_memoria[chave_str] = item
                
            return db_em_memoria
            
    except FileNotFoundError:
        return {}
        
    except json.JSONDecodeError as erro: 
        
        raise ValueError(f"Arquivo de banco de dados corrompido. Faça backup antes de continuar. Detalhes: {erro}")
        
    except Exception as erro:
        raise RuntimeError(f"Erro inesperado ao ler o arquivo do banco de dados: {erro}")

def salvar_db(db_atualizado):
    try:
        dados_lista = list(db_atualizado.values())
        
        with open(nome_db, 'w', encoding='utf-8') as arq_escrita:
            json.dump(dados_lista, arq_escrita, indent=4, ensure_ascii=False)
            
    except Exception as erro:
        raise RuntimeError(f"Erro ao tentar gravar no arquivo do banco de dados: {erro}")