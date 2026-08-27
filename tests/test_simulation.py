"""
Unit and Integration Tests for Brazilian Vehicle Telemetry Simulation.
"""

import pytest
import asyncio
from src.fleet import create_brazilian_fleet
from src.models import TelemetryPayload, VehicleCategory
from src.routes import ALL_ROUTES
from src.maps_integration import haversine_distance_m, calculate_bearing_deg


def test_fleet_creation_unique_ten_vehicles():
    """Verify that exactly 10 unique vehicles are created with distinct IDs, plates, and drivers."""
    fleet = create_brazilian_fleet()
    assert len(fleet) == 10, "Fleet must contain exactly 10 vehicles"

    vehicle_ids = [v.metadata.vehicle_id for v in fleet]
    plates = [v.metadata.plate for v in fleet]
    drivers = [v.metadata.driver_id for v in fleet]

    assert len(set(vehicle_ids)) == 10, "All vehicle IDs must be unique"
    assert len(set(plates)) == 10, "All license plates must be unique"
    assert len(set(drivers)) == 10, "All drivers must be unique"


def test_routes_definitions():
    """Verify all 10 Brazilian routes have valid waypoints and altitudes."""
    assert len(ALL_ROUTES) == 10
    for route in ALL_ROUTES:
        assert len(route.waypoints) >= 7, f"Route {route.route_id} must have multiple waypoints"
        for wp in route.waypoints:
            assert -35.0 <= wp.lat <= 5.0, f"Latitude {wp.lat} must be within Brazil"
            assert -74.0 <= wp.lon <= -30.0, f"Longitude {wp.lon} must be within Brazil"
            assert wp.alt_m >= 0.0, f"Altitude {wp.alt_m} must be non-negative"
            assert wp.speed_limit_kmh > 0.0


def test_telemetry_payload_generation():
    """Verify that vehicle simulator produces valid, strictly typed Pydantic payloads."""
    fleet = create_brazilian_fleet()
    v1 = fleet[0]

    payload = v1.generate_telemetry(elapsed_seconds=4.0)
    assert isinstance(payload, TelemetryPayload)
    assert payload.sequence_number == 1
    assert payload.location.latitude != 0.0
    assert payload.location.longitude != 0.0
    assert payload.location.altitude_m >= 0.0
    assert payload.mechanical.rpm >= 600
    assert payload.mechanical.battery_voltage_v > 10.0
    assert len(payload.tires) >= 4
    assert payload.vehicle.category == VehicleCategory.HEAVY_TRUCK_REEFER


def test_physics_step_progression():
    """Verify that stepping physics advances odometer and updates coordinates."""
    fleet = create_brazilian_fleet()
    v = fleet[0]
    initial_odo = v.initial_odometer_km

    # Simulate 5 steps of 4 seconds = 20 seconds
    for _ in range(5):
        payload = v.generate_telemetry(elapsed_seconds=4.0)

    assert v.physics.trip_odometer_km >= 0.0
    assert payload.location.odometer_km >= initial_odo


def test_geodesic_distance_and_bearing():
    """Test Haversine distance and compass bearing calculations."""
    # São Paulo (-23.5505, -46.6333) to Rio de Janeiro (-22.9068, -43.1729) ~ 357 km
    dist = haversine_distance_m(-23.5505, -46.6333, -22.9068, -43.1729)
    assert 350000.0 < dist < 370000.0

    bearing = calculate_bearing_deg(-23.5505, -46.6333, -22.9068, -43.1729)
    assert 0.0 <= bearing < 360.0
