### =====================================================================
### NOTA DE NOMENCLATURA PESSOAL:
### 'db'  -> Simplificação de "banco_de_dados"
### 'arq' -> Simplificação de "arquivos" ou "arquivo"
### 'obj' -> Simplificação de "Objeto"
### =====================================================================
from persistencia import ler_db 
from ativos import Equipamento

def consultar_todosA(): 
    db_inventario = ler_db()
    
    print("\n--- LISTAGEM DE TODOS OS ATIVOS ---")

    if not db_inventario:
        print("Nenhum ativo cadastrado no sistema no momento.")
        return False

    for chave, dados in db_inventario.items():
        tipo = dados.get('tipo')
        ativo_obj = Equipamento.fabricar_ativo(tipo, dados)

        if ativo_obj:
            ativo_obj.vulnerabilidades = dados.get('vulnerabilidades', [])
            
            ativo_obj.exibir_informacoes()
            print(f"Status de Risco: {ativo_obj.calcular_risco()}")
            
            print("\n--- Vulnerabilidades Associadas ---")
            if not ativo_obj.vulnerabilidades:
                print(" -> Este equipamento está limpo. Nenhuma vulnerabilidade registrada.")
            else:
                for vul in ativo_obj.vulnerabilidades:
                    print(f" -> [{vul['severidade'].upper()}] {vul['descricao']} | Status: {vul['status']}")
            
            print("=" * 45)
    
    return True

def consultar_ativo(termo_busca):
    db_inventario = ler_db()
    
    termo_busca = str(termo_busca).strip().lower()
    
    if termo_busca == "":
        print("\nErro: O termo de busca não pode ficar vazio.")
        return False

    print(f"\n--- CONSULTA DE ATIVO DE TI: {termo_busca.upper()} ---")
    encontrado = False

    for chave, dados in db_inventario.items():
        if str(dados['id']) == termo_busca or dados['nome'].lower() == termo_busca:
            print("\n[ ATIVO ENCONTRADO ]")
            
            tipo = dados.get('tipo')
            ativo_obj = Equipamento.fabricar_ativo(tipo, dados)
                
            if ativo_obj:
                ativo_obj.vulnerabilidades = dados.get('vulnerabilidades', [])
                
                ativo_obj.exibir_informacoes()
                print(f"Status de Risco: {ativo_obj.calcular_risco()}")
                
                print("\n--- Vulnerabilidades Associadas ---")
                if not ativo_obj.vulnerabilidades:
                    print(" -> Este equipamento está limpo. Nenhuma vulnerabilidade registrada.")
                else:
                    for vul in ativo_obj.vulnerabilidades:
                        print(f" -> [{vul['severidade'].upper()}] {vul['descricao']} | Status: {vul['status']}")
            
            encontrado = True
            break 
            
    if not encontrado:
        print("\nErro: Nenhum ativo encontrado com esse ID ou Hostname no db.")
        return False
        
    return True