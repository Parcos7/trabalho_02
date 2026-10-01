# =====================================================================
# NOTA DE NOMENCLATURA PESSOAL:
# 'db'  -> Simplificação de "banco_de_dados" 
# 'arq' -> Simplificação de "arquivos" ou "arquivo" 
# 'res' -> Simplificação de "Responsavel"
# 'loc' -> Simplificação de "Localidade"
# =====================================================================

from persistencia import ler_db, salvar_db, TipoAtivo

def cadastrar_ativo():
    db_inventario = ler_db()
    
    ativo = {}
    print("\n--- CADASTRO DE NOVO ATIVO ---")
    
    while True:
        try:
            id_num = int(input("Digite o ID numérico do ativo de TI: "))
            id_str = str(id_num)  
            
            if id_str in db_inventario:
                print("Erro: Este ID já existe no db. Tente outro.")
                continue
                
            ativo['id'] = id_num
            break
        except ValueError:
            print("Erro: O ID deve ser um número inteiro. Tente novamente.")
            
    ativo['nome'] = ""
    while ativo['nome'] == "":
        print("="*45)
        print("Padrão da empresa:\n" \
            "Notebook = NOTP(Seguido do patrimônio)\n" \
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

                
            ativo['nome'] = ativo_host
        except ValueError as erro:
            print(f"\nErro:{ erro}\n")

    ativo['responsavel'] = ""
    while ativo['responsavel'] == "":
        try:        
            ativo_res = input("Digite o nome do responsável: ").strip().title()
            if ativo_res == "":
                raise ValueError("O campo responsável não pode ficar vazio.\n")
            elif not ativo_res.replace(" ", "").isalpha():
                raise ValueError("O responsavel não pode ter numeros ou simbolos.\n")
            ativo['responsavel'] = ativo_res
        except ValueError as erro:
                print(f"\nErro: {erro}\n")
    
    ativo['local'] = ""
    while ativo['local'] == "":
        try:
            ativo_loc = input("Digite a localização do ativo: ").strip().title()
            if ativo_loc == "":
                raise ValueError("Localidade não pode estar vazia")
            elif not ativo_loc.replace(" ", "").isalpha():
                raise ValueError("A localização não pode ficar vazia ou ter numeros e símbolos")       
            ativo['local'] = ativo_loc
        except ValueError as erro:
            print(f"\nErro:{erro}\n")


    print("\nTipos de Ativos disponíveis:")
    for tipo in TipoAtivo:
        print(f"{tipo.value} - {tipo.name}")
        
    while True:
        try:
            escolha = int(input("Escolha o número correspondente ao tipo: "))
            ativo['tipo'] = TipoAtivo(escolha).name
            break
        except ValueError:
            print("\nErro: Digite um dos números da lista.\n")
            
    ativo['vulnerabilidades'] = []
    
    db_inventario[id_str] = ativo
    salvar_db(db_inventario)
    
    print(f"\nSucesso: Ativo '{ativo['nome']}' cadastrado e salvo no db!")
