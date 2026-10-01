from CRUD.cadastro import cadastrar_ativo
from CRUD.consulta import consultar_ativo, consultar_todosA
from CRUD.atualizar import atualizar_ativo
from CRUD.remover import remover_ativo
from vulnerabilidades import registrar_vulnerabilidade

def menu_principal():
    while True:
        print("\n" + "="*45)
        print("   INVENTÁRIO DE CIBERSEGURANÇA - GESTÃO   \n\n" \
        "1 - Cadastrar novo ativo de TI (Create)\n" \
        "2 - Consultar ativo existente (Read)\n" \
        "3 - Atualizar dados do ativo (Update)\n"\
        "4 - Remover ativo do sistema (Delete)\n"\
        "5 - Registrar nova vulnerabilidade\n" \
        "6 - Consultar todos os ativos.\n" \
        "0 - Sair do sistema\n")
        print("="*45)
        
        opcao = int(input("Escolha uma opção do menu: "))
        try:
            match opcao: 
                case 1:
                    cadastrar_ativo()
                case 2:
                    consultar_ativo()
                case 3:
                    atualizar_ativo()
                case 4:
                    remover_ativo()
                case 5:
                    registrar_vulnerabilidade()
                case 6:
                    consultar_todosA()
                case 0:
                    print("\nEncerrando o sistema de inventário. Até logo!")
                    break                

                case _:
                    print("\nErro: Opção inválida. Digita um número entre 0 e 5.")

        except ValueError:
            print("\nErro: Entrada inválida. Por favor, digite apenas números inteiros.")

if __name__ == "__main__":
    menu_principal()
