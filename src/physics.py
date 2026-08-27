"""
Physics and Mechanical Sensor Simulation Engine.
Computes realistic vehicle dynamics, incline/slope effects on heavy vehicles,
engine thermodynamic models, fuel consumption, and TPMS sensor feedback.
"""

import math
import random
from typing import Tuple, List
from src.models import (
    VehicleCategory, EngineStatus, TireStatus, TireSensor,
    MechanicalStatus, SafetyAndDynamics, SpecializedCargo, DiagnosticsOBD
)
from src.routes import Waypoint, RouteProfile
from src.maps_integration import haversine_distance_m, calculate_bearing_deg, interpolate_coordinate


class VehiclePhysicsEngine:
    """
    Simulates real-world physical and mechanical behavior of a commercial vehicle.
    """
    def __init__(self, vehicle_category: VehicleCategory, route: RouteProfile):
        self.category = vehicle_category
        self.route = route
        self.current_waypoint_idx = 0
        self.segment_progress_fraction = 0.0
        self.total_distance_traveled_m = 0.0

        # Dynamics state
        self.current_speed_kmh = 0.0
        self.target_speed_kmh = 0.0
        self.is_stopped = False
        self.stop_time_remaining_s = 0.0
        self.trip_odometer_km = 0.0

        # Mechanical state initialized per category
        self._init_category_specs()

    def _init_category_specs(self):
        """Configure physical traits according to vehicle class."""
        if self.category in (VehicleCategory.HEAVY_TRUCK_REEFER, VehicleCategory.BITREM_AGRO, VehicleCategory.FUEL_TANKER, VehicleCategory.CAR_CARRIER):
            self.max_speed = 90.0
            self.accel_rate_mps2 = 0.5   # Heavy diesel slow acceleration
            self.decel_rate_mps2 = 1.2
            self.base_rpm_idle = 650
            self.base_rpm_cruise = 1350
            self.max_rpm = 2300
            self.gears_count = 12
            self.fuel_tank_capacity_l = 600.0
            self.fuel_level_l = random.uniform(380.0, 560.0)
            self.base_consumption_l_per_100km = 36.0
            self.electrical_system_v = 24.0
            self.axles = 4 if self.category != VehicleCategory.BITREM_AGRO else 9
            self.adblue_level_pct = random.uniform(70.0, 95.0)
        elif self.category == VehicleCategory.MINING_TRUCK:
            self.max_speed = 45.0
            self.accel_rate_mps2 = 0.35
            self.decel_rate_mps2 = 1.5
            self.base_rpm_idle = 700
            self.base_rpm_cruise = 1600
            self.max_rpm = 2400
            self.gears_count = 8
            self.fuel_tank_capacity_l = 900.0
            self.fuel_level_l = random.uniform(600.0, 850.0)
            self.base_consumption_l_per_100km = 65.0
            self.electrical_system_v = 24.0
            self.axles = 4
            self.adblue_level_pct = random.uniform(60.0, 90.0)
        elif self.category == VehicleCategory.COACH_BUS:
            self.max_speed = 100.0
            self.accel_rate_mps2 = 0.8
            self.decel_rate_mps2 = 1.6
            self.base_rpm_idle = 650
            self.base_rpm_cruise = 1400
            self.max_rpm = 2200
            self.gears_count = 8
            self.fuel_tank_capacity_l = 450.0
            self.fuel_level_l = random.uniform(300.0, 420.0)
            self.base_consumption_l_per_100km = 28.0
            self.electrical_system_v = 24.0
            self.axles = 3
            self.adblue_level_pct = random.uniform(75.0, 95.0)
        elif self.category == VehicleCategory.AMBULANCE_ICU:
            self.max_speed = 120.0
            self.accel_rate_mps2 = 2.2
            self.decel_rate_mps2 = 3.5
            self.base_rpm_idle = 800
            self.base_rpm_cruise = 2200
            self.max_rpm = 4000
            self.gears_count = 6
            self.fuel_tank_capacity_l = 80.0
            self.fuel_level_l = random.uniform(50.0, 75.0)
            self.base_consumption_l_per_100km = 11.5
            self.electrical_system_v = 12.0
            self.axles = 2
            self.adblue_level_pct = random.uniform(80.0, 100.0)
        elif self.category == VehicleCategory.FLEET_PICKUP:
            self.max_speed = 120.0
            self.accel_rate_mps2 = 1.8
            self.decel_rate_mps2 = 2.8
            self.base_rpm_idle = 750
            self.base_rpm_cruise = 1900
            self.max_rpm = 3800
            self.gears_count = 6
            self.fuel_tank_capacity_l = 80.0
            self.fuel_level_l = random.uniform(45.0, 70.0)
            self.base_consumption_l_per_100km = 10.5
            self.electrical_system_v = 12.0
            self.axles = 2
            self.adblue_level_pct = random.uniform(80.0, 100.0)
        else:  # VUC_URBAN & VAN_CARGO
            self.max_speed = 90.0
            self.accel_rate_mps2 = 1.2
            self.decel_rate_mps2 = 2.0
            self.base_rpm_idle = 700
            self.base_rpm_cruise = 1800
            self.max_rpm = 3200
            self.gears_count = 6
            self.fuel_tank_capacity_l = 150.0
            self.fuel_level_l = random.uniform(80.0, 140.0)
            self.base_consumption_l_per_100km = 16.0
            self.electrical_system_v = 12.0 if self.category == VehicleCategory.VAN_CARGO else 24.0
            self.axles = 2
            self.adblue_level_pct = random.uniform(70.0, 95.0)

        # Baseline temperatures
        self.engine_temp_c = 88.0 + random.uniform(-2.0, 2.0)
        self.coolant_temp_c = 86.0 + random.uniform(-2.0, 2.0)
        self.oil_temp_c = 92.0 + random.uniform(-2.0, 2.0)
        self.reefer_temp_c = -18.2 if self.category == VehicleCategory.HEAVY_TRUCK_REEFER else 4.0

    def step(self, elapsed_seconds: float) -> Tuple[float, float, float, float, str, str, str]:
        """
        Advance vehicle along its route by elapsed_seconds.
        Returns: (latitude, longitude, altitude_m, heading_deg, road_name, city, state)
        """
        waypoints = self.route.waypoints
        num_wp = len(waypoints)

        if self.current_waypoint_idx >= num_wp - 1:
            # Reached end of route - loop back smoothly to start (continuous fleet run)
            self.current_waypoint_idx = 0
            self.segment_progress_fraction = 0.0

        curr_wp = waypoints[self.current_waypoint_idx]
        next_wp = waypoints[self.current_waypoint_idx + 1]

        # Handle scheduled stops (e.g. tolls, logistics depots, delivery spots)
        if self.stop_time_remaining_s > 0:
            self.stop_time_remaining_s -= elapsed_seconds
            self.current_speed_kmh = max(0.0, self.current_speed_kmh - (self.decel_rate_mps2 * 3.6 * elapsed_seconds))
            self.is_stopped = True
            heading = calculate_bearing_deg(curr_wp.lat, curr_wp.lon, next_wp.lat, next_wp.lon)
            lat, lon, alt = interpolate_coordinate(
                curr_wp.lat, curr_wp.lon, curr_wp.alt_m,
                next_wp.lat, next_wp.lon, next_wp.alt_m,
                self.segment_progress_fraction
            )
            return lat, lon, alt, heading, curr_wp.road_name, curr_wp.city, curr_wp.state

        self.is_stopped = False

        # Target speed calculation (based on speed limit, curve slowing, and gradient)
        seg_distance_m = haversine_distance_m(curr_wp.lat, curr_wp.lon, next_wp.lat, next_wp.lon)
        if seg_distance_m < 1.0:
            seg_distance_m = 1.0

        alt_diff_m = next_wp.alt_m - curr_wp.alt_m
        gradient_pct = (alt_diff_m / seg_distance_m) * 100.0  # Slope %

        # Slope effect on target speed
        speed_limit = min(self.max_speed, curr_wp.speed_limit_kmh)
        if gradient_pct > 3.0 and self.category in (VehicleCategory.HEAVY_TRUCK_REEFER, VehicleCategory.BITREM_AGRO, VehicleCategory.MINING_TRUCK):
            # Heavy truck climbs steep hill -> lower speed
            climb_penalty = min(35.0, gradient_pct * 4.5)
            self.target_speed_kmh = max(25.0, speed_limit - climb_penalty)
        elif gradient_pct < -3.0:
            # Descending hill
            self.target_speed_kmh = speed_limit
        else:
            # Flat highway / standard road
            self.target_speed_kmh = speed_limit + random.uniform(-2.0, 2.0)

        # Smooth acceleration / deceleration towards target speed
        speed_diff = self.target_speed_kmh - self.current_speed_kmh
        if speed_diff > 0:
            accel_kmh = (self.accel_rate_mps2 * 3.6) * elapsed_seconds
            self.current_speed_kmh = min(self.target_speed_kmh, self.current_speed_kmh + accel_kmh)
        else:
            decel_kmh = (self.decel_rate_mps2 * 3.6) * elapsed_seconds
            self.current_speed_kmh = max(self.target_speed_kmh, self.current_speed_kmh - decel_kmh)

        # Calculate distance traveled during this time slice
        speed_mps = (self.current_speed_kmh / 3.6)
        distance_step_m = speed_mps * elapsed_seconds
        self.total_distance_traveled_m += distance_step_m
        self.trip_odometer_km += distance_step_m / 1000.0

        # Advance along segment
        fraction_step = distance_step_m / seg_distance_m
        self.segment_progress_fraction += fraction_step

        if self.segment_progress_fraction >= 1.0:
            # Transitioned to next waypoint
            self.segment_progress_fraction = 0.0
            self.current_waypoint_idx += 1
            if self.current_waypoint_idx >= num_wp - 1:
                self.current_waypoint_idx = 0

            # Trigger stop if the reached waypoint defines a stop duration
            new_curr_wp = waypoints[self.current_waypoint_idx]
            if new_curr_wp.stop_duration_s > 0:
                self.stop_time_remaining_s = new_curr_wp.stop_duration_s

        # Interpolate coordinates
        active_curr = waypoints[self.current_waypoint_idx]
        active_next = waypoints[(self.current_waypoint_idx + 1) % num_wp]

        lat, lon, alt = interpolate_coordinate(
            active_curr.lat, active_curr.lon, active_curr.alt_m,
            active_next.lat, active_next.lon, active_next.alt_m,
            self.segment_progress_fraction
        )
        heading = calculate_bearing_deg(active_curr.lat, active_curr.lon, active_next.lat, active_next.lon)

        return lat, lon, alt, heading, active_curr.road_name, active_curr.city, active_curr.state

    def compute_mechanical_state(
        self,
        speed_kmh: float,
        altitude_m: float,
        prev_alt_m: float,
        elapsed_s: float,
        base_odometer_km: float
    ) -> MechanicalStatus:
        """Calculate engine telemetry, fuel consumption, oil pressure, and electrical metrics."""
        incline = altitude_m - prev_alt_m

        if speed_kmh < 1.0:
            engine_status = EngineStatus.IDLE
            rpm = int(self.base_rpm_idle + random.uniform(-15, 15))
            gear = 0
            throttle_pct = 0.0
            brake_pct = 15.0 if self.is_stopped else 0.0
            engine_load_pct = 12.0 + random.uniform(-2, 2)
            fuel_rate_l_h = 1.8 if self.electrical_system_v == 24.0 else 0.9
            instant_km_l = 0.0
        else:
            engine_status = EngineStatus.RUNNING
            # Calculate appropriate gear and RPM for current speed
            speed_ratio = speed_kmh / max(1.0, self.max_speed)
            gear = max(1, min(self.gears_count, int(speed_ratio * self.gears_count) + 1))
            
            rpm_variation = (speed_kmh % 15.0) / 15.0
            rpm = int(self.base_rpm_cruise + (rpm_variation * 400.0) + (incline * 8.0))
            rpm = max(self.base_rpm_idle, min(self.max_rpm, rpm))

            # Incline effect on throttle and load
            if incline > 0.5:
                # Climbing hill
                throttle_pct = min(100.0, 65.0 + (incline * 6.0) + random.uniform(-3, 5))
                brake_pct = 0.0
                engine_load_pct = min(98.0, 70.0 + (incline * 5.0))
                fuel_multiplier = 2.2
            elif incline < -0.5:
                # Descending hill
                throttle_pct = 5.0
                brake_pct = min(60.0, abs(incline) * 5.0)
                engine_load_pct = 20.0
                fuel_multiplier = 0.4
            else:
                # Flat cruise
                throttle_pct = 35.0 + random.uniform(-4, 4)
                brake_pct = 0.0
                engine_load_pct = 45.0 + random.uniform(-5, 5)
                fuel_multiplier = 1.0

            # Instantaneous fuel consumption calculation
            fuel_rate_l_h = (self.base_consumption_l_per_100km * (speed_kmh / 100.0) * fuel_multiplier) + random.uniform(-0.3, 0.3)
            fuel_rate_l_h = max(1.2, fuel_rate_l_h)
            instant_km_l = speed_kmh / fuel_rate_l_h if fuel_rate_l_h > 0 else 0.0

        # Deplete fuel tank
        liters_used = (fuel_rate_l_h / 3600.0) * elapsed_s
        self.fuel_level_l = max(5.0, self.fuel_level_l - liters_used)
        fuel_level_pct = (self.fuel_level_l / self.fuel_tank_capacity_l) * 100.0

        # Engine thermodynamics
        if engine_load_pct > 70.0:
            self.engine_temp_c = min(102.0, self.engine_temp_c + 0.15 * elapsed_s)
            self.coolant_temp_c = min(98.0, self.coolant_temp_c + 0.12 * elapsed_s)
            self.oil_temp_c = min(108.0, self.oil_temp_c + 0.18 * elapsed_s)
        else:
            self.engine_temp_c = max(86.0, self.engine_temp_c - 0.08 * elapsed_s)
            self.coolant_temp_c = max(84.0, self.coolant_temp_c - 0.08 * elapsed_s)
            self.oil_temp_c = max(89.0, self.oil_temp_c - 0.08 * elapsed_s)

        # Oil pressure directly correlated to engine RPM
        oil_pressure_bar = 1.5 + ((rpm / self.max_rpm) * 3.5) + random.uniform(-0.1, 0.1)

        # Electrical voltage with alternator charging
        if self.electrical_system_v == 24.0:
            battery_v = 28.2 + random.uniform(-0.2, 0.2)
            alt_amps = 45.0 + (throttle_pct * 0.4)
        else:
            battery_v = 14.1 + random.uniform(-0.1, 0.1)
            alt_amps = 28.0 + (throttle_pct * 0.2)

        total_hours = (base_odometer_km / 55.0) + (self.trip_odometer_km / 55.0)

        return MechanicalStatus(
            ignition=True,
            engine_status=engine_status,
            rpm=rpm,
            gear=gear,
            throttle_pedal_pct=round(throttle_pct, 1),
            brake_pedal_pct=round(brake_pct, 1),
            engine_load_pct=round(engine_load_pct, 1),
            engine_temp_c=round(self.engine_temp_c, 1),
            coolant_temp_c=round(self.coolant_temp_c, 1),
            oil_temp_c=round(self.oil_temp_c, 1),
            oil_pressure_bar=round(oil_pressure_bar, 2),
            battery_voltage_v=round(battery_v, 2),
            alternator_current_a=round(alt_amps, 1),
            fuel_level_pct=round(fuel_level_pct, 1),
            fuel_volume_liters=round(self.fuel_level_l, 1),
            fuel_rate_l_per_h=round(fuel_rate_l_h, 2),
            instantaneous_economy_km_l=round(instant_km_l, 2),
            adblue_level_pct=round(self.adblue_level_pct, 1) if self.adblue_level_pct is not None else None,
            total_engine_hours=round(total_hours, 2),
        )

    def generate_tire_sensors(self, speed_kmh: float) -> List[TireSensor]:
        """Generate TPMS sensor array based on axle configuration and running heat."""
        sensors = []
        base_psi = 110.0 if self.electrical_system_v == 24.0 else 36.0
        # Driving warms tires up by 3-6 PSI and +10-20°C
        heat_psi_offset = (speed_kmh / 100.0) * 4.0
        tire_temp = 32.0 + (speed_kmh / 100.0) * 18.0 + random.uniform(-1.5, 1.5)

        for axle in range(1, self.axles + 1):
            if axle == 1:
                # Steer axle (single wheels)
                sensors.append(TireSensor(
                    position=f"Eixo{axle}_Esq",
                    pressure_psi=round(base_psi + heat_psi_offset + random.uniform(-0.5, 0.5), 1),
                    temperature_c=round(tire_temp, 1),
                    status=TireStatus.NORMAL
                ))
                sensors.append(TireSensor(
                    position=f"Eixo{axle}_Dir",
                    pressure_psi=round(base_psi + heat_psi_offset + random.uniform(-0.5, 0.5), 1),
                    temperature_c=round(tire_temp, 1),
                    status=TireStatus.NORMAL
                ))
            else:
                # Dual / trailer wheels
                sensors.append(TireSensor(
                    position=f"Eixo{axle}_Esq_Ext",
                    pressure_psi=round(base_psi + heat_psi_offset + random.uniform(-0.8, 0.8), 1),
                    temperature_c=round(tire_temp + 2.0, 1),
                    status=TireStatus.NORMAL
                ))
                sensors.append(TireSensor(
                    position=f"Eixo{axle}_Dir_Ext",
                    pressure_psi=round(base_psi + heat_psi_offset + random.uniform(-0.8, 0.8), 1),
                    temperature_c=round(tire_temp + 2.0, 1),
                    status=TireStatus.NORMAL
                ))

        return sensors

    def generate_safety_and_dynamics(self, speed_kmh: float) -> SafetyAndDynamics:
        """Calculate safety sensors, accelerations, and dynamic indicators."""
        longitudinal_g = 0.0
        lateral_g = 0.0
        steering_deg = 0.0

        if speed_kmh > 5.0:
            steering_deg = random.uniform(-4.5, 4.5)
            lateral_g = (steering_deg / 45.0) * 0.15
            longitudinal_g = random.uniform(-0.04, 0.06)

        return SafetyAndDynamics(
            seatbelt_fastened=True,
            parking_brake_engaged=self.is_stopped,
            cruise_control_active=(speed_kmh > 60.0 and not self.is_stopped),
            abs_active=False,
            esp_active=False,
            steering_angle_deg=round(steering_deg, 1),
            accel_longitudinal_g=round(longitudinal_g, 3),
            accel_lateral_g=round(lateral_g, 3),
            hazard_lights=self.is_stopped,
            panic_button_pressed=False,
            doors_locked=True
        )

    def generate_specialized_cargo(self, speed_kmh: float) -> SpecializedCargo:
        """Generate cargo-specific sensor attributes."""
        if self.category == VehicleCategory.HEAVY_TRUCK_REEFER:
            self.reefer_temp_c += random.uniform(-0.05, 0.05)
            return SpecializedCargo(
                cargo_type="CARGA_FRIGORIFICADA_ALIMENTOS",
                cargo_weight_kg=24500.0,
                max_payload_kg=28000.0,
                reefer_temperature_c=round(self.reefer_temp_c, 1),
                reefer_setpoint_c=-18.0,
                reefer_unit_running=True,
                reefer_door_open=False,
            )
        elif self.category == VehicleCategory.BITREM_AGRO:
            return SpecializedCargo(
                cargo_type="GRAOS_SOJA_A_GRANEL",
                cargo_weight_kg=48500.0,
                max_payload_kg=54000.0,
            )
        elif self.category == VehicleCategory.FUEL_TANKER:
            return SpecializedCargo(
                cargo_type="COMBUSTIVEL_DIESEL_S10_GRANEL_LIQUIDO",
                cargo_weight_kg=32000.0,
                max_payload_kg=35000.0,
                tank_ullage_pct=5.5,
                tank_vapor_pressure_kpa=102.4 + random.uniform(-0.5, 0.5),
                bottom_loading_valve_sealed=True
            )
        elif self.category == VehicleCategory.AMBULANCE_ICU:
            return SpecializedCargo(
                cargo_type="TRANSPORTE_PACIENTE_UTI_MOVEL",
                cargo_weight_kg=650.0,
                max_payload_kg=1200.0,
                siren_active=(speed_kmh > 30.0),
                beacon_lights_active=True,
                patient_cabin_temp_c=22.5
            )
        elif self.category == VehicleCategory.MINING_TRUCK:
            return SpecializedCargo(
                cargo_type="MINERIO_DE_FERRO_BRUTO",
                cargo_weight_kg=78000.0,
                max_payload_kg=85000.0,
                tipper_bed_angle_deg=0.0
            )
        elif self.category == VehicleCategory.COACH_BUS:
            return SpecializedCargo(
                cargo_type="PASSAGEIROS_CLASSE_LEITO_TURISMO",
                cargo_weight_kg=3400.0,
                max_payload_kg=6000.0,
            )
        elif self.category == VehicleCategory.CAR_CARRIER:
            return SpecializedCargo(
                cargo_type="TRANSPORTE_VEICULOS_NOVOS_11_UNIDADES",
                cargo_weight_kg=14500.0,
                max_payload_kg=18000.0,
            )
        elif self.category == VehicleCategory.FLEET_PICKUP:
            return SpecializedCargo(
                cargo_type="PECAS_E_EQUIPAMENTOS_DE_MANUTENCAO",
                cargo_weight_kg=450.0,
                max_payload_kg=1000.0,
            )
        else:  # Urban VUC & Van
            return SpecializedCargo(
                cargo_type="ENCOMENDAS_E_MERCADORIAS_DIVERSAS",
                cargo_weight_kg=1850.0,
                max_payload_kg=3500.0,
            )
