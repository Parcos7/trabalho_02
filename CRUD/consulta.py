# =====================================================================
# NOTA DE NOMENCLATURA PESSOAL:
# 'db'  -> Simplificação de "banco_de_dados" 
# 'arq' -> Simplificação de "arquivos" ou "arquivo"
# =====================================================================

from persistencia import ler_db

def consultar_todosA():
    db_inventario = ler_db()
    for chave, ativo in db_inventario.items():
            print(f"\nID: {ativo['id']}\n"\
                f"Hostname: {ativo['nome']}\n"\
                f"Responsável: {ativo['responsavel']}\n"\
                f"Localização: {ativo['local']}\n"\
                f"Tipo: {ativo['tipo']}\n" )   

            print("\n--- Vulnerabilidades Associadas ---")
            if not len(ativo['vulnerabilidades']):
                print(" -> Este equipamento está limpo. Nenhuma vulnerabilidade registrada.") 
            else:
                for vul in ativo['vulnerabilidades']:
                    print(f" -> [{vul['severidade'].upper()}] {vul['descricao']} | Status: {vul['status']}\n")
            print("="*45)        


def consultar_ativo():
    db_inventario = ler_db()
    
    print("\n--- CONSULTA DE ATIVO DE TI ---")
    termo_busca = input("Digite o ID numérico ou o Hostname do ativo que deseja buscar: ").strip().lower()
    
    encontrado = False
    
    for chave, ativo in db_inventario.items():
        if str(ativo['id']) == termo_busca or ativo['nome'].lower() == termo_busca:
            print("\n[ ATIVO ENCONTRADO ]")
            print(f"\nID: {ativo['id']}\n"\
                f"Hostname: {ativo['nome']}\n"\
                f"Responsável: {ativo['responsavel']}\n"\
                f"Localização: {ativo['local']}\n"\
                f"Tipo: {ativo['tipo']}\n" )   
            
            print("\n--- Vulnerabilidades Associadas ---")
            if not len(ativo['vulnerabilidades']):  
                print(f" -> O equipamento {ativo['nome']} está limpo. Nenhuma vulnerabilidade registrada.\n")    
            else:
                for vul in ativo['vulnerabilidades']:  
                    print(f" -> [{vul['severidade'].upper()}] {vul['descricao']} | Status: {vul['status']}\n")
            print("="*45)          
            encontrado = True
            break 
            
    if not encontrado:
        print("\nErro: Nenhum ativo encontrado com esse ID ou Hostname no db.")
