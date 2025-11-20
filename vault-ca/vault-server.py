from flask import Flask, request, jsonify
import os
import subprocess
import tempfile
import time
import glob

app = Flask(__name__)

# Paths da chave CA
CA_KEY = "/etc/ssh/ca/ca_key"
CA_PUB = CA_KEY + ".pub"

def ensure_ca_key():
    """Gera a CA (par de chaves) se não existir."""
    if not os.path.exists(CA_KEY):
        print("🔐 Gerando chave da CA...")
        os.makedirs(os.path.dirname(CA_KEY), exist_ok=True)
        # Gerar chave CA sem passphrase
        subprocess.run([
            "ssh-keygen", "-t", "rsa", "-b", "4096",
            "-f", CA_KEY, "-N", ""
        ], check=True)
        print("✅ Chave CA gerada com sucesso!")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "vault-ca"})

@app.route('/sign', methods=['POST'])
def sign_certificate():
    try:
        data = request.json
        public_key = data.get('public_key')
        if not public_key:
            return jsonify({"error": "public_key é obrigatória"}), 400

        print(f"📨 Recebendo solicitação de assinatura para chave: {public_key[:50]}...")

        # Garantir que a CA exista
        ensure_ca_key()

        # Criar diretório temporário para evitar conflitos
        with tempfile.TemporaryDirectory() as tmpdir:
            pub_path = os.path.join(tmpdir, "key.pub")
            cert_path = os.path.join(tmpdir, "key-cert.pub")  # Nome correto

            # Escrever chave pública
            with open(pub_path, "w") as f:
                f.write(public_key.strip() + "\n")

            # Assinar o certificado
            print("🔏 Assinando certificado...")
            result = subprocess.run([
                "ssh-keygen", "-s", CA_KEY,
                "-I", f"user_cert_{time.strftime('%Y%m%d_%H%M%S')}",
                "-n", "root,testuser",
                "-V", "+10m",
                "-q",  # silencioso
                pub_path
            ], check=True, capture_output=True, text=True, cwd=tmpdir)

            print(f"✅ Comando ssh-keygen executado. Verificando certificado em: {cert_path}")
            
            # Verificar se o certificado foi gerado (pode ter nomes diferentes)
            cert_files = glob.glob(os.path.join(tmpdir, "*-cert.pub"))
            if not cert_files:
                # Tentar outro padrão de nome
                cert_files = glob.glob(os.path.join(tmpdir, "*cert*.pub"))
            
            if not cert_files:
                # Listar todos os arquivos para debug
                print(f"📁 Arquivos no diretório {tmpdir}:")
                for f in os.listdir(tmpdir):
                    print(f"  - {f}")
                raise Exception("Certificado não foi gerado pelo ssh-keygen")

            # Usar o primeiro certificado encontrado
            cert_path = cert_files[0]
            print(f"📄 Certificado encontrado: {cert_path}")

            # Ler certificado
            with open(cert_path, "r") as f:
                certificate = f.read().strip()

            print("✅ Certificado assinado com sucesso!")
            return jsonify({
                "status": "success",
                "certificate": certificate,
                "expires_in": "10 minutes"
            })

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)
        print(f"❌ Erro no ssh-keygen: {error_msg}")
        return jsonify({"error": f"Erro no ssh-keygen: {error_msg}"}), 500
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        return jsonify({"error": f"Falha na assinatura do certificado: {str(e)}"}), 500

if __name__ == '__main__':
    print("🚀 Vault CA iniciando na porta 8080...")
    app.run(host='0.0.0.0', port=8080, debug=True)  # Debug=True para mais detalhes
