
# syntax=docker/dockerfile:1

# Definir a arquitetura suportada como linux/amd64 para corrigir erro
FROM --platform=linux/amd64 python:3.12.2-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# Set the timezone
ENV TZ=America/Sao_Paulo

WORKDIR /app

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt


RUN apt-get update && apt-get install -y gnupg2 wget apt-transport-https software-properties-common ca-certificates

RUN wget -qO- https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN echo "deb [arch=amd64] https://packages.microsoft.com/debian/10/prod buster main" > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Instalar mssql-tools18 para bcp e sqlcmd
RUN ACCEPT_EULA=Y apt-get install -y mssql-tools18

# Adicionar mssql-tools18 ao PATH
RUN echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc && \
    /bin/bash -c "source ~/.bashrc"

# Instalar os cabeçalhos de desenvolvimento unixODBC (opcional)
RUN apt-get install -y unixodbc-dev

# Instalar a biblioteca Kerberos para distribuições debian-slim (opcional)
RUN apt-get install -y libgssapi-krb5-2

# Switch para o usuário não privilegiado para executar o aplicativo
USER appuser

# Copiar o código-fonte para o contêiner
COPY app.py .
COPY auth.py .
COPY groups.py .
COPY friends.py .
COPY chat.py .
COPY keys.py .
COPY templates templates
COPY static static

# Expor porta
EXPOSE 5000