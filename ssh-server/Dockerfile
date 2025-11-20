FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y openssh-server && rm -rf /var/lib/apt/lists/*

RUN mkdir /var/run/sshd

# Configurar SSH
RUN echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config
RUN echo 'PasswordAuthentication no' >> /etc/ssh/sshd_config
RUN echo 'TrustedUserCAKeys /etc/ssh/ca/ca_key.pub' >> /etc/ssh/sshd_config
RUN echo 'HostKeyAlgorithms +ssh-rsa' >> /etc/ssh/sshd_config

# Criar usuário para testes
RUN useradd -m -s /bin/bash testuser && echo 'testuser:testpass' | chpasswd

# Criar diretório para CA keys
RUN mkdir -p /etc/ssh/ca

EXPOSE 22
COPY wait-and-run.sh /usr/local/bin/wait-and-run.sh
RUN chmod +x /usr/local/bin/wait-and-run.sh

CMD ["/usr/local/bin/wait-and-run.sh"]
