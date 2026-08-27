"""
Configuration module for the Telemetry Simulator.
Loads settings from environment variables, .env file, or command-line arguments.
"""

from typing import Literal, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Simulation Settings
    SIMULATION_INTERVAL_SECONDS: float = Field(
        default=4.0,
        description="Interval in seconds between telemetry emissions for each vehicle"
    )
    VEHICLE_COUNT: int = Field(
        default=10,
        description="Number of vehicles to simulate simultaneously"
    )
    SIMULATION_SPEED_MULTIPLIER: float = Field(
        default=1.0,
        description="Speed multiplier for simulation (e.g., 2.0 to move twice as fast)"
    )

    # Transmission / Server Settings
    TRANSMISSION_MODE: Literal["http", "websocket", "console", "all"] = Field(
        default="http",
        description="Method used to transmit telemetry frames"
    )
    TARGET_SERVER_URL: str = Field(
        default="http://127.0.0.1:8000/api/v1/telemetry",
        description="HTTP Endpoint to send telemetry JSON payloads via POST"
    )
    BATCH_TARGET_SERVER_URL: str = Field(
        default="http://127.0.0.1:8000/api/v1/telemetry/batch",
        description="HTTP Endpoint to send batched telemetry payloads"
    )
    WEBSOCKET_URL: str = Field(
        default="ws://127.0.0.1:8000/ws/telemetry",
        description="WebSocket URL for real-time telemetry streaming"
    )
    AUTH_BEARER_TOKEN: Optional[str] = Field(
        default=None,
        description="Optional Bearer token for authenticating with the telemetry server"
    )

    # Resiliency / Offline Buffer Settings
    ENABLE_OFFLINE_BUFFER: bool = Field(
        default=True,
        description="Whether to buffer telemetry messages locally in SQLite when the server is unreachable"
    )
    OFFLINE_BUFFER_DB: str = Field(
        default="telemetry_offline_buffer.db",
        description="SQLite database file path for storing buffered offline payloads"
    )
    BUFFER_FLUSH_BATCH_SIZE: int = Field(
        default=25,
        description="Number of buffered payloads to send when connection is restored"
    )
    HTTP_TIMEOUT_SECONDS: float = Field(
        default=3.5,
        description="Timeout for HTTP requests before falling back to local buffer"
    )

    # Google Maps Integration (Optional)
    GOOGLE_MAPS_API_KEY: Optional[str] = Field(
        default=None,
        description="Google Maps Platform API Key for dynamic Directions & Elevation"
    )

    # Built-in Mock Server & Dashboard Settings
    SERVER_HOST: str = Field(default="0.0.0.0", description="Mock server listen host")
    SERVER_PORT: int = Field(default=8000, description="Mock server listen port")
    SERVER_WORKERS: int = Field(default=1, description="Uvicorn worker count")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Application log level")


settings = Settings()
