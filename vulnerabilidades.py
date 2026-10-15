### =====================================================================
### NOTA DE NOMENCLATURA PESSOAL:
### 'db'  -> Simplificação de "banco_de_dados"
### 'arq' -> Simplificação de "arquivos" ou "arquivo"
### =====================================================================

from persistencia import ler_db, salvar_db
from ativos import Equipamento

def corrigir_vulnerabilidade(id_busca, cve_alvo):
    db_inventario = ler_db()
    id_busca = str(id_busca).strip()
    cve_alvo = str(cve_alvo).strip().upper()

    if id_busca in db_inventario:
        dados = db_inventario[id_busca]
        vulns = dados.get('vulnerabilidades', [])
        encontrou = False
        
        for v in vulns:
            if v.get('cve', '').upper() == cve_alvo:
                v['status'] = 'corrigida'
                encontrou = True
                
        if encontrou:
            db_inventario[id_busca]['vulnerabilidades'] = vulns
            salvar_db(db_inventario)
            return True
            
    return False

def registrar_vulnerabilidade(id_busca, cve_input, descricao, categoria, sev, stat): 
    db_inventario = ler_db()
    
    id_busca = str(id_busca).strip()

    if id_busca in db_inventario:
        dados = db_inventario[id_busca]
        ativo_obj = Equipamento.fabricar_ativo(dados.get('tipo'), dados)
        
        if ativo_obj:
            ativo_obj.vulnerabilidades = dados.get('vulnerabilidades', [])
            ativo_obj.dependencias = dados.get('dependencias', [])
            
            print(f"\n[ ATIVO SELECIONADO: {ativo_obj.nome} ]")
            
            vul = {}
            
            # Tratamento do CVE (Pode ser vazio/N/A)
            cve_input = str(cve_input).strip().upper()
            vul['cve'] = cve_input if cve_input != "" else "N/A"
            
            # Validação da Descrição
            descricao = str(descricao).strip()
            if not descricao:
                print("\n[ERRO] A descrição da fragilidade não pode ficar vazia.")
                return False
            vul['descricao'] = descricao
            
            # Validação da Categoria
            categoria = str(categoria).strip()
            if not categoria:
                print("\n[ERRO] A categoria não pode ficar vazia.")
                return False
            vul['categoria'] = categoria
            
            # Validação da Severidade (Mantendo a sua tupla original)
            sev = str(sev).strip().lower()
            severidades_validas = ("baixa", "media", "alta", "critica")
            if sev not in severidades_validas:
                print(f"\n[ERRO] Severidade inválida. Digite uma destas: {severidades_validas}")
                return False
            vul['severidade'] = sev
                
            # Validação do Status (Mantendo a sua tupla original)
            stat = str(stat).strip().lower()
            status_validos = ("aberta", "em tratamento", "corrigida", "aceita")
            if stat not in status_validos:
                print(f"\n[ERRO] Status inválido. Digite um destes: {status_validos}")
                return False
            vul['status'] = stat
                        
            # Se passou em todas as regras, adiciona e salva
            ativo_obj.adicionar_vulnerabilidade(vul)
            db_inventario[id_busca] = ativo_obj.__dict__
            salvar_db(db_inventario)
            
            print(f"\n[SISTEMA] Sucesso: Vulnerabilidade registrada e vinculada ao ativo '{ativo_obj.nome}' no db!")
            return True
        
    else:
        print("\n[ERRO] Nenhum ativo encontrado com esse ID no db. Cadastre o ativo primeiro.")
        return False