"""
Resilient Telemetry Transmitter with HTTP, WebSocket, and Local SQLite Offline Buffering.
Ensures zero data loss during network dropouts or remote server downtime.
"""

import json
import sqlite3
import asyncio
import logging
from typing import Optional, List, Dict, Any
import aiohttp
import websockets
from src.config import settings
from src.models import TelemetryPayload, TelemetryBatchPayload

logger = logging.getLogger("telemetry.transmitter")


class OfflineBufferDB:
    """
    Local SQLite store for spooling unsent telemetry frames during server disconnection.
    """
    def __init__(self, db_path: str = "telemetry_offline_buffer.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS buffered_telemetry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT UNIQUE,
                    vehicle_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    payload_json TEXT
                )
            """)
            conn.commit()

    def buffer_message(self, payload: TelemetryPayload):
        """Save a failed telemetry frame to local SQLite."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO buffered_telemetry (message_id, vehicle_id, payload_json)
                    VALUES (?, ?, ?)
                """, (payload.message_id, payload.vehicle.vehicle_id, payload.model_dump_json()))
                conn.commit()
                logger.debug("Buffered message %s for vehicle %s", payload.message_id, payload.vehicle.vehicle_id)
        except Exception as e:
            logger.error("Error writing to local SQLite buffer: %s", e)

    def fetch_batch(self, limit: int = 25) -> List[Dict[str, Any]]:
        """Retrieve up to `limit` stored messages for flushing."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, message_id, payload_json FROM buffered_telemetry ORDER BY id ASC LIMIT ?", (limit,))
                rows = cursor.fetchall()
                return [{"db_id": r[0], "message_id": r[1], "payload_json": r[2]} for r in rows]
        except Exception as e:
            logger.error("Error reading from local SQLite buffer: %s", e)
            return []

    def delete_messages(self, db_ids: List[int]):
        """Remove successfully forwarded messages from buffer."""
        if not db_ids:
            return
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                placeholders = ",".join("?" * len(db_ids))
                cursor.execute(f"DELETE FROM buffered_telemetry WHERE id IN ({placeholders})", db_ids)
                conn.commit()
        except Exception as e:
            logger.error("Error deleting from local SQLite buffer: %s", e)

    def get_count(self) -> int:
        """Count pending buffered frames."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM buffered_telemetry")
                return cursor.fetchone()[0]
        except Exception:
            return 0


class TelemetryTransmitter:
    """
    Asynchronous network transmitter capable of HTTP POST, WebSockets, and offline recovery.
    """
    def __init__(self):
        self.mode = settings.TRANSMISSION_MODE
        self.target_url = settings.TARGET_SERVER_URL
        self.batch_target_url = settings.BATCH_TARGET_SERVER_URL
        self.websocket_url = settings.WEBSOCKET_URL
        self.timeout = aiohttp.ClientTimeout(total=settings.HTTP_TIMEOUT_SECONDS)
        self.offline_buffer = OfflineBufferDB(settings.OFFLINE_BUFFER_DB) if settings.ENABLE_OFFLINE_BUFFER else None

        self._session: Optional[aiohttp.ClientSession] = None
        self._ws_connection: Optional[websockets.WebSocketClientProtocol] = None
        
        # Transmission Stats
        self.total_sent = 0
        self.total_buffered = 0
        self.total_failed = 0
        self.is_connected = True

    async def start(self):
        """Initialize persistent HTTP connection pool."""
        headers = {"Content-Type": "application/json"}
        if settings.AUTH_BEARER_TOKEN:
            headers["Authorization"] = f"Bearer {settings.AUTH_BEARER_TOKEN}"
        self._session = aiohttp.ClientSession(timeout=self.timeout, headers=headers)

    async def stop(self):
        """Gracefully close all network sessions."""
        if self._session and not self._session.closed:
            await self._session.close()
        if self._ws_connection:
            await self._ws_connection.close()

    async def send(self, payload: TelemetryPayload) -> bool:
        """
        Send a single telemetry frame according to configured mode.
        """
        success = False

        if self.mode in ("http", "all"):
            http_ok = await self._send_http(payload)
            success = success or http_ok

        if self.mode in ("websocket", "all"):
            ws_ok = await self._send_websocket(payload)
            success = success or ws_ok

        if self.mode == "console":
            self._print_console(payload)
            success = True

        if not success and self.offline_buffer:
            self.offline_buffer.buffer_message(payload)
            self.total_buffered += 1
            if self.is_connected:
                logger.warning("Target server unreachable. Spooling to local SQLite buffer.")
                self.is_connected = False
        elif success and not self.is_connected:
            self.is_connected = True
            logger.info("Connection to telemetry server restored! Flushing offline buffer...")
            asyncio.create_task(self.flush_offline_buffer())

        return success

    async def _send_http(self, payload: TelemetryPayload) -> bool:
        """Transmit payload via HTTP POST."""
        if not self._session or self._session.closed:
            await self.start()

        try:
            async with self._session.post(self.target_url, json=payload.model_dump()) as resp:
                if resp.status in (200, 201, 202):
                    self.total_sent += 1
                    return True
                else:
                    logger.debug("HTTP server responded with status %s: %s", resp.status, await resp.text())
                    return False
        except Exception as e:
            logger.debug("HTTP transmission failed: %s", e)
            return False

    async def _send_websocket(self, payload: TelemetryPayload) -> bool:
        """Transmit payload via WebSocket stream."""
        try:
            if self._ws_connection is None or self._ws_connection.closed:
                self._ws_connection = await websockets.connect(self.websocket_url, open_timeout=2.0)

            await self._ws_connection.send(payload.model_dump_json())
            self.total_sent += 1
            return True
        except Exception as e:
            logger.debug("WebSocket transmission error: %s", e)
            self._ws_connection = None
            return False

    def _print_console(self, payload: TelemetryPayload):
        """Pretty log output for console-only mode."""
        v = payload.vehicle
        loc = payload.location
        mech = payload.mechanical
        logger.info(
            "[%s | %s] Speed: %5.1f km/h | Alt: %4.0fm | RPM: %4d | Temp: %4.1f°C | Road: %s (%s, %s)",
            v.vehicle_id, v.plate, loc.speed_kmh, loc.altitude_m, mech.rpm, mech.engine_temp_c,
            loc.current_road, loc.current_city, loc.current_state
        )

    async def flush_offline_buffer(self):
        """Transmit stored buffered messages in batches when connection is restored."""
        if not self.offline_buffer:
            return

        while True:
            buffered_records = self.offline_buffer.fetch_batch(settings.BUFFER_FLUSH_BATCH_SIZE)
            if not buffered_records:
                break

            db_ids = [r["db_id"] for r in buffered_records]
            parsed_payloads = [json.loads(r["payload_json"]) for r in buffered_records]

            # Send via batch endpoint
            try:
                if not self._session or self._session.closed:
                    await self.start()

                batch_obj = {
                    "batch_id": str(db_ids[0]),
                    "sent_at": parsed_payloads[0]["timestamp"],
                    "total_records": len(parsed_payloads),
                    "records": parsed_payloads
                }

                async with self._session.post(self.batch_target_url, json=batch_obj) as resp:
                    if resp.status in (200, 201, 202):
                        self.offline_buffer.delete_messages(db_ids)
                        self.total_sent += len(db_ids)
                        logger.info("Flushed %d buffered records to server.", len(db_ids))
                    else:
                        break
            except Exception as e:
                logger.warning("Failed to flush buffer: %s", e)
                break
