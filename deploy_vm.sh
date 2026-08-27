#!/usr/bin/env bash
# ==============================================================================
# Script de Deploy e Inicialização da Infraestrutura no GCP Compute Engine
# Cria VPC customizada, Subnet, Regras de Firewall e VM automaticamente
# ==============================================================================
set -euo pipefail

PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "demotelemetria")
REGION="us-central1"
ZONE="us-central1-a"
NETWORK_NAME="telemetry-vpc"
SUBNET_NAME="telemetry-subnet"
SUBNET_CIDR="10.10.0.0/24"
INSTANCE_NAME="telemetry-simulator-vm"
MACHINE_TYPE="e2-small"
REPO_URL="https://github.com/anselmodanilo-gcp/demo_telemetria.git"

echo "=============================================================================="
echo "🚀 DEPLOY DO SIMULADOR DE TELEMETRIA NO GOOGLE CLOUD COMPUTE ENGINE"
echo "Projeto GCP: ${PROJECT_ID} | Região: ${REGION} | Zona: ${ZONE}"
echo "=============================================================================="

# 1. Habilitar APIs necessárias
echo "1. Habilitando APIs do Google Cloud (Compute Engine)..."
gcloud services enable compute.googleapis.com --project="${PROJECT_ID}"

# 2. Criar VPC customizada se não existir
echo "2. Verificando / Criando VPC Network '${NETWORK_NAME}'..."
if ! gcloud compute networks describe "${NETWORK_NAME}" --project="${PROJECT_ID}" &>/dev/null; then
    gcloud compute networks create "${NETWORK_NAME}" \
        --project="${PROJECT_ID}" \
        --subnet-mode=custom \
        --mtu=1460 \
        --bgp-routing-mode=regional
    echo "✅ VPC '${NETWORK_NAME}' criada."
else
    echo "ℹ️  VPC '${NETWORK_NAME}' já existe."
fi

# 3. Criar Subnet se não existir
echo "3. Verificando / Criando Subnet '${SUBNET_NAME}' em ${REGION} (${SUBNET_CIDR})..."
if ! gcloud compute networks subnets describe "${SUBNET_NAME}" --region="${REGION}" --project="${PROJECT_ID}" &>/dev/null; then
    gcloud compute networks subnets create "${SUBNET_NAME}" \
        --project="${PROJECT_ID}" \
        --network="${NETWORK_NAME}" \
        --region="${REGION}" \
        --range="${SUBNET_CIDR}" \
        --enable-private-ip-google-access
    echo "✅ Subnet '${SUBNET_NAME}' criada."
else
    echo "ℹ️  Subnet '${SUBNET_NAME}' já existe."
fi

# 4. Criar Cloud Router e Cloud NAT para conectividade segura
echo "4. Verificando Cloud Router e Cloud NAT..."
if ! gcloud compute routers describe "${NETWORK_NAME}-router" --region="${REGION}" --project="${PROJECT_ID}" &>/dev/null; then
    gcloud compute routers create "${NETWORK_NAME}-router" \
        --project="${PROJECT_ID}" \
        --network="${NETWORK_NAME}" \
        --region="${REGION}"
fi

if ! gcloud compute routers nats describe "${NETWORK_NAME}-nat" --router="${NETWORK_NAME}-router" --region="${REGION}" --project="${PROJECT_ID}" &>/dev/null; then
    gcloud compute routers nats create "${NETWORK_NAME}-nat" \
        --project="${PROJECT_ID}" \
        --router="${NETWORK_NAME}-router" \
        --region="${REGION}" \
        --auto-allocate-nat-external-ips \
        --nat-all-subnet-ip-ranges
    echo "✅ Cloud NAT criado."
fi

# 5. Criar Regras de Firewall
echo "5. Configurando Regras de Firewall..."

# SSH & IAP
if ! gcloud compute firewall-rules describe "${NETWORK_NAME}-allow-ssh" --project="${PROJECT_ID}" &>/dev/null; then
    gcloud compute firewall-rules create "${NETWORK_NAME}-allow-ssh" \
        --project="${PROJECT_ID}" \
        --network="${NETWORK_NAME}" \
        --direction=INGRESS \
        --priority=1000 \
        --action=ALLOW \
        --rules=tcp:22 \
        --source-ranges=35.235.240.0/20,0.0.0.0/0 \
        --target-tags=telemetry-server
fi

# Dashboard Web (Porta 8000) e Ingestão REST
if ! gcloud compute firewall-rules describe "${NETWORK_NAME}-allow-telemetry-web" --project="${PROJECT_ID}" &>/dev/null; then
    gcloud compute firewall-rules create "${NETWORK_NAME}-allow-telemetry-web" \
        --project="${PROJECT_ID}" \
        --network="${NETWORK_NAME}" \
        --direction=INGRESS \
        --priority=1000 \
        --action=ALLOW \
        --rules=tcp:8000,tcp:80,tcp:443 \
        --source-ranges=0.0.0.0/0 \
        --target-tags=telemetry-server
fi

# ICMP
if ! gcloud compute firewall-rules describe "${NETWORK_NAME}-allow-icmp" --project="${PROJECT_ID}" &>/dev/null; then
    gcloud compute firewall-rules create "${NETWORK_NAME}-allow-icmp" \
        --project="${PROJECT_ID}" \
        --network="${NETWORK_NAME}" \
        --direction=INGRESS \
        --priority=1000 \
        --action=ALLOW \
        --rules=icmp \
        --source-ranges=0.0.0.0/0
fi

# 6. Provisionar Instância Compute Engine
echo "6. Provisionando VM Compute Engine '${INSTANCE_NAME}' (${MACHINE_TYPE} em ${ZONE})..."

if ! gcloud compute instances describe "${INSTANCE_NAME}" --zone="${ZONE}" --project="${PROJECT_ID}" &>/dev/null; then
    gcloud compute instances create "${INSTANCE_NAME}" \
        --project="${PROJECT_ID}" \
        --zone="${ZONE}" \
        --machine-type="${MACHINE_TYPE}" \
        --network="${NETWORK_NAME}" \
        --subnet="${SUBNET_NAME}" \
        --no-address \
        --tags=http-server,https-server,telemetry-server \
        --image-family=debian-12 \
        --image-project=debian-cloud \
        --boot-disk-size=20GB \
        --boot-disk-type=pd-balanced \
        --scopes=cloud-platform \
        --metadata=startup-script='#!/bin/bash
          set -euo pipefail
          exec > >(tee -a /var/log/telemetry_startup.log) 2>&1
          echo "Iniciando provisionamento do Telemetry Simulator..."
          export DEBIAN_FRONTEND=noninteractive
          apt-get update -y
          apt-get install -y git python3 python3-pip python3-venv curl sqlite3

          useradd --system --no-create-home --shell /bin/false telemetry || true

          APP_DIR="/opt/demo_telemetria"
          mkdir -p "${APP_DIR}"
          if [ ! -d "${APP_DIR}/.git" ]; then
              git clone https://github.com/anselmodanilo-gcp/demo_telemetria.git "${APP_DIR}"
          else
              cd "${APP_DIR}" && git pull origin main
          fi

          cd "${APP_DIR}"
          python3 -m venv "${APP_DIR}/.venv"
          "${APP_DIR}/.venv/bin/pip" install --upgrade pip
          "${APP_DIR}/.venv/bin/pip" install -r "${APP_DIR}/requirements.txt"

          if [ ! -f "${APP_DIR}/.env" ]; then
              cp "${APP_DIR}/.env.example" "${APP_DIR}/.env"
          fi

          chown -R telemetry:telemetry "${APP_DIR}"

          cp "${APP_DIR}/telemetry_service.service" /etc/systemd/system/telemetry_service.service
          systemctl daemon-reload
          systemctl enable telemetry_service
          systemctl restart telemetry_service
          echo "Telemetry Service iniciado com sucesso!"
        '
    echo "✅ VM '${INSTANCE_NAME}' criada com sucesso (segura via Cloud NAT e IAP)."
else
    echo "ℹ️  VM '${INSTANCE_NAME}' já existe."
fi

echo ""
echo "=============================================================================="
echo "🎉 DEPLOY CONCLUÍDO COM SUCESSO NA VPC '${NETWORK_NAME}'!"
echo "=============================================================================="
echo "🔒 A VM foi provisionada em rede privada segura com Cloud NAT."
echo ""
echo "🌐 Para abrir o Dashboard Web no seu navegador ou Cloud Shell:"
echo "   1. Abra um túnel de porta via IAP:"
echo "      gcloud compute ssh ${INSTANCE_NAME} --zone=${ZONE} --project=${PROJECT_ID} --tunnel-through-iap -- -L 8000:localhost:8000"
echo ""
echo "   2. No Cloud Shell, clique no botão 'Web Preview' (Visualização na Web) na porta 8000,"
echo "      ou abra no seu navegador local: http://localhost:8000"
echo ""
echo "📜 Para ver os logs da simulação em tempo real na VM:"
echo "   gcloud compute ssh ${INSTANCE_NAME} --zone=${ZONE} --project=${PROJECT_ID} --tunnel-through-iap --command='sudo journalctl -u telemetry_service -f'"
echo "=============================================================================="
