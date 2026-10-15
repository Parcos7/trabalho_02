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
        
        # Proteção caso a fábrica falhe em ler o tipo
        if ativo_obj:
            ativo_obj.vulnerabilidades = dados.get('vulnerabilidades', [])
            print("\nVocê acabou de remover o seguinte equipamento permanentemente:")
            ativo_obj.exibir_informacoes()
            print("=" * 45)
        
        # --- CORREÇÃO CRÍTICA: LIMPANDO DEPENDÊNCIAS ÓRFÃS ---
        # Varre todo o banco e remove o ID deste ativo das listas de dependências dos outros
        for key, asset_data in db_inventario.items():
            if 'dependencias' in asset_data:
                if id_busca in asset_data['dependencias']:
                    asset_data['dependencias'].remove(id_busca)

        del db_inventario[id_busca]
        salvar_db(db_inventario)
        
        nome_ativo = ativo_obj.nome if ativo_obj else "Desconhecido"
        print(f"\nSucesso: O ativo '{nome_ativo}' foi removido do db e as dependências foram limpas.")
        return True
    else:
        print("\nErro: Nenhum ativo encontrado com esse ID no db.")
        return False