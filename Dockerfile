# ==============================================================================
# Dockerfile — CyberPixel SOC (Trabalho 02 - UFU Cibersegurança)
# Estudante: Marcos (Matrícula: 12621CBS214)
# Identificador do Projeto: trab02_2026_2_12621cbs214
# ==============================================================================

FROM python:3.10-slim

LABEL maintainer="12621CBS214"
LABEL project="trab02_2026_2_12621cbs214"
LABEL course="Bacharelado em Ciberseguranca - UFU"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DISPLAY=:0

RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    x11vnc \
    novnc \
    websockify \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8080

CMD ["bash", "-c", "Xvfb :0 -screen 0 1280x720x24 -ac & sleep 1 && x11vnc -display :0 -nopw -forever -shared -bg && websockify --web /usr/share/novnc 8080 localhost:5900 & python main_game.py"]
