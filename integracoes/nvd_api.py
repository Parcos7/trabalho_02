import json
import os
import re
import threading
import time
from queue import Empty, Full, Queue
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class NvdCveApi:
    BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    CACHE_SECONDS = 600

    def __init__(self, timeout=8):
        self.timeout = timeout
        self.api_key = os.getenv("NVD_API_KEY", "").strip()
        self._cache = {}
        self._lock = threading.Lock()
        self._last_request = 0.0

    def buscar(self, termo, inicio=0, limite=100):
        termo = str(termo).strip()
        if len(termo) < 3:
            return {"vulnerabilidades": [], "total": 0, "inicio": inicio}

        limite = min(max(limite, 1), 100)
        inicio = max(0, int(inicio))
        chave_cache = (termo.casefold(), inicio, limite)
        agora = time.monotonic()
        with self._lock:
            resultado_cache = self._cache.get(chave_cache)
            if resultado_cache and agora - resultado_cache[0] < self.CACHE_SECONDS:
                return {
                    "vulnerabilidades": list(resultado_cache[1]["vulnerabilidades"]),
                    "total": resultado_cache[1]["total"],
                    "inicio": inicio
                }

        self._respeitar_limite()
        parametros_busca = {"startIndex": inicio, "resultsPerPage": limite}
        if re.fullmatch(r"CVE-\d{4}-\d+", termo, re.IGNORECASE):
            parametros_busca["cveId"] = termo.upper()
        else:
            parametros_busca["keywordSearch"] = termo
        parametros = urlencode(parametros_busca)
        cabecalhos = {"User-Agent": "CyberPixel/1.0 CVE lookup"}
        if self.api_key:
            cabecalhos["apiKey"] = self.api_key
        requisicao = Request(f"{self.BASE_URL}?{parametros}", headers=cabecalhos)

        try:
            with urlopen(requisicao, timeout=self.timeout) as resposta:
                conteudo = json.loads(resposta.read().decode("utf-8"))
        except HTTPError as erro:
            if erro.code == 429:
                raise RuntimeError("Limite de consultas da NVD atingido. Aguarde e tente novamente.") from erro
            raise RuntimeError(f"A NVD respondeu com HTTP {erro.code}.") from erro
        except (OSError, json.JSONDecodeError) as erro:
            raise RuntimeError("Não foi possível consultar a API da NVD.") from erro

        vulnerabilidades = [
            vulnerabilidade
            for registro in conteudo.get("vulnerabilities", [])
            if (vulnerabilidade := self._normalizar(registro.get("cve", {}))) is not None
        ]
        resultado = {
            "vulnerabilidades": vulnerabilidades,
            "total": int(conteudo.get("totalResults", len(vulnerabilidades))),
            "inicio": inicio
        }

        with self._lock:
            self._cache[chave_cache] = (time.monotonic(), resultado)
        return {
            "vulnerabilidades": list(vulnerabilidades),
            "total": resultado["total"],
            "inicio": inicio
        }

    def _respeitar_limite(self):
        intervalo_minimo = 0.65 if self.api_key else 6.1
        with self._lock:
            espera = intervalo_minimo - (time.monotonic() - self._last_request)
            if espera > 0:
                time.sleep(espera)
            self._last_request = time.monotonic()

    @staticmethod
    def _normalizar(cve):
        identificador = cve.get("id")
        if not identificador:
            return None

        descricoes = cve.get("descriptions", [])
        descricao = next(
            (item.get("value", "") for item in descricoes if item.get("lang") == "en"),
            descricoes[0].get("value", "") if descricoes else ""
        ).strip()
        fraquezas = cve.get("weaknesses", [])
        categoria = next(
            (
                item.get("value", "")
                for fraqueza in fraquezas
                for item in fraqueza.get("description", [])
                if item.get("value", "").startswith("CWE-")
            ),
            "Vulnerabilidade CVE"
        )
        severidade = "alta"
        metricas = cve.get("metrics", {})
        for nome_metrica in ("cvssMetricV40", "cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
            lista_metricas = metricas.get(nome_metrica, [])
            if lista_metricas:
                dados_cvss = lista_metricas[0].get("cvssData", {})
                severidade_api = dados_cvss.get("baseSeverity", "").upper()
                mapa_severidade = {
                    "LOW": "baixa",
                    "MEDIUM": "media",
                    "MODERATE": "media",
                    "HIGH": "alta",
                    "CRITICAL": "critica"
                }
                severidade = mapa_severidade.get(severidade_api, severidade)
                break

        return {
            "id": identificador,
            "nome": f"{identificador} | {descricao or 'Sem descrição disponível'}",
            "cve": identificador,
            "descricao": descricao or "Sem descrição disponível",
            "categoria": categoria,
            "severidade": severidade
        }


class NvdCveSearchWorker:
    def __init__(self, api=None):
        self.api = api or NvdCveApi()
        self._pedidos = Queue(maxsize=1)
        self._resultados = Queue(maxsize=1)
        self._thread = threading.Thread(target=self._executar, daemon=True, name="nvd-cve-search")
        self._thread.start()

    def solicitar(self, termo, inicio=0):
        pedido = (termo, inicio)
        try:
            self._pedidos.put_nowait(pedido)
        except Full:
            try:
                self._pedidos.get_nowait()
            except Empty:
                pass
            self._pedidos.put_nowait(pedido)

    def receber(self):
        resultado = None
        while True:
            try:
                resultado = self._resultados.get_nowait()
            except Empty:
                return resultado

    def _executar(self):
        while True:
            termo, inicio = self._pedidos.get()
            try:
                resultado = (termo, self.api.buscar(termo, inicio), "")
            except Exception as erro:
                resultado = (termo, {"vulnerabilidades": [], "total": 0, "inicio": inicio}, str(erro))

            try:
                self._resultados.put_nowait(resultado)
            except Full:
                try:
                    self._resultados.get_nowait()
                except Empty:
                    pass
                self._resultados.put_nowait(resultado)