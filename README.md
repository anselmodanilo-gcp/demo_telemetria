# 🚛 Plataforma de Simulação de Telemetria de Frotas Comerciais (Brasil)

Sistema profissional de geração, simulação física e transmissão de telemetria avançada de veículos comerciais em rotas reais pelo Brasil. Desenvolvido para simular operações logísticas de grande porte, testes de arquitetura de dados e homologação de pipelines em nuvem no **Google Cloud Compute Engine (GCE)**, **Google Cloud Run**, **BigQuery** e **Pub/Sub**.

---

## 🌟 Principais Recursos

- **10 Veículos Únicos & Frotas Distintas**: Cada veículo possui perfil mecânico, modelo, categoria, capacidade de carga, telemetria de pneus (TPMS) e motorista individual.
- **Rotas Reais no Brasil com Topografia e Altitude**: Trajetos reais cobrindo rodovias estratégicas (BR-116 Régis Bittencourt, BR-163 Corredor do Agro, BR-116 Presidente Dutra, BR-381 Fernão Dias, Estradas de Mineração em MG, etc.).
- **Física e Mecânica Realista**:
  - Ajuste de velocidade por inclinação/subida de serra (efeito rampa e perda de velocidade em caminhões pesados).
  - Variação térmica do bloco do motor, óleo e líquido de arrefecimento proporcional ao esforço/carga (0-100%).
  - Cálculo de consumo de combustível instantâneo (L/h e km/L) e esgotamento gradual do tanque.
  - Aquecimento de pneus e pressão dinâmica em PSI (TPMS) por eixo e carreta.
  - Sensores especializados por tipo de carga: **Baú frigorífico (-18°C)**, **Tanque de combustível inflamável (pressão de vapor)**, **Ambulância UTI móvel (sirene/giroflex)**, **Caçamba basculante de minério**, **Ônibus executivo** e **Caminhão Cegonha**.
- **Taxa de Atualização de 4 Segundos**: Emissão contínua de pacotes a cada 4 segundos com cálculo de interpolação geodésica suave.
- **Resiliência e Buffer Offline SQLite**: Se o servidor de destino cair ou houver oscilação de rede, os pacotes são salvos em SQLite local e descarregados automaticamente em lote assim que a conexão retornar.
- **Servidor Receptor & Dashboard Web em Tempo Real Embutido**: Interface interativa em Leaflet.js + Tailwind CSS com mapa escuro do Brasil, marcadores animados, painel de instrumentos e streaming via WebSocket.
- **Pronto para Deploy no GCP Compute Engine**: Inclui scripts de automação, arquivo de serviço `systemd`, `Dockerfile` e `docker-compose.yml`.

---

## 🚗 A Frota dos 10 Veículos Simulados

| ID | Placa | Categoria | Modelo | Motorista | Rota Real / Rodovia | Perfil de Operação |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BR-VH-101** | `BRA2E19` | Frigorífico Pesado | Scania R450 6x2 | Carlos Eduardo Silveira | São Paulo ➔ Curitiba (BR-116 Régis) | Baú refrigerado a -18°C / Serra do Cafezal |
| **BR-VH-102** | `RND8F32` | Bitrem 9 Eixos | Volvo FH 540 8x4 | Marcos Antonio Rezende | Rondonópolis (MT) ➔ Campo Grande (MS) (BR-163) | Escoamento de Soja (48t) / Corredor Agro |
| **BR-VH-103** | `SPK4A77` | VUC Urbano | MB Accelo 1016 | Rodrigo de Oliveira | Distribuição Grande SP (Ceagesp ➔ Jardins) | Entregas urbanas fracionadas / ZMRC |
| **BR-VH-104** | `RJL9D45` | Furgão Carga | MB Sprinter 416 | Felipe Nascimento Costa | Rio de Janeiro ➔ Cabo Frio (Ponte / RJ-124) | Logística expressa e-commerce / offshore |
| **BR-VH-105** | `EXP1H90` | Ônibus Executivo | Marcopolo Paradiso G8 / K410 | Valdir Santos Moreira | SP (Tietê) ➔ RJ (Novo Rio) (BR-116 Dutra) | Transporte interestadual de passageiros |
| **BR-VH-106** | `PLN3C61` | Caminhão Tanque | DAF XF 530 6x4 | Gilberto Mendes Prado | Paulínia (REPLAN) ➔ Bauru (SP-300) | Combustível Granel Líquido (Hazmat) |
| **BR-VH-107** | `MGH7B14` | Picape Apoio 4x4 | Toyota Hilux 2.8 D-4D | Lucas Henrique Souza | BH ➔ Ouro Preto ➔ Cons. Lafaiete (BR-356) | Manutenção técnica / Terreno montanhoso |
| **BR-VH-108** | `VAL5M22` | Basculante Mineração | MB Actros 4844 8x4 | José Roberto Fagundes | Complexo Cauê ➔ Usina Itabira MG | Carga pesada de minério de ferro em cavas |
| **BR-VH-109** | `SAM1U92` | Ambulância UTI | Renault Master 2.3 dCi | Dr. André Brandão / Enf. Paulo | Brasília DF (Hospital de Base ➔ Lago Sul) | Emergência médica / Sirene e giroflex ativos |
| **BR-VH-110** | `BTM6K88` | Cegonha 11 Carros | Volvo VM 330 6x2 | Claudio Barbosa Lima | Betim MG ➔ Atibaia SP (BR-381 Fernão Dias) | Transporte de veículos automotores novos |

---

## 📊 Estrutura do Payload de Telemetria (JSON)

Exemplo de frame emitido a cada 4 segundos:

```json
{
  "message_id": "9f9a2f3a-932d-419b-a320-c28f099238aa",
  "timestamp": "2026-08-27T14:40:00.000000Z",
  "sequence_number": 420,
  "vehicle": {
    "vehicle_id": "BR-VH-101",
    "plate": "BRA2E19",
    "vin": "9BWZZZ377VT001011",
    "fleet_name": "TransLog Brasil Frio",
    "category": "HEAVY_TRUCK_REEFER",
    "manufacturer": "Scania",
    "model": "R450 6x2 Highline",
    "manufacture_year": 2024,
    "driver_id": "DRV-0019",
    "driver_name": "Carlos Eduardo Silveira"
  },
  "location": {
    "latitude": -24.120000,
    "longitude": -47.230000,
    "altitude_m": 120.0,
    "heading_deg": 218.4,
    "speed_kmh": 60.0,
    "odometer_km": 184542.8,
    "trip_distance_km": 22.8,
    "satellite_count": 18,
    "hdop": 0.85,
    "current_road": "Serra do Cafezal - Curva da Ferradura",
    "current_city": "Miracatu",
    "current_state": "SP"
  },
  "mechanical": {
    "ignition": true,
    "engine_status": "RUNNING",
    "rpm": 1420,
    "gear": 8,
    "throttle_pedal_pct": 38.5,
    "brake_pedal_pct": 0.0,
    "engine_load_pct": 52.0,
    "engine_temp_c": 89.2,
    "coolant_temp_c": 86.4,
    "oil_temp_c": 93.1,
    "oil_pressure_bar": 3.8,
    "battery_voltage_v": 28.3,
    "alternator_current_a": 60.4,
    "fuel_level_pct": 78.4,
    "fuel_volume_liters": 470.4,
    "fuel_rate_l_per_h": 21.6,
    "instantaneous_economy_km_l": 2.78,
    "adblue_level_pct": 88.5,
    "total_engine_hours": 3355.3
  },
  "tires": [
    { "position": "Eixo1_Esq", "pressure_psi": 112.5, "temperature_c": 44.2, "status": "NORMAL" },
    { "position": "Eixo1_Dir", "pressure_psi": 112.6, "temperature_c": 44.5, "status": "NORMAL" },
    { "position": "Eixo2_Esq_Ext", "pressure_psi": 113.1, "temperature_c": 46.8, "status": "NORMAL" },
    { "position": "Eixo2_Dir_Ext", "pressure_psi": 113.0, "temperature_c": 46.5, "status": "NORMAL" }
  ],
  "safety": {
    "seatbelt_fastened": true,
    "parking_brake_engaged": false,
    "cruise_control_active": true,
    "abs_active": false,
    "esp_active": false,
    "steering_angle_deg": 1.2,
    "accel_longitudinal_g": 0.02,
    "accel_lateral_g": 0.01,
    "hazard_lights": false,
    "panic_button_pressed": false,
    "doors_locked": true
  },
  "cargo": {
    "cargo_type": "CARGA_FRIGORIFICADA_ALIMENTOS",
    "cargo_weight_kg": 24500.0,
    "max_payload_kg": 28000.0,
    "reefer_temperature_c": -18.2,
    "reefer_setpoint_c": -18.0,
    "reefer_unit_running": true,
    "reefer_door_open": false
  },
  "diagnostics": {
    "mil_indicator_light": false,
    "active_dtcs": [],
    "service_distance_remaining_km": 14977.2,
    "brake_pad_wear_pct": 28.5,
    "air_filter_restriction_kpa": 1.3
  },
  "device": {
    "tracker_serial": "TK-BRVH101",
    "firmware_version": "v3.4.12-GCP",
    "gsm_signal_csq": 29,
    "network_carrier": "Vivo Empresas 5G / IoT",
    "internal_battery_pct": 99.2,
    "buffer_queue_count": 0
  }
}
```

---

## 🚀 Como Executar Localmente

### 1. Criar e Ativar Ambiente Virtual
```bash
cd /home/anselmodanilo/dev/demo_telemetria
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Modos de Execução

#### A. Modo Completo (Servidor Ingestão + Dashboard Web + Simulador dos 10 Veículos)
```bash
python main.py all
```
Abra seu navegador em: **`http://localhost:8000`** para ver o mapa do Brasil com todos os 10 veículos transmitindo telemetria em tempo real!

#### B. Modo Apenas Simulador (Enviando para um Servidor Remoto / GCP)
```bash
python main.py simulate --target http://SEU_IP_OU_DOMINIO/api/v1/telemetry --interval 4.0
```

#### C. Modo Apenas Servidor Receptor & Dashboard
```bash
python main.py server
```

### 3. Rodando os Testes Automatizados
```bash
pytest
```

---

## 🐳 Executando com Docker

### Docker Compose
```bash
docker compose up --build -d
```
Acesse `http://localhost:8000`.

---

## ☁️ Deploy no Google Cloud Compute Engine (VM)

### Passo 1: Executar script de provisionamento
```bash
chmod +x deploy_vm.sh
./deploy_vm.sh
```

### Passo 2: Copiar código para a VM
```bash
gcloud compute scp --recurse . vm-telemetria-frota-brasil:/opt/demo_telemetria --zone=southamerica-east1-a
```

### Passo 3: Ativar o Serviço Systemd na VM
```bash
gcloud compute ssh vm-telemetria-frota-brasil --zone=southamerica-east1-a --command="
  sudo cp /opt/demo_telemetria/telemetry_service.service /etc/systemd/system/
  sudo systemctl daemon-reload
  sudo systemctl enable telemetry_service
  sudo systemctl start telemetry_service
  sudo systemctl status telemetry_service
"
```

Acesse o IP público da sua VM na porta 8000: `http://<EXTERNAL_IP>:8000`

---

## 📁 Estrutura de Arquivos

```
demo_telemetria/
├── .env.example                # Configurações de ambiente
├── Dockerfile                  # Imagem container para nuvem
├── docker-compose.yml          # Orquestração local
├── deploy_vm.sh                # Script de provisionamento GCP Compute Engine
├── telemetry_service.service   # Arquivo de serviço Linux systemd
├── requirements.txt            # Dependências Python
├── pytest.ini                  # Configurações do Pytest
├── main.py                     # Ponto de entrada CLI
├── README.md                   # Documentação detalhada
├── src/
│   ├── __init__.py
│   ├── config.py               # Configurações Pydantic Settings
│   ├── models.py               # Modelos Pydantic de Telemetria
│   ├── routes.py               # 10 Rotas Reais Brasileiras com Altitudes
│   ├── maps_integration.py     # Integração Google Maps & Geodésica
│   ├── physics.py              # Motor de física, consumo e termodinâmica
│   ├── vehicle.py              # Ator de simulação de veículo
│   ├── fleet.py                # Gerenciador da frota dos 10 veículos
│   ├── transmitter.py          # Transmissor HTTP/WS com buffer SQLite
│   └── server_mock.py          # Servidor FastAPI + Dashboard Web Leaflet
└── tests/
    └── test_simulation.py      # Testes automatizados
```
