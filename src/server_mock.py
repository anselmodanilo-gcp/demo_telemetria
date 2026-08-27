"""
Telemetry Receiver Server & Real-Time Monitoring Web Dashboard.
Built with FastAPI, WebSockets, and an interactive HTML5/Leaflet.js UI.
"""

import os
import json
import asyncio
from typing import Dict, List, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from src.models import TelemetryPayload, TelemetryBatchPayload

app = FastAPI(
    title="Fleet Telemetry Ingestion Platform",
    description="High-Throughput Ingestion Server & Live Dashboard for Commercial Fleets in Brazil",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for latest state and breadcrumb trails
latest_telemetry_store: Dict[str, Dict[str, Any]] = {}
vehicle_history_trails: Dict[str, List[Dict[str, Any]]] = {}
connected_websockets: List[WebSocket] = []
MAX_HISTORY_POINTS = 50


@app.get("/health")
async def health_check():
    """GCP Health Probe / Load Balancer Endpoint."""
    return {"status": "healthy", "service": "telemetry-ingestion-api", "active_vehicles": len(latest_telemetry_store)}


@app.post("/api/v1/telemetry", status_code=201)
async def receive_telemetry(payload: TelemetryPayload):
    """
    Ingest a single real-time vehicle telemetry frame.
    """
    data = payload.model_dump()
    vehicle_id = payload.vehicle.vehicle_id

    # Store latest snapshot
    latest_telemetry_store[vehicle_id] = data

    # Record breadcrumb history
    if vehicle_id not in vehicle_history_trails:
        vehicle_history_trails[vehicle_id] = []
    
    trail = vehicle_history_trails[vehicle_id]
    trail.append({
        "lat": payload.location.latitude,
        "lon": payload.location.longitude,
        "alt_m": payload.location.altitude_m,
        "speed_kmh": payload.location.speed_kmh,
        "time": payload.timestamp
    })
    if len(trail) > MAX_HISTORY_POINTS:
        trail.pop(0)

    # Broadcast to all connected web dashboards
    await broadcast_websocket(data)

    return {"status": "success", "message_id": payload.message_id, "vehicle_id": vehicle_id}


@app.post("/api/v1/telemetry/batch", status_code=201)
async def receive_telemetry_batch(batch: TelemetryBatchPayload):
    """
    Ingest batched telemetry frames (useful for offline recovery / replay).
    """
    for record in batch.records:
        await receive_telemetry(record)
    return {"status": "success", "processed_records": batch.total_records}


@app.get("/api/v1/vehicles")
async def get_all_vehicles():
    """Get latest telemetry snapshot of all active fleet vehicles."""
    return {"vehicles": list(latest_telemetry_store.values())}


@app.get("/api/v1/vehicles/{vehicle_id}/history")
async def get_vehicle_history(vehicle_id: str):
    """Get recent GPS breadcrumb trail for a specific vehicle."""
    if vehicle_id not in vehicle_history_trails:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {"vehicle_id": vehicle_id, "history": vehicle_history_trails[vehicle_id]}


@app.websocket("/ws/telemetry")
async def websocket_telemetry_stream(websocket: WebSocket):
    """WebSocket endpoint for real-time live browser streaming."""
    await websocket.accept()
    connected_websockets.append(websocket)
    
    # Send initial current state of all vehicles upon connection
    for vehicle_data in latest_telemetry_store.values():
        await websocket.send_text(json.dumps(vehicle_data))

    try:
        while True:
            # Handle any incoming client messages or heartbeats
            data_str = await websocket.receive_text()
            try:
                data_json = json.loads(data_str)
                # If a client sends a telemetry frame directly via websocket
                if "vehicle" in data_json and "location" in data_json:
                    parsed = TelemetryPayload.model_validate(data_json)
                    await receive_telemetry(parsed)
            except Exception:
                pass
    except WebSocketDisconnect:
        if websocket in connected_websockets:
            connected_websockets.remove(websocket)


async def broadcast_websocket(data: Dict[str, Any]):
    """Push telemetry frame to all live web UI clients."""
    if not connected_websockets:
        return
    msg = json.dumps(data)
    dead_sockets = []
    for ws in connected_websockets:
        try:
            await ws.send_text(msg)
        except Exception:
            dead_sockets.append(ws)
    for ws in dead_sockets:
        if ws in connected_websockets:
            connected_websockets.remove(ws)


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Live interactive web dashboard with Leaflet map and telemetry gauges."""
    return HTMLResponse(content=HTML_DASHBOARD_TEMPLATE)


HTML_DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GCP Fleet Telemetry Platform - Brasil</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Leaflet CSS & JS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <!-- FontAwesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" />
    <style>
        #map { height: calc(100vh - 80px); }
        .custom-marker {
            background-color: #2563eb;
            border: 2px solid #ffffff;
            border-radius: 50%;
            color: white;
            text-align: center;
            font-size: 11px;
            font-weight: bold;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
        }
        .custom-marker:hover {
            transform: scale(1.2);
            background-color: #10b981;
        }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-thumb { background: #374151; border-radius: 3px; }
    </style>
</head>
<body class="bg-gray-950 text-gray-100 flex flex-col h-screen overflow-hidden">
    <!-- Header -->
    <header class="bg-gray-900 border-b border-gray-800 px-6 py-3 flex items-center justify-between shadow-md">
        <div class="flex items-center space-x-3">
            <div class="p-2 bg-blue-600/20 text-blue-400 rounded-lg border border-blue-500/30">
                <i class="fa-solid fa-satellite-dish text-xl animate-pulse"></i>
            </div>
            <div>
                <h1 class="font-bold text-lg text-white tracking-wide">Plataforma de Telemetria de Frotas Brasil</h1>
                <p class="text-xs text-gray-400">Google Cloud Compute Engine Simulator • 4s Sync • Telemetria Avançada</p>
            </div>
        </div>
        <div class="flex items-center space-x-6">
            <div class="flex items-center space-x-2">
                <span class="inline-block w-3 h-3 bg-green-500 rounded-full animate-ping"></span>
                <span class="text-xs text-green-400 font-semibold" id="conn-status">Conectado ao Servidor</span>
            </div>
            <div class="bg-gray-800 px-3 py-1.5 rounded-md border border-gray-700 text-xs">
                <span class="text-gray-400">Total Veículos:</span>
                <span class="font-bold text-blue-400 text-sm ml-1" id="vehicle-count">0</span> / 10
            </div>
            <div class="bg-gray-800 px-3 py-1.5 rounded-md border border-gray-700 text-xs">
                <span class="text-gray-400">Mensagens Recebidas:</span>
                <span class="font-bold text-emerald-400 text-sm ml-1" id="msg-count">0</span>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <div class="flex flex-1 overflow-hidden">
        <!-- Sidebar: Vehicle List & Telemetry Cards -->
        <aside class="w-96 bg-gray-900 border-r border-gray-800 overflow-y-auto flex flex-col p-4 space-y-3">
            <div class="flex items-center justify-between pb-2 border-b border-gray-800">
                <h2 class="text-sm font-semibold text-gray-300 uppercase tracking-wider">Veículos em Trânsito</h2>
                <span class="text-xs text-blue-400 font-mono" id="last-update">--:--:--</span>
            </div>
            <div id="vehicle-cards-container" class="space-y-3">
                <!-- Vehicle Cards injected here -->
                <div class="p-4 bg-gray-800/50 rounded-lg border border-gray-700/50 text-center text-xs text-gray-400">
                    Aguardando primeiros pacotes de telemetria...
                </div>
            </div>
        </aside>

        <!-- Center: Interactive Map -->
        <main class="flex-1 relative">
            <div id="map"></div>
        </main>
    </div>

    <!-- Scripts -->
    <script>
        // Initialize Map centered on Brazil
        const map = L.map('map', {
            zoomControl: true
        }).setView([-15.7801, -47.9292], 5);

        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; CartoDB | Telemetria GCP',
            maxZoom: 19
        }).addTo(map);

        const vehicleMarkers = {};
        const vehicleTrails = {};
        let totalMessagesReceived = 0;

        function getCategoryIcon(category) {
            switch(category) {
                case 'HEAVY_TRUCK_REEFER': return 'fa-snowflake';
                case 'BITREM_AGRO': return 'fa-wheat-awn';
                case 'VUC_URBAN': return 'fa-truck-ramp-box';
                case 'VAN_CARGO': return 'fa-van-shuttle';
                case 'COACH_BUS': return 'fa-bus';
                case 'FUEL_TANKER': return 'fa-gas-pump';
                case 'FLEET_PICKUP': return 'fa-truck-pickup';
                case 'MINING_TRUCK': return 'fa-mountain';
                case 'AMBULANCE_ICU': return 'fa-truck-medical';
                case 'CAR_CARRIER': return 'fa-car-side';
                default: return 'fa-truck';
            }
        }

        function updateVehicleOnMap(data) {
            const vId = data.vehicle.vehicle_id;
            const lat = data.location.latitude;
            const lon = data.location.longitude;
            const heading = data.location.heading_deg;
            const speed = data.location.speed_kmh;
            const iconClass = getCategoryIcon(data.vehicle.category);

            // Update or create marker
            if (!vehicleMarkers[vId]) {
                const iconHtml = `
                    <div class="custom-marker w-8 h-8 flex items-center justify-center">
                        <i class="fa-solid ${iconClass}"></i>
                    </div>
                `;
                const customIcon = L.divIcon({
                    html: iconHtml,
                    className: '',
                    iconSize: [32, 32],
                    iconAnchor: [16, 16]
                });
                const marker = L.marker([lat, lon], { icon: customIcon }).addTo(map);
                marker.bindPopup(`
                    <div class="p-2 text-xs text-gray-900 font-sans leading-relaxed">
                        <b class="text-sm text-blue-700">${data.vehicle.vehicle_id} - ${data.vehicle.plate}</b><br>
                        <b>Modelo:</b> ${data.vehicle.manufacturer} ${data.vehicle.model}<br>
                        <b>Motorista:</b> ${data.vehicle.driver_name}<br>
                        <b>Velocidade:</b> ${speed} km/h | <b>Altitude:</b> ${data.location.altitude_m}m<br>
                        <b>Local:</b> ${data.location.current_road}, ${data.location.current_city} - ${data.location.current_state}<br>
                        <b>RPM:</b> ${data.mechanical.rpm} | <b>Temp Motor:</b> ${data.mechanical.engine_temp_c}°C
                    </div>
                `);
                vehicleMarkers[vId] = marker;
                vehicleTrails[vId] = L.polyline([[lat, lon]], { color: '#3b82f6', weight: 3, opacity: 0.7 }).addTo(map);
            } else {
                vehicleMarkers[vId].setLatLng([lat, lon]);
                vehicleMarkers[vId].getPopup().setContent(`
                    <div class="p-2 text-xs text-gray-900 font-sans leading-relaxed">
                        <b class="text-sm text-blue-700">${data.vehicle.vehicle_id} - ${data.vehicle.plate}</b><br>
                        <b>Modelo:</b> ${data.vehicle.manufacturer} ${data.vehicle.model}<br>
                        <b>Motorista:</b> ${data.vehicle.driver_name}<br>
                        <b>Velocidade:</b> ${speed} km/h | <b>Altitude:</b> ${data.location.altitude_m}m<br>
                        <b>Local:</b> ${data.location.current_road}, ${data.location.current_city} - ${data.location.current_state}<br>
                        <b>RPM:</b> ${data.mechanical.rpm} | <b>Temp Motor:</b> ${data.mechanical.engine_temp_c}°C
                    </div>
                `);
                vehicleTrails[vId].addLatLng([lat, lon]);
            }
        }

        const vehiclesState = {};

        function renderVehicleCards() {
            const container = document.getElementById('vehicle-cards-container');
            const vIds = Object.keys(vehiclesState).sort();
            document.getElementById('vehicle-count').textContent = vIds.length;

            if (vIds.length === 0) return;

            let html = '';
            vIds.forEach(id => {
                const d = vehiclesState[id];
                const icon = getCategoryIcon(d.vehicle.category);
                const isRunning = d.location.speed_kmh > 0;
                const speedBadge = isRunning 
                    ? `<span class="bg-blue-900/60 text-blue-300 border border-blue-700/50 px-2 py-0.5 rounded text-xs font-mono font-bold">${d.location.speed_kmh} km/h</span>`
                    : `<span class="bg-amber-900/60 text-amber-300 border border-amber-700/50 px-2 py-0.5 rounded text-xs font-mono font-bold">PARADO</span>`;

                html += `
                    <div class="p-3 bg-gray-800/80 hover:bg-gray-800 rounded-lg border border-gray-700 transition cursor-pointer" onclick="map.panTo([${d.location.latitude}, ${d.location.longitude}])">
                        <div class="flex items-center justify-between mb-1.5">
                            <div class="flex items-center space-x-2">
                                <i class="fa-solid ${icon} text-blue-400 text-sm"></i>
                                <span class="font-bold text-sm text-white">${d.vehicle.vehicle_id}</span>
                                <span class="text-xs bg-gray-700 text-gray-300 px-1.5 py-0.2 rounded font-mono">${d.vehicle.plate}</span>
                            </div>
                            ${speedBadge}
                        </div>
                        <div class="text-xs text-gray-400 truncate mb-1">
                            ${d.vehicle.model} • ${d.vehicle.driver_name}
                        </div>
                        <div class="text-xs text-emerald-400 truncate mb-2">
                            <i class="fa-solid fa-location-dot text-gray-500 mr-1"></i>${d.location.current_road}, ${d.location.current_city}-${d.location.current_state}
                        </div>
                        
                        <!-- Telemetry Grid -->
                        <div class="grid grid-cols-3 gap-1.5 text-[11px] bg-gray-900/80 p-2 rounded border border-gray-800 font-mono">
                            <div>
                                <span class="text-gray-500 block text-[10px]">ALTITUDE</span>
                                <span class="text-gray-200 font-semibold">${d.location.altitude_m}m</span>
                            </div>
                            <div>
                                <span class="text-gray-500 block text-[10px]">RPM</span>
                                <span class="text-gray-200 font-semibold">${d.mechanical.rpm}</span>
                            </div>
                            <div>
                                <span class="text-gray-500 block text-[10px]">TEMP MOTOR</span>
                                <span class="text-gray-200 font-semibold">${d.mechanical.engine_temp_c}°C</span>
                            </div>
                            <div>
                                <span class="text-gray-500 block text-[10px]">COMBUSTÍVEL</span>
                                <span class="text-amber-400 font-semibold">${d.mechanical.fuel_level_pct}%</span>
                            </div>
                            <div>
                                <span class="text-gray-500 block text-[10px]">CONSUMO</span>
                                <span class="text-gray-200 font-semibold">${d.mechanical.instantaneous_economy_km_l} km/l</span>
                            </div>
                            <div>
                                <span class="text-gray-500 block text-[10px]">BATERIA</span>
                                <span class="text-gray-200 font-semibold">${d.mechanical.battery_voltage_v}V</span>
                            </div>
                        </div>
                    </div>
                `;
            });

            container.innerHTML = html;
        }

        // WebSocket Connection
        function connectWebSocket() {
            const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${proto}//${window.location.host}/ws/telemetry`;
            const ws = new WebSocket(wsUrl);

            ws.onopen = () => {
                document.getElementById('conn-status').textContent = 'Conectado ao Servidor (Tempo Real)';
                document.getElementById('conn-status').className = 'text-xs text-green-400 font-semibold';
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    totalMessagesReceived++;
                    document.getElementById('msg-count').textContent = totalMessagesReceived;
                    document.getElementById('last-update').textContent = new Date().toLocaleTimeString();

                    vehiclesState[data.vehicle.vehicle_id] = data;
                    updateVehicleOnMap(data);
                    renderVehicleCards();
                } catch (e) {
                    console.error('Error parsing WS message', e);
                }
            };

            ws.onclose = () => {
                document.getElementById('conn-status').textContent = 'Reconectando...';
                document.getElementById('conn-status').className = 'text-xs text-amber-400 font-semibold';
                setTimeout(connectWebSocket, 2000);
            };
        }

        connectWebSocket();
    </script>
</body>
</html>
"""
