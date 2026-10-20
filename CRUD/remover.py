from persistencia import ler_db, salvar_db

def remover_ativo(id_busca):
    db_inventario = ler_db()
    id_busca = str(id_busca).strip()

    if id_busca == "":
        return False

    if id_busca in db_inventario:
        for asset_data in db_inventario.values():
            if 'dependencias' in asset_data:
                asset_data['dependencias'] = [
                    dependencia for dependencia in asset_data['dependencias']
                    if str(dependencia.get('id_alvo', '')) != id_busca
                ]

        del db_inventario[id_busca]
        salvar_db(db_inventario)
        return True

    return False
