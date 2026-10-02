# =====================================================================
# NOTA DE NOMENCLATURA PESSOAL:
# 'db'  -> Simplificação de "banco_de_dados" 
# 'arq' -> Simplificação de "arquivos" ou "arquivo"
# 'resp' -> Simplificação de "Responsavel"
# 'at' -> Simplificalção de "Atualizar"
# =====================================================================

from persistencia import ler_db, salvar_db
from ativos import Equipamento

def atualizar_ativo():
    db_inventario = ler_db()
    
    print("\n--- ATUALIZAR ATIVO DE TI ---")
    id_busca = input("Digite o ID numérico do ativo que deseja atualizar: ").strip()
    
    if id_busca in db_inventario:
        dados = db_inventario[id_busca]
        ativo_obj = Equipamento.fabricar_ativo(dados.get('tipo'), dados)
        ativo_obj.vulnerabilidades = dados.get('vulnerabilidades', [])
        
        print(f"\n[ ATIVO ENCONTRADO: {ativo_obj.nome} ]")
        
        while True:   
            print("="*45)
            print("1 - Nome do responsavel\n" \
            "2 - Localidade" \
            "\n0 - Cancelar")
            print("="*45)

            try:
                opcao_at = int(input("Digite o número da opção: "))
            except ValueError:
                print("\nErro: Digite um número válido do menu.\n")
                continue             

            match opcao_at:
                case 1:
                    print(f"Responsável atual: {ativo_obj.responsavel}")
                    while True:
                        try:
                            novo_resp = input("Digite o novo responsável (ou aperte Enter para manter o atual): ").strip().title()                                              
                            if novo_resp == "":
                                print("Nenhuma alteração feita.")
                                break 
                            elif not novo_resp.replace(" ", "").isalpha():                            
                                raise ValueError("O nome do responsavel não pode ter numeros ou simbolos.")                             
                            ativo_obj.responsavel = novo_resp
                            break
                        except ValueError as erro:
                            print(f"\nErro:{erro}\n") 
                    
                case 2:
                    print(f"Localização atual: {ativo_obj.local}")
                    while True:
                        try:    
                            novo_local = input("Digite a nova localização (ou aperte Enter para manter a atual): ").strip().title()
                            
                            if novo_local == "":
                                print("Nenhum local foi alterado.\n")
                                break
                            elif not novo_local.replace(" ", "").isalpha():
                                raise ValueError ("A localidade não pode conter números. Tente novamente.")
                            ativo_obj.local = novo_local
                            break
                        except ValueError as erro:
                            print(f"\nErro:{erro}\n")
                                             
                case 0:
                    print("\nAtualizaçãno cancelada.\n")
                    break
                    
                case _:
                    print("\nErro: Opção inválida. Escolha 1, 2 ou 0.\n")
                    
        if opcao_at != 0:
            db_inventario[id_busca] = ativo_obj.__dict__
            salvar_db(db_inventario)
            print(f"\nSucesso: O ativo '{ativo_obj.nome}' foi atualizado no db!")
            
    else:
        print("\nErro: Nenhum ativo encontrado com esse ID no db.")