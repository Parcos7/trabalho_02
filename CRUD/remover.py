# =====================================================================
# NOTA DE NOMENCLATURA PESSOAL:
# 'db'  -> Simplificação de "banco_de_dados" 
# 'arq' -> Simplificação de "arquivos" ou "arquivo" 
# =====================================================================

# remover.py
from persistencia import ler_db, salvar_db
from ativos import Equipamento

def remover_ativo(): 
    db_inventario = ler_db()
    
    print("\n--- REMOVER ATIVO DE TI ---")
    id_busca = input("Digite o ID numérico do ativo que deseja remover: ").strip()

    if id_busca in db_inventario:
        dados = db_inventario[id_busca]
        
        ativo_obj = Equipamento.fabricar_ativo(dados.get('tipo'), dados)
        ativo_obj.vulnerabilidades = dados.get('vulnerabilidades', [])
        
        print("\nVocê está prestes a remover o seguinte equipamento permanentemente:")
        ativo_obj.exibir_informacoes()
        print("=" * 45)
        
        confirmacao = input(f"Tem certeza que deseja deletar o {ativo_obj.nome}? (S/N): ").strip().upper()
        
        if confirmacao == 'S':
            del db_inventario[id_busca]
            salvar_db(db_inventario)
            print(f"\nSucesso: O ativo '{ativo_obj.nome}' foi removido do db de forma permanente.")
        else:
            print("\nOperação de remoção cancelada.")
    else:
        print("\nErro: Nenhum ativo encontrado com esse ID no db.")