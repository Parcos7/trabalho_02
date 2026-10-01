# =====================================================================
# NOTA DE NOMENCLATURA PESSOAL:
# 'db'  -> Simplificação de "base de dados"
# 'arq' -> Simplificação de "ficheiros" ou "ficheiro"
# 'res' -> Simplificação de "Responsavel"
# 'loc' -> Simplificação de "Localidade"
# 'fw' -> Simplificação de "firmware"
# 'so' -> Simplificação de "Sistema Operacional"
# =====================================================================

from persistencia import ler_db, salvar_db, TipoAtivo
from ativos import Servidor, Roteador, Notebook, Desktop

def cadastrar_ativo():
    db_inventario = ler_db()
    
    print("\n--- REGISTO DE NOVO ATIVO ---")

    while True:
        try:
            id_num = int(input("Digite o ID numérico do ativo de TI: "))
            id_str = str(id_num)  
            
            if id_str in db_inventario:
                print("Erro: Este ID já existe na db. Tente outro.")
                continue
            break
        except ValueError:
            print("Erro: O ID deve ser um número inteiro. Tente novamente.")
            
    ativo_host = ""
    while ativo_host == "":
        print("="*45)
        print("Padrão da empresa:\n" \
            "Notebook = NOTP(Seguido do património)\n" \
            "Servidor = SERV(Seguido do patrimônio)\n" \
            "Desktop = MICP(Seguido do patrimônio)\n" \
            "Roteadores = ROTP(Seguido do patrimônio)\n")
        print("="*45)
        
        pre_validos = ("notp", "serv", "micp", "rotp")
        try:
            ativo_host = input("Digite o hostname do equipamento: ").strip().lower()

            if ativo_host == "":
                raise ValueError(" O campo hostname não pode ficar vazio.")
            for item in db_inventario.values():
                if item.get('nome') == ativo_host:
                    raise ValueError("Valor duplicado. Tente novamente.")
            if not ativo_host.startswith(pre_validos):
                raise ValueError("Hostname fora do padrão. Inicie com NOTP, SERV, MICP ou ROTP") 
                
        except ValueError as erro:
            print(f"\nErro:{ erro}\n")
            ativo_host = ""

    ativo_res = ""
    while ativo_res == "":
        try:        
            ativo_res = input("Digite o nome do responsável: ").strip().title()
            if ativo_res == "":
                raise ValueError("O campo responsável não pode ficar vazio.\n")
            elif not ativo_res.replace(" ", "").isalpha():
                raise ValueError("O responsável não pode ter números ou símbolos.\n")
        except ValueError as erro:
            print(f"\nErro: {erro}\n")
            ativo_res = ""

    ativo_loc = ""
    while ativo_loc == "":
        try:
            ativo_loc = input("Digite a localização do ativo: ").strip().title()
            if ativo_loc == "":
                raise ValueError("Localidade não pode estar vazia")
            elif not ativo_loc.replace(" ", "").isalpha():
                raise ValueError("A localização não pode ficar vazia ou ter números e símbolos")       
        except ValueError as erro:
            print(f"\nErro:{erro}\n")
            ativo_loc = ""

    print("\nTipos de Ativos disponíveis:")
    for tipo in TipoAtivo:
        print(f"{tipo.value} - {tipo.name}")
        
    novo_ativo = None
    
    while True:
        try:
            escolha = int(input("Escolha o número correspondente ao tipo: "))
        
            match escolha:
                case TipoAtivo.NOTEBOOK.value:
                    ram = int(input("Digite a quantidade de memória RAM (GB): "))
                    novo_ativo = Notebook(id_num, ativo_host, ativo_res, ativo_loc, ram)
                    novo_ativo.tipo = "NOTEBOOK"
                    break
                
                case TipoAtivo.SERVIDOR.value:
                    so = input("Digite o Sistema Operativo do Servidor: ").strip()
                    novo_ativo = Servidor(id_num, ativo_host, ativo_res, ativo_loc, so)
                    novo_ativo.tipo = "SERVIDOR"
                    break
                
                case TipoAtivo.ROTEADOR.value:
                    fw = input("O firmware está atualizado? (S/N): ").strip().upper()
                    fw_atualizado = True if fw == 'S' else False
                    novo_ativo = Roteador(id_num, ativo_host, ativo_res, ativo_loc, fw_atualizado)
                    novo_ativo.tipo = "ROTEADOR"
                    break
                
                case TipoAtivo.DESKTOP.value:
                    ram = int(input("Digite a quantidade de memória RAM (GB) da máquina base: "))
                    novo_ativo = Desktop(id_num, ativo_host, ativo_res, ativo_loc, ram) 
                    novo_ativo.tipo = "Desktop"
                    break
                case _:
                    print("\nErro: Número fora da lista.\n")
                
        except ValueError:
            print("\nErro: Digite um dos números da lista ou garanta que os dados extra estão corretos.\n")


    db_inventario[id_str] = novo_ativo.__dict__
    
    salvar_db(db_inventario)

    print(f"\nSucesso: Ativo '{novo_ativo.nome}' \
          (Objeto {novo_ativo.__class__.__name__}) registado e guardado na db!")