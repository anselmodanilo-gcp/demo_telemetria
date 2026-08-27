#!/usr/bin/env bash
# ==============================================================================
# Script de Deploy e Inicialização na VM do Google Cloud Compute Engine
# ==============================================================================
set -e

PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "seu-projeto-gcp")
ZONE="southamerica-east1-a" # São Paulo, Brasil
INSTANCE_NAME="vm-telemetria-frota-brasil"
MACHINE_TYPE="e2-medium"

echo "=============================================================================="
echo "🚀 DEPLOY DO SIMULADOR DE TELEMETRIA NO GOOGLE CLOUD COMPUTE ENGINE"
echo "Projeto GCP: ${PROJECT_ID} | Zona: ${ZONE}"
echo "=============================================================================="

# 1. Criação da Regra de Firewall para permitir acesso à porta 8000 (Dashboard e Ingestão)
echo "1. Configurando Regra de Firewall para porta 8000 (Dashboard Web / API)..."
gcloud compute firewall-rules create allow-telemetry-port-8000 \
    --project="${PROJECT_ID}" \
    --direction=INGRESS \
    --priority=1000 \
    --network=default \
    --action=ALLOW \
    --rules=tcp:8000 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=telemetry-server || echo "Regra de firewall já existe ou foi mantida."

# 2. Criação da VM no Compute Engine com Startup Script
echo "2. Provisionando instância no Compute Engine (${MACHINE_TYPE} em ${ZONE})..."
gcloud compute instances create "${INSTANCE_NAME}" \
    --project="${PROJECT_ID}" \
    --zone="${ZONE}" \
    --machine-type="${MACHINE_TYPE}" \
    --tags=http-server,https-server,telemetry-server \
    --image-family=debian-12 \
    --image-project=debian-cloud \
    --boot-disk-size=20GB \
    --boot-disk-type=pd-balanced \
    --metadata=startup-script='#!/bin/bash
      set -e
      apt-get update
      apt-get install -y git python3 python3-pip python3-venv curl sqlite3

      # Criar usuário de serviço
      useradd -m -s /bin/bash telemetry || true

      # Diretório da aplicação
      mkdir -p /opt/demo_telemetria
      cd /opt/demo_telemetria

      # Clonar ou sincronizar arquivos
      # git clone <seu-repo> . OU cópia direta
      python3 -m venv /opt/demo_telemetria/.venv
      /opt/demo_telemetria/.venv/bin/pip install --upgrade pip
      /opt/demo_telemetria/.venv/bin/pip install fastapi uvicorn pydantic pydantic-settings aiohttp requests python-dotenv websockets rich

      chown -R telemetry:telemetry /opt/demo_telemetria
      echo "Startup script finalizado com sucesso."
    '

echo ""
echo "=============================================================================="
echo "✅ VM Provisionada com Sucesso!"
echo "Para copiar o código local para a VM e iniciar o serviço:"
echo "  gcloud compute scp --recurse /home/anselmodanilo/dev/demo_telemetria/* ${INSTANCE_NAME}:/opt/demo_telemetria --zone=${ZONE}"
echo "  gcloud compute ssh ${INSTANCE_NAME} --zone=${ZONE} --command='sudo cp /opt/demo_telemetria/telemetry_service.service /etc/systemd/system/ && sudo systemctl daemon-reload && sudo systemctl enable --now telemetry_service'"
echo "=============================================================================="
