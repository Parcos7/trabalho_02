import numpy as np

from ativos import Equipamento
from persistencia import ler_db


FRACAO_PROPAGACAO_ASCENDENTE = 0.25


def _calcular_riscos_da_rede(equipamentos):
    quantidade_equipamentos = len(equipamentos)
    vulnerabilidades_ativas = []

    for indice, equipamento in enumerate(equipamentos):
        for vulnerabilidade in equipamento.get('vulnerabilidades', []):
            if Equipamento.vulnerabilidade_esta_aberta(vulnerabilidade):
                vulnerabilidades_ativas.append((indice, vulnerabilidade))

    quantidade_vulnerabilidades = len(vulnerabilidades_ativas)
    matriz_vulnerabilidades = np.zeros((quantidade_equipamentos, quantidade_vulnerabilidades))
    vetor_severidades = np.zeros(quantidade_vulnerabilidades)

    for indice_vulnerabilidade, (indice_ativo, vulnerabilidade) in enumerate(vulnerabilidades_ativas):
        matriz_vulnerabilidades[indice_ativo, indice_vulnerabilidade] = 1.0
        severidade = str(vulnerabilidade.get('severidade', 'baixa')).strip().lower()
        vetor_severidades[indice_vulnerabilidade] = Equipamento.PESOS_SEVERIDADE.get(severidade, 1.0)

    riscos_base = np.dot(matriz_vulnerabilidades, vetor_severidades)
    riscos_proprios = np.zeros(quantidade_equipamentos)

    for indice, equipamento in enumerate(equipamentos):
        ativo = Equipamento.fabricar_ativo(str(equipamento.get('tipo', '')).upper(), equipamento)
        if ativo:
            riscos_proprios[indice] = ativo.calcular_risco(riscos_base[indice])
        else:
            riscos_proprios[indice] = riscos_base[indice]

    indices_por_id = {
        str(equipamento.get('id', '')): indice
        for indice, equipamento in enumerate(equipamentos)
    }
    tipos_pai = {
        'ROTEADOR': ('SERVIDOR',),
        'NOTEBOOK': ('ROTEADOR', 'SERVIDOR'),
        'DESKTOP': ('ROTEADOR', 'SERVIDOR')
    }
    matriz_dependencias = np.zeros((quantidade_equipamentos, quantidade_equipamentos))
    conexoes = []
    peso_dependentes = np.zeros(quantidade_equipamentos)

    for indice, equipamento in enumerate(equipamentos):
        dependencias = [
            dependencia for dependencia in equipamento.get('dependencias', [])
            if str(dependencia.get('id_alvo', '')) in indices_por_id
        ]

        if not dependencias:
            tipos_pai_esperados = tipos_pai.get(str(equipamento.get('tipo', '')).upper(), ())
            equipamento_pai = next(
                (
                    candidato for candidato in equipamentos
                    if str(candidato.get('tipo', '')).upper() in tipos_pai_esperados
                    and str(candidato.get('id', '')) != str(equipamento.get('id', ''))
                ),
                None
            )
            if equipamento_pai:
                dependencias = [{
                    'id_alvo': str(equipamento_pai.get('id', '')),
                    'fracao': 1.0
                }]

        for dependencia in dependencias:
            indice_pai = indices_por_id.get(str(dependencia.get('id_alvo', '')))
            if indice_pai is None or indice_pai == indice:
                continue

            fracao = float(dependencia.get('fracao', 1.0))
            if fracao <= 0:
                continue
            conexoes.append((indice, indice_pai, fracao))
            peso_dependentes[indice_pai] += fracao

    for indice_dependente, indice_pai, fracao in conexoes:
        matriz_dependencias[indice_dependente, indice_pai] += fracao
        fracao_ascendente = FRACAO_PROPAGACAO_ASCENDENTE * fracao / peso_dependentes[indice_pai]
        matriz_dependencias[indice_pai, indice_dependente] += fracao_ascendente

    matriz_sistema = np.eye(quantidade_equipamentos) - matriz_dependencias
    determinante = np.linalg.det(matriz_sistema) if quantidade_equipamentos else 1.0

    if quantidade_vulnerabilidades == 0:
        riscos_efetivos = np.zeros(quantidade_equipamentos)
    elif np.isclose(determinante, 0.0):
        riscos_efetivos = None
    else:
        try:
            riscos_efetivos = np.linalg.solve(matriz_sistema, riscos_proprios)
        except np.linalg.LinAlgError:
            riscos_efetivos = None

    return riscos_proprios, riscos_efetivos, quantidade_vulnerabilidades, determinante


def calcular_relatorio_risco_por_sala():
    inventario = ler_db()
    equipamentos = list(inventario.values())
    riscos_proprios, riscos_efetivos, quantidade_vulnerabilidades, determinante = _calcular_riscos_da_rede(equipamentos)

    risco_global = sum(riscos_efetivos) if riscos_efetivos is not None else None
    risco_global_formatado = f'{risco_global:.2f}' if risco_global is not None else 'N/A'
    linhas = [
        f'RISCO GLOBAL EFETIVO TOTAL: {risco_global_formatado}',
        '================ RELATÓRIO DE RISCO POR SALA ================',
        f'Matriz de rede: {len(equipamentos)}x{quantidade_vulnerabilidades} | Determ.: {determinante:.2f}'
    ]

    if riscos_efetivos is None:
        linhas.append('ALERTA: Dependência cíclica na rede. Risco efetivo indisponível.')

    indices_por_sala = {}
    for indice, equipamento in enumerate(equipamentos):
        nome_sala = str(equipamento.get('local', '')).strip() or 'Sem sala'
        chave_sala = nome_sala.casefold()
        if chave_sala not in indices_por_sala:
            indices_por_sala[chave_sala] = {'nome': nome_sala, 'indices': []}
        indices_por_sala[chave_sala]['indices'].append(indice)

    for dados_sala in sorted(indices_por_sala.values(), key=lambda sala: sala['nome'].casefold()):
        indices = dados_sala['indices']
        total_sala = sum(riscos_efetivos[indice] for indice in indices) if riscos_efetivos is not None else None
        total_sala_formatado = f'{total_sala:.2f}' if total_sala is not None else 'N/A'
        linhas.append(f'SALA: {dados_sala["nome"]} | RISCO EFETIVO TOTAL: {total_sala_formatado}')

        for indice in indices:
            equipamento = equipamentos[indice]
            nome = str(equipamento.get('nome', equipamento.get('id', ''))).lower()
            risco_efetivo = f'{riscos_efetivos[indice]:5.2f}' if riscos_efetivos is not None else 'N/A'
            linhas.append(
                f'[{nome:<8}] Risco Próprio: {riscos_proprios[indice]:5.2f} | Risco Efetivo: {risco_efetivo}'
            )

    if not equipamentos:
        linhas.append('Nenhum ativo cadastrado para calcular risco por sala.')

    return linhas
