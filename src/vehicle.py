"""
Vehicle Simulation Actor.
Maintains state, odometer, trajectory advancement, and compiles full TelemetryPayload instances.
"""

import uuid
import datetime
from typing import Dict, Any, Optional
from src.models import (
    VehicleMetadata, GPSLocation, DeviceTelemetry,
    DiagnosticsOBD, TelemetryPayload
)
from src.routes import RouteProfile
from src.physics import VehiclePhysicsEngine


class VehicleSimulator:
    """
    Stateful simulator for a single commercial vehicle in Brazil.
    """
    def __init__(
        self,
        metadata: VehicleMetadata,
        route: RouteProfile,
        initial_odometer_km: float = 120500.0,
        tracker_serial: Optional[str] = None
    ):
        self.metadata = metadata
        self.route = route
        self.initial_odometer_km = initial_odometer_km
        self.tracker_serial = tracker_serial or f"TK-{self.metadata.vehicle_id.replace('-', '')}"
        self.physics = VehiclePhysicsEngine(self.metadata.category, self.route)
        
        self.sequence_number = 0
        self.prev_altitude_m = self.route.waypoints[0].alt_m
        self.active_dtcs = []
        self.mil_light = False

    def trigger_anomaly(self, anomaly_type: str):
        """Simulate a telemetry alert or mechanical anomaly for testing."""
        if anomaly_type == "CHECK_ENGINE":
            self.mil_light = True
            self.active_dtcs = ["P0128 - Coolant Thermostat Error"]
        elif anomaly_type == "CLEAR_FAULTS":
            self.mil_light = False
            self.active_dtcs = []

    def generate_telemetry(self, elapsed_seconds: float = 4.0) -> TelemetryPayload:
        """
        Execute physics step and return an updated TelemetryPayload frame.
        """
        self.sequence_number += 1
        now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Advance physics along route
        lat, lon, alt, heading, road, city, state = self.physics.step(elapsed_seconds)
        speed = self.physics.current_speed_kmh
        total_odometer = self.initial_odometer_km + self.physics.trip_odometer_km

        # Compute mechanical sub-systems
        mechanical = self.physics.compute_mechanical_state(
            speed_kmh=speed,
            altitude_m=alt,
            prev_alt_m=self.prev_altitude_m,
            elapsed_s=elapsed_seconds,
            base_odometer_km=self.initial_odometer_km
        )
        self.prev_altitude_m = alt

        # Compute TPMS, Safety, Cargo, and Diagnostics
        tires = self.physics.generate_tire_sensors(speed)
        safety = self.physics.generate_safety_and_dynamics(speed)
        cargo = self.physics.generate_specialized_cargo(speed)

        diagnostics = DiagnosticsOBD(
            mil_indicator_light=self.mil_light,
            active_dtcs=self.active_dtcs,
            service_distance_remaining_km=max(0.0, 15000.0 - (self.physics.trip_odometer_km % 15000.0)),
            brake_pad_wear_pct=round(min(95.0, 25.0 + (total_odometer / 5000.0) % 50.0), 1),
            air_filter_restriction_kpa=1.3 if speed > 40.0 else 0.8
        )

        location = GPSLocation(
            latitude=round(lat, 6),
            longitude=round(lon, 6),
            altitude_m=round(alt, 1),
            heading_deg=round(heading, 1),
            speed_kmh=round(speed, 1),
            odometer_km=round(total_odometer, 2),
            trip_distance_km=round(self.physics.trip_odometer_km, 2),
            satellite_count=18,
            hdop=0.85,
            current_road=road,
            current_city=city,
            current_state=state
        )

        device = DeviceTelemetry(
            tracker_serial=self.tracker_serial,
            firmware_version="v3.4.12-GCP",
            gsm_signal_csq=29,
            network_carrier="Vivo Empresas 5G / IoT",
            internal_battery_pct=99.2,
            buffer_queue_count=0
        )

        return TelemetryPayload(
            message_id=str(uuid.uuid4()),
            timestamp=now_utc,
            sequence_number=self.sequence_number,
            vehicle=self.metadata,
            location=location,
            mechanical=mechanical,
            tires=tires,
            safety=safety,
            cargo=cargo,
            diagnostics=diagnostics,
            device=device
        )
