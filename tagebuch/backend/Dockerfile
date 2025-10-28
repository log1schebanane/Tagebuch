# Stage 1: Builder-Stage mit vollem Build-System
FROM python:3.10 as builder

# Installiere die Build-Abhängigkeiten, die für mysqlclient notwendig sind
# build-base: Enthält gcc und andere Build-Tools (auf Debian/Alpine)
# mariadb-client: Enthält die benötigten Header-Dateien für die DB-Verbindung
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config && \
    rm -rf /var/lib/apt/lists/*

# Setze das Arbeitsverzeichnis
WORKDIR /app

# Kopiere und installiere die Python-Abhängigkeiten
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Stage 2: Finales, schlankes Image
FROM python:3.10-slim

# Kopiere die Abhängigkeiten von der Builder-Stage
# Wir kopieren nur das, was zur Laufzeit benötigt wird
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/lib/x86_64-linux-gnu /usr/lib/x86_64-linux-gnu

# Kopiere den Anwendungscode
WORKDIR /app
COPY . .

# Exponiere den Port
EXPOSE 5000

# Starte die Anwendung
CMD ["python", "app.py"]