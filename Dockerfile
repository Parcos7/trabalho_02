# ==============================================================================
# Dockerfile — CyberPixel SOC (Trabalho 02 - UFU Cibersegurança)
# Estudante: Marcos (Matrícula: 12621CBS214)
# Identificador do Projeto: trab02_2026_2_12621cbs214
# ==============================================================================

# 1. Imagem base enxuta (Python slim) para minimizar superfície de ataque (S4_16)
FROM python:3.10-slim

# Metadados de identificação acadêmica
LABEL maintainer="12621CBS214"
LABEL project="trab02_2026_2_12621cbs214"
LABEL course="Bacharelado em Ciberseguranca - UFU"

# Evita geração de .pyc e força flush imediato de stdout/stderr (12-Factor App XI)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DISPLAY=:0

# 2. Instalação das ferramentas para execução headless e ponte Web (HTML5/noVNC)
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    x11vnc \
    novnc \
    websockify \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 3. Otimização do Cache de Camadas: copia e instala dependências antes do código-fonte (S4_16)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 4. Cópia dos arquivos da aplicação
COPY . /app

# 5. Porta interna exposta pelo websockify (noVNC)
EXPOSE 8080

# 6. Inicialização dos processos:
#    - Xvfb: cria tela virtual em memória RAM (1280x720 24-bit)
#    - x11vnc: captura o display virtual na porta 5900
#    - websockify: converte VNC para WebSockets na porta 8080
#    - python main_game.py: inicia o loop gráfico da aplicação SOC
CMD ["bash", "-c", "Xvfb :0 -screen 0 1280x720x24 -ac & sleep 1 && x11vnc -display :0 -nopw -forever -shared -bg && websockify --web /usr/share/novnc 8080 localhost:5900 & python main_game.py"]
