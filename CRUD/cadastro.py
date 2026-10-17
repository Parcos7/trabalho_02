# =====================================================================
# NOTA DE NOMENCLATURA PESSOAL:
# 'db'  -> Simplificação de "base de dados"
# 'arq' -> Simplificação de "arquivos" ou "arquivo"
# 'resp' -> Simplificação de "Responsavel"
# 'cad' -> Simplificação de "Cadastrar"
# =====================================================================
from persistencia import ler_db, salvar_db
from ativos import Equipamento

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


    sala_novo = str(novo_ativo_obj.local).strip().casefold()
    for id_existente, dados in db_inventario.items():
        sala_existente = str(dados.get("local", "")).strip().casefold()
        if dados.get("tipo", "").upper() == alvo_desejado and sala_existente == sala_novo:

            novo_ativo_obj.dependencias.append({
                "id_alvo": str(id_existente),
                "fracao": 1.0
            })
            print(f"[*] AUTO-TOPOLOGIA: {novo_ativo_obj.nome} conectado a {dados.get('nome')} (ID: {id_existente})")
            break

def cadastrar_ativo(id_str, ativo_host, ativo_res, ativo_loc, tipo_str, dado_extra):
    db_inventario = ler_db()

    id_str = str(id_str).strip()
    if not id_str.isdigit():
        print("\nErro: O ID deve ser um número inteiro. Tente novamente.")
        return False
    if len(id_str) < 4:
        print("\nErro: O patrimônio deve conter pelo menos 4 dígitos.")
        return False

    id_chave = str(int(id_str))
    if id_chave in db_inventario:
        print("\nErro: Este ID já existe na db. Tente outro.")
        return False

    tipo_str = str(tipo_str).strip().upper()
    prefixos = {
        "NOTEBOOK": "notp",
        "SERVIDOR": "serv",
        "DESKTOP": "micp",
        "ROTEADOR": "rotp"
    }
    prefixo_esperado = prefixos.get(tipo_str)
    if not prefixo_esperado:
        print("\nErro: Tipo de ativo inválido.")
        return False
        
    ativo_host = ativo_host.strip().lower()
    if ativo_host == "":
        print("\nErro: O campo hostname não pode ficar vazio.")
        return False
        
    for item in db_inventario.values():
        if item.get('nome') == ativo_host:
            print("\nErro: Valor duplicado. Tente novamente.")
            return False
            
    sufixo_hostname = ativo_host[len(prefixo_esperado):]
    if not ativo_host.startswith(prefixo_esperado) or sufixo_hostname != id_str:
        print(f"\nErro: O hostname deve ser {prefixo_esperado} seguido pelo patrimônio informado.")
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
    elif not ativo_loc.replace(" ", "").replace("-", "").isalnum():
        print("\nErro: A localização aceita letras, números, espaços e hífens.")
        return False

    id_num = int(id_str)
    dados_brutos = {
        'id': id_num,
        'nome': ativo_host,
        'responsavel': ativo_res,
        'local': ativo_loc,
        'dado_extra': dado_extra
    }

    dado_extra = str(dado_extra).strip()
    if tipo_str in ("NOTEBOOK", "DESKTOP"):
        if not dado_extra.isdigit() or int(dado_extra) < 1:
            print("\nErro: Informe a memória RAM em GB como um número inteiro positivo.")
            return False
        dados_brutos['qnt_ram'] = int(dado_extra)
    elif tipo_str == "SERVIDOR":
        if not dado_extra:
            print("\nErro: Informe o sistema operacional do servidor.")
            return False
        dados_brutos['sistema_operacional'] = dado_extra
    elif tipo_str == "ROTEADOR":
        firmware = dado_extra.casefold()
        if firmware in ("s", "sim", "atualizado", "yes", "y"):
            dados_brutos['firmware_atualizado'] = True
        elif firmware in ("n", "não", "nao", "desatualizado", "no"):
            dados_brutos['firmware_atualizado'] = False
        else:
            print("\nErro: Informe S ou N para o estado do firmware.")
            return False

    novo_ativo = Equipamento.fabricar_ativo(tipo_str, dados_brutos)

    if not novo_ativo:
        print("\nErro: Falha ao instanciar o objeto. Verifique o tipo ou formato do dado extra.")
        return False

    novo_ativo.tipo = tipo_str

    amarrar_dependencia_automatica(novo_ativo, db_inventario, tipo_str)

    db_inventario[id_chave] = novo_ativo.__dict__
    salvar_db(db_inventario)

    print(f"\nSucesso: Ativo '{novo_ativo.nome}' registrado e guardado na db!")
    return True