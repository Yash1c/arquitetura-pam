Aqui está o README.md editado para o professor executar sem problemas:

```markdown
# 🔐 Sistema PAM - Autenticação com Certificados SSH Expiráveis

## 📋 Descrição do Projeto
Sistema de autenticação PAM (Privileged Access Management) que utiliza certificados SSH de curta duração (10 minutos) com autenticação multi-fator (MFA) para acesso seguro a servidores.

## 🏗️ Arquitetura do Sistema

```
👤 USUÁRIO
    │
    ↓ (Script cliente)
🔑 SIGNER APP (Porta 5000)
    │  ✅ Valida MFA
    ↓
🏦 VAULT CA (Porta 8080)
    │  ✅ Assina certificados
    ↓  
🖥️ SSH SERVER (Porta 2223)
    │  ✅ Aceita certificados
    ↓
🔓 ACESSO CONCEDIDO
```

## 📁 Estrutura do Projeto

```
arquitetura-pam/
├── 📦 docker-compose.yml
├── 🔑 signer-app/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
├── 🏦 vault-ca/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── vault-server.py
├── 🖥️ ssh-server/
│   ├── Dockerfile
│   └── wait-and-run.sh
├── 👤 client/
│   └── get-certificate.sh
└── 📚 README.md
```

## 🚀 Guia de Execução para o Professor

### ✅ Pré-requisitos Verificados
- Docker e Docker Compose instalados
- Python 3.x 
- Git

### 🔧 Configuração Inicial Obrigatória

#### 1. **Clonar e Acessar o Projeto**
```bash
git clone [url-do-repositorio]
cd arquitetura-pam
```

#### 2. **Configurar Ambiente Python (OBRIGATÓRIO)**
```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependência necessária para o script cliente
pip install pyotp
```

#### 3. **Build dos Containers Docker (OBRIGATÓRIO)**
```bash
# Build de todos os serviços
docker compose build

# Verificar build bem-sucedido
docker images | grep arquitetura-pam
```

### 🏃‍♂️ Execução do Sistema

#### 4. **Iniciar os Serviços**
```bash
# Subir todos os containers
docker compose up -d

# Aguardar 20 segundos para inicialização completa
sleep 20

# Verificar status
docker compose ps
```

**✅ Deve mostrar 3 containers rodando:**
- pam-signer
- pam-vault  
- pam-ssh-server

#### 5. **Verificar Saúde dos Serviços**
```bash
# Testar Signer App
curl http://localhost:5000/health

# Testar Vault CA
curl http://localhost:8080/health

# Saída esperada:
# {"status": "healthy", "service": "signer-app"}
# {"status": "healthy", "service": "vault-ca"}
```

#### 6. **Executar Teste Completo**
```bash
# Navegar para cliente
cd client

# Dar permissão de execução
chmod +x get-certificate.sh

# Executar fluxo completo
./get-certificate.sh
```

### 🎯 Resultado Esperado

```
🔑 SISTEMA PAM - CLIENTE
========================
1. 🔑 Gerando par de chaves...
✅ Chaves geradas: /tmp/pam_key
2. 📱 Obtendo código MFA...
📟 Código MFA: 123456
3. 🚀 Solicitando certificado ao Signer...
📨 Resposta do Signer: { "status": "success", ... }
4. 💾 Salvando certificado...
✅ Certificado salvo: /tmp/pam_key-cert.pub
5. 🔌 Testando conexão SSH...
🎉 CONEXÃO SSH BEM-SUCEDIDA! Sistema PAM funcionando!
testuser
========================
🧪 PROCESSO CONCLUÍDO
```

## 🐛 Solução de Problemas Comuns

### ❌ Erro: "python3: command not found"
```bash
sudo apt update && sudo apt install python3 python3-pip python3-venv
```

### ❌ Erro: "docker: command not found"
```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo apt install docker-compose-plugin
```

### ❌ Erro: "pip: command not found"
```bash
sudo apt install python3-pip
```

### ❌ Erro: Portas ocupadas
```bash
# Verificar portas em uso
sudo netstat -tulpn | grep -E ':(5000|8080|2223)'

# Se ocupadas, altere no docker-compose.yml:
# ports:
#   - "5001:5000"  # Mude a porta externa
```

### ❌ Erro: "Cannot connect to Docker daemon"
```bash
# Iniciar serviço Docker
sudo systemctl start docker
sudo systemctl enable docker

# Adicionar usuário ao grupo docker (recomendado fazer logout/login após)
sudo usermod -aG docker $USER
```

### ❌ Build do Docker falha
```bash
# Limpar cache e rebuildar
docker compose build --no-cache

# Ou rebuildar serviço específico
docker compose build signer-app
```

## 📊 Comandos de Verificação

### Verificar Sistema Funcionando
```bash
# 1. Containers rodando
docker compose ps

# 2. Serviços saudáveis
curl -s http://localhost:5000/health | python3 -m json.tool
curl -s http://localhost:8080/health | python3 -m json.tool

# 3. Teste manual de conexão SSH
ssh -i /tmp/pam_key \
    -o CertificateFile=/tmp/pam_key-cert.pub \
    -o StrictHostKeyChecking=no \
    -p 2223 \
    testuser@localhost "echo '✅ SSH funcionando!' && whoami"
```

### Verificar Certificado Gerado
```bash
# Ver detalhes do certificado
ssh-keygen -L -f /tmp/pam_key-cert.pub

# Ver validade (deve ser 10 minutos)
ssh-keygen -L -f /tmp/pam_key-cert.pub | grep -A 2 "Valid:"
```

## 🧹 Limpeza do Ambiente

### Parar Serviços
```bash
docker compose down
```

### Limpeza Completa
```bash
# Parar e remover tudo
docker compose down -v

# Limpar recursos Docker
docker system prune -f

# Remover chaves temporárias
rm -f /tmp/pam_key* /tmp/test_key*

# Desativar ambiente virtual (se usado)
deactivate
```

## 📝 Para o Relatório

### Evidências de Funcionamento:
1. ✅ Print dos 3 containers rodando (`docker compose ps`)
2. ✅ Print dos endpoints de saúde respondendo
3. ✅ Print do fluxo completo do cliente funcionando
4. ✅ Print da conexão SSH bem-sucedida
5. ✅ Print dos detalhes do certificado (validade de 10min)

### Comandos para Demonstração:
```bash
# 1. Mostrar arquitetura
tree -I 'venv|__pycache__'

# 2. Mostrar serviços rodando
docker compose ps

# 3. Executar fluxo completo
cd client && ./get-certificate.sh

# 4. Verificar certificado
ssh-keygen -L -f /tmp/pam_key-cert.pub | head -20
```

## 🔒 Aspectos de Segurança Implementados

- ✅ **MFA obrigatório** para obtenção de certificados
- ✅ **Certificados de 10 minutos** - janela temporal curta
- ✅ **Autenticação apenas por certificados** - sem senhas SSH
- ✅ **CA dedicada** - isolada em container
- ✅ **Network segregada** - comunicação interna segura

---

## 🆘 Suporte Rápido

### Sequência para Debug:
```bash
# 1. Verificar pré-requisitos
docker --version && python3 --version

# 2. Verificar serviços
docker compose ps

# 3. Ver logs
docker compose logs

# 4. Testar endpoints
curl http://localhost:5000/health || echo "Signer App offline"
curl http://localhost:8080/health || echo "Vault CA offline"

# 5. Reinstalar se necessário
docker compose down && docker compose up -d
```

### Se nada funcionar:
1. Execute todos os passos da **Configuração Inicial Obrigatória**
2. Verifique se as **portas 5000, 8080 e 2223** estão livres
3. Confirme que o **ambiente virtual Python está ativado**
4. Execute `docker compose build --no-cache` para rebuild completo

---

**🎉 Preparado para Demonstração!** Siga a sequência na ordem e qualquer problema consulte a seção de Solução de Problemas.
```

## 🎯 **Principais Melhorias para o Professor:**

1. **✅ Configuração Python explícita** - criando venv e instalando pyotp
2. **✅ Build Docker obrigatório** - antes de executar
3. **✅ Sequência passo a passo** - na ordem correta
4. **✅ Solução de problemas comum** - com comandos copy-paste
5. **✅ Verificações intermediárias** - para confirmar cada etapa
6. **✅ Resultado esperado claro** - mostrando o output ideal
7. **✅ Comandos de verificação** - para debug rápido

Agora o professor conseguirá executar sem problemas! 🚀