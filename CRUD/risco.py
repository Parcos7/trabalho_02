import numpy as np
from persistencia import ler_db
from ativos import Equipamento

def calcular_risco_global():
    db_inventario = ler_db()
    equipamentos = list(db_inventario.values())
    n = len(equipamentos)

    if n == 0:
        return ["====== RELATÓRIO DE RISCO GLOBAL ======", "Nenhum ativo cadastrado para calcular risco."]

    vulns_ativas = []
    for indice_eq, eq in enumerate(equipamentos):
        for vulnerabilidade in eq.get('vulnerabilidades', []):
            if vulnerabilidade.get('status', '').strip().lower() != 'corrigida':
                vulns_ativas.append((indice_eq, vulnerabilidade))

    m = len(vulns_ativas)
    if m == 0:
        return [
            "================= RELATÓRIO DE RISCO GLOBAL =================",
            "SISTEMA 100% SEGURO",
            "Nenhuma vulnerabilidade ativa detectada.",
            "Matriz M: 0x0"
        ]

    pesos = {'baixa': 1.0, 'media': 2.5, 'alta': 5.0, 'critica': 10.0}

    M = np.zeros((n, m))
    v = np.zeros(m)

    for indice_vuln, (indice_eq, vulnerabilidade) in enumerate(vulns_ativas):
        M[indice_eq, indice_vuln] = 1.0
        severidade = vulnerabilidade.get('severidade', 'baixa').strip().lower()
        v[indice_vuln] = pesos.get(severidade, 1.0)

    b = np.dot(M, v)

    for i, eq in enumerate(equipamentos):
        tipo = str(eq.get('tipo', '')).upper()
        ativo_obj = Equipamento.fabricar_ativo(tipo, eq)
        fator_exposicao = ativo_obj.fator_exposicao() if ativo_obj else 1.0
        b[i] *= fator_exposicao

    A = np.zeros((n, n))
    indices_por_id = {str(eq.get('id', '')): indice for indice, eq in enumerate(equipamentos)}
    tipo_pai = {
        'ROTEADOR': 'SERVIDOR',
        'NOTEBOOK': 'ROTEADOR',
        'DESKTOP': 'ROTEADOR'
    }

    for i, eq in enumerate(equipamentos):
        dependencias = eq.get('dependencias', [])
        if not dependencias:
            pai_esperado = tipo_pai.get(str(eq.get('tipo', '')).upper())
            if pai_esperado:
                ativo_pai = next(
                    (ativo for ativo in equipamentos if str(ativo.get('tipo', '')).upper() == pai_esperado),
                    None
                )
                if ativo_pai:
                    dependencias = [{'id_alvo': str(ativo_pai.get('id', '')), 'fracao': 1.0}]

        for dep in dependencias:
            id_alvo = str(dep.get('id_alvo', ''))
            fracao = float(dep.get('fracao', 0.0))
            indice_alvo = indices_por_id.get(id_alvo)
            if indice_alvo is not None:
                A[i, indice_alvo] += fracao

    I = np.eye(n)
    I_A = I - A
    det = np.linalg.det(I_A)

    linhas = []
    linhas.append("=================== RELATÓRIO DE RISCO GLOBAL ===================")

    x = None
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
            x = None

    for i, eq in enumerate(equipamentos):
        nome = eq.get('nome', str(eq.get('id', ''))).lower()
        r_prop = b[i]
        r_efet = f"{x[i]:5.2f}" if x is not None else "N/A"
        linhas.append(f"[{nome:<8}] Risco Próprio: {r_prop:5.2f} | Risco Efetivo: {r_efet}")

    return linhas