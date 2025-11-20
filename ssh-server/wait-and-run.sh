#!/bin/bash

# Espera pela chave CA pública e em seguida inicia o sshd
CA_PUB="/etc/ssh/ca/ca_key.pub"
MAX_WAIT=60
WAITED=0

while [ ! -f "$CA_PUB" ] && [ $WAITED -lt $MAX_WAIT ]; do
  echo "Aguardando $CA_PUB... ($WAITED/$MAX_WAIT)"
  sleep 1
  WAITED=$((WAITED+1))
done

if [ -f "$CA_PUB" ]; then
  echo "Chave CA encontrada, iniciando sshd"
else
  echo "Aviso: chave CA não encontrada após $MAX_WAIT segundos, iniciando sshd mesmo assim"
fi

exec /usr/sbin/sshd -D
