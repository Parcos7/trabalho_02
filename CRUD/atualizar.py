# =====================================================================
# NOTA DE NOMENCLATURA PESSOAL:
# 'db'  -> Simplificação de "banco_de_dados"
# 'arq' -> Simplificação de "arquivos" ou "arquivo"
# 'resp' -> Simplificação de "Responsavel"
# 'at' -> Simplificalção de "Atualizar"
# =====================================================================
from persistencia import ler_db, salvar_db
from ativos import Equipamento

def atualizar_ativo(id_busca, novo_resp="", novo_local="", dep_alvo="", dep_fracao=""):
    db_inventario = ler_db()
    
    if id_busca not in db_inventario:
        print("\nErro: Nenhum ativo encontrado com esse ID no db.")
        return False

    dados = db_inventario[id_busca]
    ativo_obj = Equipamento.fabricar_ativo(dados.get('tipo'), dados)
    ativo_obj.vulnerabilidades = dados.get('vulnerabilidades', [])
    ativo_obj.dependencias = dados.get('dependencias', [])

    print(f"\n[ ATIVO ENCONTRADO: {ativo_obj.nome} ]")

    if novo_resp.strip():
        novo_resp_formatado = novo_resp.strip().title()
        if not novo_resp_formatado.replace(" ", "").isalpha():
            print("\nErro: O nome do responsavel não pode ter numeros ou simbolos.")
            return False 
        ativo_obj.responsavel = novo_resp_formatado

    if novo_local.strip():
        novo_local_formatado = novo_local.strip().title()
        if not novo_local_formatado.replace(" ", "").isalpha():
            print("\nErro: A localidade não pode conter números. Tente novamente.")
            return False
        ativo_obj.local = novo_local_formatado

    # --- HERANÇA DE RISCO ---
    if dep_alvo.strip() and dep_fracao.strip():
        try:
            frac = float(dep_fracao.strip())
            ativo_obj.dependencias.append({
                "id_alvo": dep_alvo.strip(),
                "fracao": frac
            })
        except ValueError:
            print("\nErro: Fração de dependência inválida.")
            return False

    db_inventario[id_busca] = ativo_obj.__dict__
    salvar_db(db_inventario)
    print(f"\nSucesso: O ativo '{ativo_obj.nome}' foi atualizado no db!")
    return True