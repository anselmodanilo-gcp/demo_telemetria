#!/usr/bin/env bash
# ==============================================================================
# Script de Destruição da Infraestrutura Terraform no GCP
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

export PATH="${HOME}/.local/bin:${PATH}"

echo "=============================================================================="
echo "⚠️  ATENÇÃO: Este script irá destruir todos os recursos criados pelo Terraform:"
echo "  - Compute Engine VM (telemetry-simulator-vm)"
echo "  - Cloud Router e Cloud NAT"
echo "  - Regras de Firewall"
echo "  - VPC e Subnet em us-central1"
echo "  - Service Account e permissões IAM"
echo "=============================================================================="

read -p "Tem certeza que deseja prosseguir com a destruição? (s/N): " confirm
if [[ "$confirm" =~ ^[sS](im)?$ ]]; then
    terraform destroy -auto-approve
    echo "✅ Recursos destruídos com sucesso."
else
    echo "Operação cancelada pelo usuário."
fi
