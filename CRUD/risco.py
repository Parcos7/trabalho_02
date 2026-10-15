import numpy as np
from persistencia import ler_db

def calcular_risco_global():
    db_inventario = ler_db()
    equipamentos = list(db_inventario.values())
    n = len(equipamentos)

    if n == 0:
        return ["====== RELATÓRIO DE RISCO GLOBAL ======", "Nenhum ativo cadastrado para calcular risco."]

    vulns_ativas = {}
    for eq in equipamentos:
        for v in eq.get('vulnerabilidades', []):
            cve = v.get('cve', 'N/A')
            if v.get('status', '').lower() != 'corrigida':
                vulns_ativas[cve] = v.get('severidade', 'baixa').lower()

    m = len(vulns_ativas)
    if m == 0:
        return [
            "================= RELATÓRIO DE RISCO GLOBAL =================",
            "SISTEMA 100% SEGURO",
            "Nenhuma vulnerabilidade ativa detectada.",
            "Matriz M: 0x0"
        ]

    cve_indices = {cve: idx for idx, cve in enumerate(vulns_ativas.keys())}
    pesos = {'baixa': 1.0, 'media': 2.5, 'alta': 5.0, 'critica': 10.0}

    M = np.zeros((n, m))
    v = np.zeros(m)

    for cve, sev in vulns_ativas.items():
        v[cve_indices[cve]] = pesos.get(sev, 1.0)

    for i, eq in enumerate(equipamentos):
        for vul in eq.get('vulnerabilidades', []):
            cve = vul.get('cve', 'N/A')
            if cve in cve_indices and vul.get('status', '').lower() != 'corrigida':
                M[i, cve_indices[cve]] = 1.0


    b = np.dot(M, v)

    A = np.zeros((n, n))
    for i, eq in enumerate(equipamentos):
        for dep in eq.get('dependencias', []):
            id_alvo = str(dep.get('id_alvo', ''))
            fracao = float(dep.get('fracao', 0.0))
            for j, alvo_eq in enumerate(equipamentos):
                if str(alvo_eq.get('id', '')) == id_alvo:
                    A[i, j] = fracao
                    break

    I = np.eye(n)
    I_A = I - A
    det = np.linalg.det(I_A)

    linhas = []
    linhas.append("=================== RELATÓRIO DE RISCO GLOBAL ===================")

    if np.isclose(det, 0.0):
        linhas.append(f"Matriz M: {n}x{m} | Determ.: 0.00 (SISTEMA NÃO INVERTÍVEL!)")
        linhas.append("ALERTA: Dependência cíclica total detectada. Risco Efetivo bloqueado.")
        linhas.append("-" * 65)

    else:
        linhas.append(f"Matriz M: {n}x{m} | Determ.: {det:.2f} (Sistema Invertível)")
        linhas.append("-" * 65)
        try:
            x = np.linalg.solve(I_A, b)
        except np.linalg.LinAlgError:
            x = b

    for i, eq in enumerate(equipamentos):
        nome = eq.get('nome', str(eq.get('id', ''))).lower()
        r_prop = b[i]
        r_efet = x[i]
        linhas.append(f"[{nome:<8}] Risco Próprio: {r_prop:5.2f} | Risco Efetivo: {r_efet:5.2f}")

    return linhas