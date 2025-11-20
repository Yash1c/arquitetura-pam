#!/bin/bash

echo "🔑 SISTEMA PAM - CLIENTE"
echo "========================"

# 1. Gerar par de chaves
echo "1. 🔑 Gerando par de chaves..."
ssh-keygen -t rsa -b 4096 -f /tmp/pam_key -N "" -q
echo "✅ Chaves geradas: /tmp/pam_key"

# 2. Obter código MFA atual
echo "2. 📱 Obtendo código MFA..."
SECRET="JBSWY3DPEHPK3PXP"
MFA_CODE=$(python3 -c "
import pyotp
import time
totp = pyotp.TOTP('$SECRET')
print(totp.now())
" 2>/dev/null)

if [ -z "$MFA_CODE" ]; then
    echo "❌ Python/pyotp não disponível. Digite manualmente:"
    read MFA_CODE
else
    echo "📟 Código MFA: $MFA_CODE"
fi

# 3. Solicitar certificado
echo "3. 🚀 Solicitando certificado ao Signer..."
PUBLIC_KEY=$(cat /tmp/pam_key.pub)

RESPONSE=$(curl -s -X POST http://localhost:5000/request-certificate \
  -H "Content-Type: application/json" \
  -d "{\"public_key\": \"$PUBLIC_KEY\", \"mfa_code\": \"$MFA_CODE\"}")

echo "📨 Resposta do Signer:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"

# 4. Extrair certificado
echo "4. 💾 Salvando certificado..."
echo "$RESPONSE" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if data.get('status') == 'success':
        with open('/tmp/pam_key-cert.pub', 'w') as f:
            f.write(data['certificate'])
        print('✅ Certificado salvo: /tmp/pam_key-cert.pub')
        print('⏰ Validade: 10 minutos')
    else:
        print('❌ Erro:', data.get('error'))
except Exception as e:
    print('❌ Erro ao processar resposta:', e)
"

# 5. Testar conexão (se certificado foi gerado)
if [ -f "/tmp/pam_key-cert.pub" ]; then
    echo "5. 🔌 Testando conexão SSH..."
    ssh -i /tmp/pam_key \
        -o CertificateFile=/tmp/pam_key-cert.pub \
        -o StrictHostKeyChecking=no \
        -p 2223 \
        testuser@localhost \
        "echo '🎉 CONEXÃO SSH BEM-SUCEDIDA! Sistema PAM funcionando!' && whoami"
else
    echo "5. ❌ Certificado não gerado, pulando teste SSH"
fi

echo "========================"
echo "🧪 PROCESSO CONCLUÍDO"
