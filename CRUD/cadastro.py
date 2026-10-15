# =====================================================================
# NOTA DE NOMENCLATURA PESSOAL:
# 'db'  -> Simplificação de "base de dados"
# 'arq' -> Simplificação de "arquivos" ou "arquivo"
# 'resp' -> Simplificação de "Responsavel"
# 'cad' -> Simplificação de "Cadastrar"
# =====================================================================
from persistencia import ler_db, salvar_db
from ativos import Notebook, Servidor, Roteador, Desktop

def amarrar_dependencia_automatica(novo_ativo_obj, db_inventario, tipo_ativo):
    if not novo_ativo_obj:
        return

    tipo = str(tipo_ativo).upper()
    
    if tipo == "SERVIDOR":
        return

    alvo_desejado = ""
    if tipo in ["NOTEBOOK", "DESKTOP"]:
        alvo_desejado = "ROTEADOR"
    elif tipo == "ROTEADOR":
        alvo_desejado = "SERVIDOR"


    for id_existente, dados in db_inventario.items():
        if dados.get("tipo", "").upper() == alvo_desejado:

            novo_ativo_obj.dependencias.append({
                "id_alvo": str(id_existente),
                "fracao": 1.0
            })
            print(f"[*] AUTO-TOPOLOGIA: {novo_ativo_obj.nome} conectado a {dados.get('nome')} (ID: {id_existente})")
            break

def cadastrar_ativo(id_str, ativo_host, ativo_res, ativo_loc, tipo_str, dado_extra):
    db_inventario = ler_db()
    
    if not id_str.isdigit():
        print("\nErro: O ID deve ser um número inteiro. Tente novamente.")
        return False
        
    if id_str in db_inventario:
        print("\nErro: Este ID já existe na db. Tente outro.")
        return False
        
    ativo_host = ativo_host.strip().lower()
    if ativo_host == "":
        print("\nErro: O campo hostname não pode ficar vazio.")
        return False
        
    for item in db_inventario.values():
        if item.get('nome') == ativo_host:
            print("\nErro: Valor duplicado. Tente novamente.")
            return False
            
    pre_validos = ("notp", "serv", "micp", "rotp")
    if not ativo_host.startswith(pre_validos):
        print("\nErro: Hostname fora do padrão. Inicie com NOTP, SERV, MICP ou ROTP")
        return False

    ativo_res = ativo_res.strip().title()
    if ativo_res == "":
        print("\nErro: O campo responsável não pode ficar vazio.")
        return False
    elif not ativo_res.replace(" ", "").isalpha():
        print("\nErro: O responsável não pode ter números ou símbolos.")
        return False

    ativo_loc = ativo_loc.strip().title()
    if ativo_loc == "":
        print("\nErro: Localidade não pode estar vazia")
        return False
    elif not ativo_loc.replace(" ", "").isalpha():
        print("\nErro: A localização não pode ficar vazia ou ter números e símbolos")
        return False

    novo_ativo = None
    id_num = int(id_str)
    tipo_str = tipo_str.strip().upper()

    try:
        match tipo_str:
            case "NOTEBOOK":
                ram = int(dado_extra) if dado_extra.strip() else 8
                novo_ativo = Notebook(id_num, ativo_host, ativo_res, ativo_loc, ram)
                
            case "SERVIDOR":
                so = str(dado_extra).strip() if dado_extra.strip() else "Linux"
                novo_ativo = Servidor(id_num, ativo_host, ativo_res, ativo_loc, so)
                
            case "ROTEADOR":
                fw = str(dado_extra).strip().upper()
                fw_atualizado = True if fw == 'S' else False
                novo_ativo = Roteador(id_num, ativo_host, ativo_res, ativo_loc, fw_atualizado)
                
            case "DESKTOP":
                ram = int(dado_extra) if dado_extra.strip() else 8
                novo_ativo = Desktop(id_num, ativo_host, ativo_res, ativo_loc, ram)
                
            case _:
                print("\nErro: Tipo de ativo inválido. Escolha NOTEBOOK, SERVIDOR, ROTEADOR ou DESKTOP.")
                return False
                
    except ValueError:
        print("\nErro: O dado extra está no formato incorreto (Ex: RAM deve ser número).")
        return False

    if not novo_ativo:
        print("\nErro: Falha ao instanciar o objeto ativo.")
        return False


    novo_ativo.tipo = tipo_str

    amarrar_dependencia_automatica(novo_ativo, db_inventario, tipo_str)

    db_inventario[id_str] = novo_ativo.__dict__
    salvar_db(db_inventario)

    print(f"\nSucesso: Ativo '{novo_ativo.nome}' registrado e guardado na db!")
    return True