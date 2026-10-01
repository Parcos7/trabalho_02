# =====================================================================
# NOTA DE NOMENCLATURA PESSOAL:
# 'db'  -> Simplificação de "banco_de_dados" 
# 'arq' -> Simplificação de "arquivos" ou "arquivo" 
# 'vul' -> Simplificação de "Vulnerabilidade"
# =====================================================================

from persistencia import ler_db, salvar_db

def registrar_vulnerabilidade():
    db_inventario = ler_db()
    
    print("\n--- REGISTRAR NOVA VULNERABILIDADE ---")
    id_busca = input("Digite o ID numérico do ativo que possui a falha: ").strip()
    
    if id_busca in db_inventario:
        ativo = db_inventario[id_busca]
        print(f"\n[ ATIVO SELECIONADO: {ativo['nome']} ]")
        
        vul = {}
        
        vul['descricao'] = input("Descrição da fragilidade (Ex: Senha fraca, porta aberta): ").strip()
        vul['categoria'] = input("Categoria (Ex: Rede, Software, Hardware): ").strip()   

        severidades_validas = ("baixa", "media", "alta", "critica")
        while True:
            sev = input("Severidade (baixa, media, alta, critica): ").strip().lower()
            if sev in severidades_validas:
                vul['severidade'] = sev
                break
            print("Erro: Digite uma severidade válida da lista.")
            
        status_validos = ("aberta", "em tratamento", "corrigida", "aceita")
        while True:
            stat = input("Status (aberta, em tratamento, corrigida, aceita): ").strip().lower()
            if stat in status_validos:
                vul['status'] = stat
                break
            print("Erro: Digite um status válido da lista.")
            
        ativo['vulnerabilidades'].append(vul)
        
        salvar_db(db_inventario)
        
        print(f"\nSucesso: Vulnerabilidade registrada e vinculada ao ativo '{ativo['nome']}' no db!")
        
    else:
        print("\nErro: Nenhum ativo encontrado com esse ID no db. Cadastre o ativo primeiro.")