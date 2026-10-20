from persistencia import ler_db, salvar_db
from ativos import Equipamento

def atualizar_ativo(id_busca, novo_resp="", novo_local=""):
    db_inventario = ler_db()
    
    if id_busca not in db_inventario:
        return False

    dados = db_inventario[id_busca]
    ativo_obj = Equipamento.fabricar_ativo(dados.get('tipo'), dados)
    ativo_obj.vulnerabilidades = dados.get('vulnerabilidades', [])
    ativo_obj.dependencias = dados.get('dependencias', [])

    if novo_resp.strip():
        novo_resp_formatado = novo_resp.strip().title()
        if not novo_resp_formatado.replace(" ", "").isalpha():
            return False
        ativo_obj.responsavel = novo_resp_formatado

    if novo_local.strip():
        novo_local_formatado = novo_local.strip().title()
        if not novo_local_formatado.replace(" ", "").isalpha():
            return False
        ativo_obj.local = novo_local_formatado

    db_inventario[id_busca] = ativo_obj.__dict__
    salvar_db(db_inventario)
    return True
