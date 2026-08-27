#!/usr/bin/env bash
# ==============================================================================
# Script de Automação para Deploy da Infraestrutura com Terraform no GCP
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

export PATH="${HOME}/.local/bin:${PATH}"

# Detect Terraform
if ! command -v terraform &>/dev/null; then
    echo "❌ Erro: Terraform não encontrado no PATH."
    echo "Instalando binário do Terraform..."
    mkdir -p "${HOME}/.local/bin"
    curl -sSL https://releases.hashicorp.com/terraform/1.9.5/terraform_1.9.5_linux_amd64.zip -o /tmp/terraform.zip
    unzip -o /tmp/terraform.zip -d "${HOME}/.local/bin/"
    rm -f /tmp/terraform.zip
fi

# Detect Google Cloud Project
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "")
if [ -z "${CURRENT_PROJECT}" ]; then
    echo "⚠️ Nenhum projeto GCP ativo detectado via gcloud. Usando default das variáveis."
else
    echo "🔍 Projeto GCP Ativo: ${CURRENT_PROJECT}"
fi

# Create terraform.tfvars if it doesn't exist
if [ ! -f "terraform.tfvars" ]; then
    echo "📝 Criando terraform.tfvars a partir de terraform.tfvars.example..."
    cp terraform.tfvars.example terraform.tfvars
    if [ -n "${CURRENT_PROJECT}" ]; then
        sed -i "s/project_id = .*/project_id = \"${CURRENT_PROJECT}\"/" terraform.tfvars
    fi
fi

echo ""
echo "=============================================================================="
echo "🚀 1. Inicializando Terraform..."
echo "=============================================================================="
terraform init -upgrade

echo ""
echo "=============================================================================="
echo "🔍 2. Validando sintaxe dos arquivos Terraform..."
echo "=============================================================================="
terraform validate

echo ""
echo "=============================================================================="
echo "📋 3. Gerando plano de execução (Terraform Plan)..."
echo "=============================================================================="
terraform plan -out=tfplan

echo ""
echo "=============================================================================="
echo "⚡ 4. Aplicando infraestrutura no Google Cloud (Compute Engine + VPC + NAT)..."
echo "=============================================================================="
terraform apply -auto-approve tfplan
rm -f tfplan

echo ""
echo "=============================================================================="
echo "🎉 DEPLOY CONCLUÍDO COM SUCESSO!"
echo "=============================================================================="
terraform output

echo ""
echo "💡 Dica: A máquina virtual leva cerca de 1 a 2 minutos para concluir a instalação"
echo "dos pacotes e iniciar o serviço de telemetria."
echo "Para acompanhar o log de inicialização na VM:"
eval "$(terraform output -raw startup_logs_command 2>/dev/null || echo '')"
