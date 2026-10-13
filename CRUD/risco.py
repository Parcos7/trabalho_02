# =====================================================================
# NOTA DE NOMENCLATURA PESSOAL:
# 'db'  -> Simplificação de "banco_de_dados" 
# 'arq' -> Simplificação de "arquivos" ou "arquivo"
# 'resp' -> Simplificação de "Responsavel"
# 'at' -> Simplificação de "Atualizar"
# 'eq' -> Simplificação de "equipamento"
# 'sev" -> |   | de "Severidade"
# =====================================================================

import numpy as np
from persistencia import ler_db

def gerar_relatorio_risco():
    db_inventario = ler_db()
    equipamentos = list(db_inventario.values())
    n = len(equipamentos)
    
    if n == 0:
        print("Nenhum equipamento cadastrado para análise.")
        return

    todas_vulns = {}
    for eq in equipamentos:
        for vul in eq.get('vulnerabilidades', []):
            nome_vuln = vul['descricao']
            if nome_vuln not in todas_vulns:
                sev = vul['severidade'].lower()
                nota = 10.0 if sev == 'critica' else 7.0 if sev == 'alta' else 4.0 if sev == 'media' else 1.0
                todas_vulns[nome_vuln] = nota
                
    lista_vulns = list(todas_vulns.keys())
    m = len(lista_vulns)

    M = np.zeros((n, m))
    v = np.zeros(m)
    
    for j, nome_vuln in enumerate(lista_vulns):
        v[j] = todas_vulns[nome_vuln]
        
    for i, eq in enumerate(equipamentos):
        vulns_equip = [v['descricao'] for v in eq.get('vulnerabilidades', [])]
        for j, nome_vuln in enumerate(lista_vulns):
            if nome_vuln in vulns_equip:
                M[i, j] = 1
                
    b = np.dot(M, v)
    A = np.zeros((n, n))
    I = np.eye(n)
    matriz_sistema = I - A
    
    print("\n--- ANÁLISE DE RISCO GLOBAL (ÁLGEBRA LINEAR) ---")
    try:
        x = np.linalg.solve(matriz_sistema, b)
        
        for i, eq in enumerate(equipamentos):
            print(f"[{eq['id']}] {eq['nome']} | Risco Próprio: {b[i]:.2f} | Risco Efetivo: {x[i]:.2f}")
            
    except np.linalg.LinAlgError:
        print("Erro: O sistema I - A não é invertível. Verifique as dependências cadastradas.")