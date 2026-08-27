"""
Main Entrypoint for Brazilian Commercial Fleet Telemetry Simulator.
Supports running in simulation-only, ingestion-server-only, or combined mode.
"""

import sys
import time
import signal
import asyncio
import argparse
import logging
import uvicorn
from rich.console import Console
from rich.table import Table
from rich.logging import RichHandler

from src.config import settings
from src.fleet import create_brazilian_fleet
from src.transmitter import TelemetryTransmitter
from src.server_mock import app

console = Console()

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True, show_path=False)]
)
logger = logging.getLogger("telemetry.main")


async def run_simulator_loop(interval_seconds: float = 4.0, speed_multiplier: float = 1.0):
    """
    Main asynchronous loop orchestrating telemetry generation across all 10 vehicles every 4 seconds.
    """
    fleet = create_brazilian_fleet()
    transmitter = TelemetryTransmitter()
    await transmitter.start()

    console.print(f"[bold green]▶ Iniciando Simulação de Telemetria para {len(fleet)} Veículos Brasileiros...[/bold green]")
    console.print(f"[cyan]Intervalo de Transmissão: {interval_seconds}s | Multiplicador de Velocidade: {speed_multiplier}x[/cyan]")
    console.print(f"[cyan]Modo de Envio: {settings.TRANSMISSION_MODE} -> {settings.TARGET_SERVER_URL}[/cyan]\n")

    iteration = 0
    try:
        while True:
            start_loop = time.time()
            iteration += 1

            table = Table(title=f"📡 Ciclo de Telemetria #{iteration} ({time.strftime('%H:%M:%S')})", show_header=True, header_style="bold magenta")
            table.add_column("ID / Placa", style="bold cyan", width=16)
            table.add_column("Veículo / Modelo", width=24)
            table.add_column("Velocidade", justify="right", width=12)
            table.add_column("Altitude", justify="right", width=10)
            table.add_column("RPM / Temp", justify="right", width=14)
            table.add_column("Combustível", justify="right", width=12)
            table.add_column("Localização Real", style="italic green", width=34)

            # Advance all vehicles in parallel
            for vehicle in fleet:
                elapsed = interval_seconds * speed_multiplier
                payload = vehicle.generate_telemetry(elapsed_seconds=elapsed)
                
                # Transmit asynchronously
                await transmitter.send(payload)

                # Format status row for CLI dashboard
                v = payload.vehicle
                loc = payload.location
                mech = payload.mechanical
                
                sp_str = f"{loc.speed_kmh:4.1f} km/h" if loc.speed_kmh > 0 else "[bold red]PARADO[/bold red]"
                table.add_row(
                    f"{v.vehicle_id}\n[dim]{v.plate}[/dim]",
                    f"{v.model}\n[dim]{v.driver_name.split()[0]}[/dim]",
                    sp_str,
                    f"{loc.altitude_m:4.0f} m",
                    f"{mech.rpm} rpm\n{mech.engine_temp_c:.1f}°C",
                    f"{mech.fuel_level_pct:.1f}%\n[dim]{mech.instantaneous_economy_km_l:.1f} km/l[/dim]",
                    f"{loc.current_road}\n[dim]{loc.current_city} - {loc.current_state}[/dim]"
                )

            console.print(table)
            
            # Precise timing control for exact 4-second intervals
            calc_time = time.time() - start_loop
            sleep_duration = max(0.05, interval_seconds - calc_time)
            await asyncio.sleep(sleep_duration)

    except asyncio.CancelledError:
        logger.info("Encerrando simulação de telemetria...")
    finally:
        await transmitter.stop()
        logger.info("Transmissor desconectado com sucesso.")


def run_server():
    """Start the ingestion server and web dashboard with uvicorn."""
    console.print(f"[bold green]▶ Iniciando Servidor de Ingestão & Dashboard em http://{settings.SERVER_HOST}:{settings.SERVER_PORT}...[/bold green]")
    uvicorn.run(
        app,
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        log_level="info",
        access_log=False
    )


async def run_combined_mode(interval_seconds: float = 4.0, speed_multiplier: float = 1.0):
    """Run both the FastAPI server and the fleet simulator concurrently in the same process."""
    config = uvicorn.Config(
        app,
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        log_level="warning",
        access_log=False
    )
    server = uvicorn.Server(config)

    console.print(f"[bold cyan]================================================================[/bold cyan]")
    console.print(f"[bold green]🚀 SERVIÇO DE TELEMETRIA GCP PRONTO & EXECUTANDO![/bold green]")
    console.print(f"[bold white]  • Dashboard Web Interativo: [/bold white][bold blue]http://localhost:{settings.SERVER_PORT}[/bold blue]")
    console.print(f"[bold white]  • Endpoint Ingestão REST:   [/bold white][bold blue]http://localhost:{settings.SERVER_PORT}/api/v1/telemetry[/bold blue]")
    console.print(f"[bold white]  • Endpoint WebSocket:       [/bold white][bold blue]ws://localhost:{settings.SERVER_PORT}/ws/telemetry[/bold blue]")
    console.print(f"[bold cyan]================================================================[/bold cyan]\n")

    # Launch server and simulation
    server_task = asyncio.create_task(server.serve())
    await asyncio.sleep(1.0)  # Give server a moment to bind port
    sim_task = asyncio.create_task(run_simulator_loop(interval_seconds, speed_multiplier))

    try:
        await asyncio.gather(server_task, sim_task)
    except asyncio.CancelledError:
        pass


def main():
    parser = argparse.ArgumentParser(description="Simulador de Telemetria de Frotas Comerciais - Brasil")
    parser.add_argument("command", choices=["all", "simulate", "server"], default="all", nargs="?",
                        help="Modo de execução: 'all' (servidor + simulador), 'simulate' (somente envio), 'server' (somente receptor)")
    parser.add_argument("--interval", "-i", type=float, default=settings.SIMULATION_INTERVAL_SECONDS,
                        help="Intervalo em segundos entre atualizações (padrão: 4.0s)")
    parser.add_argument("--speed", "-s", type=float, default=settings.SIMULATION_SPEED_MULTIPLIER,
                        help="Multiplicador de velocidade da física (padrão: 1.0x)")
    parser.add_argument("--target", "-t", type=str, default=settings.TARGET_SERVER_URL,
                        help="URL de destino HTTP para envio das telemetrias")
    parser.add_argument("--mode", "-m", choices=["http", "websocket", "console", "all"], default=settings.TRANSMISSION_MODE,
                        help="Protocolo de envio (padrão: http)")

    args = parser.parse_args()

    # Override settings from CLI
    settings.SIMULATION_INTERVAL_SECONDS = args.interval
    settings.SIMULATION_SPEED_MULTIPLIER = args.speed
    settings.TARGET_SERVER_URL = args.target
    settings.TRANSMISSION_MODE = args.mode

    if args.command == "server":
        run_server()
    elif args.command == "simulate":
        asyncio.run(run_simulator_loop(args.interval, args.speed))
    else:
        # Default: all (combined)
        asyncio.run(run_combined_mode(args.interval, args.speed))


if __name__ == "__main__":
    main()
