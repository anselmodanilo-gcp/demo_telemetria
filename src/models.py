"""
Pydantic Data Models for Brazilian Commercial Fleet Telemetry.
Comprehensive modeling covering GPS, engine diagnostics, OBD-II, TPMS, specialized cargo, and safety sensors.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class VehicleCategory(str, Enum):
    HEAVY_TRUCK_REEFER = "HEAVY_TRUCK_REEFER"        # Scania R450 - SP -> Curitiba
    BITREM_AGRO = "BITREM_AGRO"                      # Volvo FH 540 - Rondonópolis -> Santos
    VUC_URBAN = "VUC_URBAN"                          # Mercedes Accelo 1016 - Grande SP Entregas
    VAN_CARGO = "VAN_CARGO"                          # MB Sprinter 416 - RJ -> Região dos Lagos
    COACH_BUS = "COACH_BUS"                          # Marcopolo Paradiso G8 - Dutra SP -> RJ
    FUEL_TANKER = "FUEL_TANKER"                      # DAF XF 530 - REPLAN Paulínia -> Bauru
    FLEET_PICKUP = "FLEET_PICKUP"                    # Hilux 4x4 - Estrada Real / Apoio MG
    MINING_TRUCK = "MINING_TRUCK"                    # Mercedes Actros 4844 8x4 - Itabira Mineração
    AMBULANCE_ICU = "AMBULANCE_ICU"                  # Renault Master UTI Móvel - Brasília DF
    CAR_CARRIER = "CAR_CARRIER"                      # Volvo VM 330 Cegonha - Betim MG -> SP


class EngineStatus(str, Enum):
    RUNNING = "RUNNING"
    IDLE = "IDLE"
    STOPPED = "STOPPED"
    STARTING = "STARTING"


class TireStatus(str, Enum):
    NORMAL = "NORMAL"
    LOW_PRESSURE = "LOW_PRESSURE"
    HIGH_TEMPERATURE = "HIGH_TEMPERATURE"
    PUNCTURE_LEAK = "PUNCTURE_LEAK"


class VehicleMetadata(BaseModel):
    vehicle_id: str = Field(..., description="Unique vehicle tracker ID e.g. BR-VH-101")
    plate: str = Field(..., description="Brazilian Mercosul license plate e.g. BRA2E19")
    vin: str = Field(..., description="Vehicle Identification Number (Chassis)")
    fleet_name: str = Field(..., description="Fleet Operator Name")
    category: VehicleCategory = Field(..., description="Vehicle classification type")
    manufacturer: str = Field(..., description="Brand/Manufacturer")
    model: str = Field(..., description="Commercial model description")
    manufacture_year: int = Field(..., description="Year of manufacturing")
    driver_id: str = Field(..., description="ID of the registered driver")
    driver_name: str = Field(..., description="Full name of driver")


class GPSLocation(BaseModel):
    latitude: float = Field(..., description="WGS84 Latitude")
    longitude: float = Field(..., description="WGS84 Longitude")
    altitude_m: float = Field(..., description="Altitude in meters above sea level")
    heading_deg: float = Field(..., ge=0.0, lt=360.0, description="Compass heading 0-359.9 degrees")
    speed_kmh: float = Field(..., ge=0.0, description="Instantaneous ground speed in km/h")
    odometer_km: float = Field(..., ge=0.0, description="Total cumulative odometer distance")
    trip_distance_km: float = Field(..., ge=0.0, description="Distance traveled in current route")
    satellite_count: int = Field(default=16, description="Visible GPS satellites")
    hdop: float = Field(default=0.9, description="Horizontal Dilution of Precision")
    current_road: str = Field(default="", description="Highway or street name")
    current_city: str = Field(default="", description="Current city municipality")
    current_state: str = Field(default="", description="State code (e.g. SP, RJ, MT, MG, DF)")


class MechanicalStatus(BaseModel):
    ignition: bool = Field(..., description="Ignition switch status")
    engine_status: EngineStatus = Field(..., description="Engine operating state")
    rpm: int = Field(..., ge=0, description="Engine Revolutions Per Minute")
    gear: int = Field(..., description="Transmission gear (-1: Reverse, 0: Neutral, 1-14: Forward)")
    throttle_pedal_pct: float = Field(..., ge=0.0, le=100.0, description="Accelerator pedal depression %")
    brake_pedal_pct: float = Field(..., ge=0.0, le=100.0, description="Brake pedal depression %")
    engine_load_pct: float = Field(..., ge=0.0, le=100.0, description="Calculated engine load %")
    engine_temp_c: float = Field(..., description="Engine block temperature in °C")
    coolant_temp_c: float = Field(..., description="Coolant temperature in °C")
    oil_temp_c: float = Field(..., description="Engine oil temperature in °C")
    oil_pressure_bar: float = Field(..., ge=0.0, description="Engine oil pressure in Bar")
    battery_voltage_v: float = Field(..., ge=0.0, description="Electrical system voltage (12V/24V)")
    alternator_current_a: float = Field(..., description="Alternator output current in Amperes")
    fuel_level_pct: float = Field(..., ge=0.0, le=100.0, description="Fuel level percentage")
    fuel_volume_liters: float = Field(..., ge=0.0, description="Remaining fuel in liters")
    fuel_rate_l_per_h: float = Field(..., ge=0.0, description="Instantaneous fuel consumption rate (L/h)")
    instantaneous_economy_km_l: float = Field(..., ge=0.0, description="Instantaneous fuel economy (km/L)")
    adblue_level_pct: Optional[float] = Field(default=None, description="ARLA 32 / AdBlue level for diesel")
    total_engine_hours: float = Field(..., ge=0.0, description="Total running hours of the engine")


class TireSensor(BaseModel):
    position: str = Field(..., description="Tire identifier e.g. 'Eixo1_Esq', 'Eixo1_Dir', 'Carreta1_Esq'")
    pressure_psi: float = Field(..., description="Tire pressure in PSI")
    temperature_c: float = Field(..., description="Tire internal temperature in °C")
    status: TireStatus = Field(default=TireStatus.NORMAL, description="TPMS alert state")


class SafetyAndDynamics(BaseModel):
    seatbelt_fastened: bool = Field(..., description="Driver seatbelt sensor")
    parking_brake_engaged: bool = Field(..., description="Handbrake/Air parking brake state")
    cruise_control_active: bool = Field(default=False, description="Cruise control engaged")
    abs_active: bool = Field(default=False, description="Anti-lock braking system firing")
    esp_active: bool = Field(default=False, description="Electronic stability program firing")
    steering_angle_deg: float = Field(default=0.0, description="Steering wheel angle in degrees")
    accel_longitudinal_g: float = Field(default=0.0, description="Longitudinal acceleration in G-force")
    accel_lateral_g: float = Field(default=0.0, description="Lateral cornering acceleration in G-force")
    hazard_lights: bool = Field(default=False, description="Hazard warning flashers")
    panic_button_pressed: bool = Field(default=False, description="Driver silent panic/emergency trigger")
    doors_locked: bool = Field(default=True, description="Cab/cargo door locking status")


class SpecializedCargo(BaseModel):
    cargo_type: str = Field(..., description="Description of freight or passenger payload")
    cargo_weight_kg: float = Field(..., ge=0.0, description="Current weight of cargo in kg")
    max_payload_kg: float = Field(..., ge=0.0, description="Vehicle maximum legal payload capacity in kg")
    
    # Reefer specific
    reefer_temperature_c: Optional[float] = Field(default=None, description="Cargo hold thermometer (°C)")
    reefer_setpoint_c: Optional[float] = Field(default=None, description="Target cooling temperature (°C)")
    reefer_unit_running: Optional[bool] = Field(default=None, description="Reefer diesel/electric motor state")
    reefer_door_open: Optional[bool] = Field(default=None, description="Cold chamber door sensor")

    # Hazmat / Tanker specific
    tank_ullage_pct: Optional[float] = Field(default=None, description="Tank vapor headroom %")
    tank_vapor_pressure_kpa: Optional[float] = Field(default=None, description="Tank internal pressure (kPa)")
    bottom_loading_valve_sealed: Optional[bool] = Field(default=None, description="Hazardous cargo valve seal")

    # Emergency Ambulance specific
    siren_active: Optional[bool] = Field(default=None, description="Emergency audio siren active")
    beacon_lights_active: Optional[bool] = Field(default=None, description="Emergency strobe light bar active")
    patient_cabin_temp_c: Optional[float] = Field(default=None, description="Ambulance ICU cabin temp")

    # Mining Tipper specific
    tipper_bed_angle_deg: Optional[float] = Field(default=None, description="Dump bed hydraulic tilt angle")


class DiagnosticsOBD(BaseModel):
    mil_indicator_light: bool = Field(default=False, description="Check Engine / MIL warning light")
    active_dtcs: List[str] = Field(default_factory=list, description="Active OBD-II fault codes e.g. ['P0128']")
    service_distance_remaining_km: float = Field(default=15000.0, description="Distance until scheduled maintenance")
    brake_pad_wear_pct: float = Field(default=22.0, ge=0.0, le=100.0, description="Brake pad friction wear %")
    air_filter_restriction_kpa: float = Field(default=1.2, description="Air intake filter restriction")


class DeviceTelemetry(BaseModel):
    tracker_serial: str = Field(..., description="On-board Telematics unit serial number")
    firmware_version: str = Field(default="v3.4.12-GCP", description="Device firmware version")
    gsm_signal_csq: int = Field(default=28, ge=0, le=31, description="Cellular signal strength (0-31)")
    network_carrier: str = Field(default="Vivo Empresas 5G / LTE", description="Cellular operator")
    internal_battery_pct: float = Field(default=98.5, description="Tracker backup battery %")
    buffer_queue_count: int = Field(default=0, description="Unsent buffered message count")


class TelemetryPayload(BaseModel):
    """
    Standard Real-Time Telemetry Frame emitted every 4 seconds.
    """
    message_id: str = Field(..., description="UUIDv4 identifier for telemetry frame deduplication")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp of sensor acquisition")
    sequence_number: int = Field(..., ge=1, description="Monotonically increasing counter per vehicle")
    vehicle: VehicleMetadata
    location: GPSLocation
    mechanical: MechanicalStatus
    tires: List[TireSensor]
    safety: SafetyAndDynamics
    cargo: SpecializedCargo
    diagnostics: DiagnosticsOBD
    device: DeviceTelemetry


class TelemetryBatchPayload(BaseModel):
    """
    Batch telemetry wrapper for bulk ingestion.
    """
    batch_id: str = Field(..., description="UUID for batch transmission")
    sent_at: str = Field(..., description="ISO 8601 UTC timestamp of dispatch")
    total_records: int = Field(..., description="Number of telemetry frames in payload")
    records: List[TelemetryPayload]
