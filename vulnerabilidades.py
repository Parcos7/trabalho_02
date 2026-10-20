from persistencia import ler_db, salvar_db
from ativos import Equipamento

CATALOGO_VULNERABILIDADES = (
    {
        'id': 'senha_fraca',
        'nome': 'Senha fraca [N/A]',
        'cve': 'N/A',
        'descricao': 'Senha fraca',
        'categoria': 'Autenticação',
        'severidade': 'baixa'
    },
    {
        'id': 'credencial_padrao',
        'nome': 'Credenciais padrão [N/A]',
        'cve': 'N/A',
        'descricao': 'Credenciais padrão',
        'categoria': 'Autenticação',
        'severidade': 'media'
    },
    {
        'id': 'heartbleed',
        'nome': 'Heartbleed [CVE-2014-0160]',
        'cve': 'CVE-2014-0160',
        'descricao': 'Vazamento de memória',
        'categoria': 'Exposição de memória',
        'severidade': 'alta'
    },
    {
        'id': 'eternalblue',
        'nome': 'EternalBlue [CVE-2017-0144]',
        'cve': 'CVE-2017-0144',
        'descricao': 'RCE via SMBv1',
        'categoria': 'Execução remota',
        'severidade': 'critica'
    },
    {
        'id': 'apache_struts',
        'nome': 'Apache Struts [CVE-2017-5638]',
        'cve': 'CVE-2017-5638',
        'descricao': 'RCE Apache Struts',
        'categoria': 'Execução remota',
        'severidade': 'critica'
    },
    {
        'id': 'log4shell',
        'nome': 'Log4Shell [CVE-2021-44228]',
        'cve': 'CVE-2021-44228',
        'descricao': 'RCE via Log4j',
        'categoria': 'Execução remota',
        'severidade': 'critica'
    },
    {
        'id': 'spring4shell',
        'nome': 'Spring4Shell [CVE-2022-22965]',
        'cve': 'CVE-2022-22965',
        'descricao': 'RCE no Spring',
        'categoria': 'Execução remota',
        'severidade': 'critica'
    }
)

def corrigir_vulnerabilidade(id_busca, cve_alvo, descricao_alvo=''):
    db_inventario = ler_db()
    id_busca = str(id_busca).strip()
    cve_alvo = str(cve_alvo).strip().upper()
    descricao_alvo = str(descricao_alvo).strip()

    if id_busca in db_inventario:
        dados = db_inventario[id_busca]
        vulns = dados.get('vulnerabilidades', [])
        for v in vulns:
            cve_vulnerabilidade = str(v.get('cve', '')).strip().upper()
            descricao_vulnerabilidade = str(v.get('descricao', '')).strip()
            descricao_corresponde = not descricao_alvo or descricao_vulnerabilidade == descricao_alvo
            if (
                cve_vulnerabilidade == cve_alvo
                and descricao_corresponde
                and Equipamento.vulnerabilidade_esta_aberta(v)
            ):
                v['status'] = Equipamento.STATUS_FECHADO
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
            
            vul = {}
            
            cve_input = str(cve_input).strip().upper()
            vul['cve'] = cve_input if cve_input != "" else "N/A"
            
            descricao = str(descricao).strip()
            if not descricao:
                return False
            vul['descricao'] = descricao
            
            categoria = str(categoria).strip()
            if not categoria:
                return False

            vulnerabilidade_predefinida = next(
                (
                    item for item in CATALOGO_VULNERABILIDADES
                    if item['cve'].upper() == cve_input
                    and item['descricao'].casefold() == descricao.casefold()
                    and item['categoria'].casefold() == categoria.casefold()
                ),
                None
            )
            if vulnerabilidade_predefinida:
                cve_input = vulnerabilidade_predefinida['cve']
                descricao = vulnerabilidade_predefinida['descricao']
                categoria = vulnerabilidade_predefinida['categoria']
                vul['cve'] = cve_input
                vul['descricao'] = descricao
            vul['categoria'] = categoria
            
            sev = str(sev).strip().lower()
            if vulnerabilidade_predefinida:
                sev = vulnerabilidade_predefinida['severidade']
            if ativo_obj.tipo == "SERVIDOR":
                sev = "critica"
            severidades_validas = tuple(Equipamento.PESOS_SEVERIDADE)
            if sev not in severidades_validas:
                return False
            vul['severidade'] = sev
                
            stat = str(stat).strip().lower()
            status_validos = (Equipamento.STATUS_ABERTO, Equipamento.STATUS_FECHADO)
            if stat not in status_validos:
                return False
            vul['status'] = stat

            ativo_obj.adicionar_vulnerabilidade(vul)
            db_inventario[id_busca] = ativo_obj.__dict__
            salvar_db(db_inventario)
            return True
        
    return False