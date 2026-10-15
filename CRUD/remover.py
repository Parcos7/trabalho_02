### =====================================================================
### NOTA DE NOMENCLATURA PESSOAL:
### 'db'  -> Simplificação de "banco_de_dados"
### 'arq' -> Simplificação de "arquivos" ou "arquivo"
### =====================================================================
from persistencia import ler_db, salvar_db
from ativos import Equipamento

def remover_ativo(id_busca): 
    db_inventario = ler_db()
    
    id_busca = str(id_busca).strip()
    
    if id_busca == "":
        print("\nErro: O campo ID não pode ficar vazio.")
        return False

    if id_busca in db_inventario:
        dados = db_inventario[id_busca]
        
        ativo_obj = Equipamento.fabricar_ativo(dados.get('tipo'), dados)
        ativo_obj.vulnerabilidades = dados.get('vulnerabilidades', [])
        
        print("\nVocê acabou de remover o seguinte equipamento permanentemente:")
        ativo_obj.exibir_informacoes()
        print("=" * 45)
        
        del db_inventario[id_busca]
        salvar_db(db_inventario)
        
        print(f"\nSucesso: O ativo '{ativo_obj.nome}' foi removido do db de forma permanente.")
        return True
    else:
        print("\nErro: Nenhum ativo encontrado com esse ID no db.")
        return False