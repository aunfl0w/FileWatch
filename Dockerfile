FROM python:3.9-slim

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
    openssl && apt-get clean
COPY . .

RUN mkdir /usr/src/app/certs && \
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /usr/src/app/certs/server.key -out /usr/src/app/certs/server.crt \
    -subj "/C=US/ST=NC/L=Raleigh/O=KillerStuffInc/CN=localhost"

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5443

CMD ["python", "FileWatch.py","--certfile=/usr/src/app/certs/server.crt","--keyfile=/usr/src/app/certs/server.key"]

