# Dockerfile para FastAPI Admin Dashboard
FROM python:3.11-slim

# Diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto
COPY . /app

# Instala dependências
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir fastapi uvicorn redis pydantic

# Porta exposta
EXPOSE 8001

# Comando para iniciar o serviço
CMD ["uvicorn", "admin_dashboard:app", "--host", "0.0.0.0", "--port", "8001"]
