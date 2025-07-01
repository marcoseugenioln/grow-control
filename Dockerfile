# Base da imagem Docker a ser utilizada
FROM python:3.13-alpine

# Copie arquivos ou pastas da origem para o caminho de destino no sistema de arquivos da imagem.
COPY . .

# expose port
EXPOSE 3000

# instal dependencies
RUN pip install -r requirements.txt

# Configura o contêiner para ser executado como um executável.
ENTRYPOINT ["python","index.py", "config.json"]