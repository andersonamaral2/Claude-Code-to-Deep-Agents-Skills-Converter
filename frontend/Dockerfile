# Dockerfile para o frontend (Python)
FROM python:3.11-slim

WORKDIR /app

# Copia os arquivos do frontend
COPY . .

# Instala as dependências, se houver requirements.txt
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Expõe a porta padrão (ajuste se necessário)
EXPOSE 3000

# Comando para rodar o servidor Python (ajuste se necessário)
CMD ["python", "server.py"]
