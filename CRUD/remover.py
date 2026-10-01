# =====================================================================
# NOTA DE NOMENCLATURA PESSOAL:
# 'db'  -> Simplificação de "banco_de_dados" 
# 'arq' -> Simplificação de "arquivos" ou "arquivo" 
# =====================================================================

from persistencia import ler_db, salvar_db

def remover_ativo():
    db_inventario = ler_db()
    
    print("\n--- REMOVER ATIVO DE TI ---")
    id_busca = input("Digite o ID numérico do ativo que deseja remover: ").strip()
    
    if id_busca in db_inventario:
        nome_removido = db_inventario[id_busca]['nome']
        
        del db_inventario[id_busca]
        
        salvar_db(db_inventario)
        
        print(f"\nSucesso: O ativo '{nome_removido}' e todas as suas vulnerabilidades foram removidos do db de forma permanente.")
    else:
        print("\nErro: Nenhum ativo encontrado com esse ID no db. Nenhuma ação foi realizada.")