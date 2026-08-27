"""
Fleet Manager.
Instantiates and orchestrates 10 unique commercial vehicles across Brazil.
"""

from typing import List, Dict
from src.models import VehicleMetadata, VehicleCategory
from src.routes import (
    ROUTE_BR116_SP_PR,
    ROUTE_BR163_MT_MS,
    ROUTE_SP_URBAN_DELIVERY,
    ROUTE_RJ_COASTAL_LOGISTICS,
    ROUTE_BR116_DUTRA_PASSENGER,
    ROUTE_SP300_HAZMAT_FUEL,
    ROUTE_MG_ESTRADA_REAL,
    ROUTE_CARAJAS_MINING_HEAVY,
    ROUTE_DF_EMERGENCY_MOBILE,
    ROUTE_BR381_FERNAO_DIAS,
)
from src.vehicle import VehicleSimulator


def create_brazilian_fleet() -> List[VehicleSimulator]:
    """
    Build 10 completely unique commercial fleet vehicles with realistic routes and metadata.
    """
    fleet_configs = [
        # 1. Heavy Reefer Truck - SP to Curitiba
        {
            "meta": VehicleMetadata(
                vehicle_id="BR-VH-101",
                plate="BRA2E19",
                vin="9BWZZZ377VT001011",
                fleet_name="TransLog Brasil Frio",
                category=VehicleCategory.HEAVY_TRUCK_REEFER,
                manufacturer="Scania",
                model="R450 6x2 Highline",
                manufacture_year=2024,
                driver_id="DRV-0019",
                driver_name="Carlos Eduardo Silveira"
            ),
            "route": ROUTE_BR116_SP_PR,
            "odometer": 184520.0
        },
        # 2. Agro Bitrem 9 Eixos - MT to MS
        {
            "meta": VehicleMetadata(
                vehicle_id="BR-VH-102",
                plate="RND8F32",
                vin="9BWZZZ377VT001022",
                fleet_name="AgroTrans Brasil Grãos",
                category=VehicleCategory.BITREM_AGRO,
                manufacturer="Volvo",
                model="FH 540 8x4 Bitrem",
                manufacture_year=2023,
                driver_id="DRV-0044",
                driver_name="Marcos Antonio Rezende"
            ),
            "route": ROUTE_BR163_MT_MS,
            "odometer": 298400.0
        },
        # 3. Urban Delivery VUC - São Paulo Capital
        {
            "meta": VehicleMetadata(
                vehicle_id="BR-VH-103",
                plate="SPK4A77",
                vin="9BWZZZ377VT001033",
                fleet_name="Paulistana Express VUC",
                category=VehicleCategory.VUC_URBAN,
                manufacturer="Mercedes-Benz",
                model="Accelo 1016 Urbano",
                manufacture_year=2022,
                driver_id="DRV-0082",
                driver_name="Rodrigo de Oliveira"
            ),
            "route": ROUTE_SP_URBAN_DELIVERY,
            "odometer": 76300.0
        },
        # 4. Cargo Delivery Van - Rio de Janeiro to Cabo Frio
        {
            "meta": VehicleMetadata(
                vehicle_id="BR-VH-104",
                plate="RJL9D45",
                vin="9BWZZZ377VT001044",
                fleet_name="Rio Express Encomendas",
                category=VehicleCategory.VAN_CARGO,
                manufacturer="Mercedes-Benz",
                model="Sprinter 416 Furgão",
                manufacture_year=2024,
                driver_id="DRV-0112",
                driver_name="Felipe Nascimento Costa"
            ),
            "route": ROUTE_RJ_COASTAL_LOGISTICS,
            "odometer": 54200.0
        },
        # 5. Executive Coach Bus - São Paulo to Rio (Dutra)
        {
            "meta": VehicleMetadata(
                vehicle_id="BR-VH-105",
                plate="EXP1H90",
                vin="9BWZZZ377VT001055",
                fleet_name="Viação Dutra Premium",
                category=VehicleCategory.COACH_BUS,
                manufacturer="Scania / Marcopolo",
                model="Paradiso G8 1800 DD / K410",
                manufacture_year=2024,
                driver_id="DRV-0230",
                driver_name="Valdir Santos Moreira"
            ),
            "route": ROUTE_BR116_DUTRA_PASSENGER,
            "odometer": 215600.0
        },
        # 6. Fuel Tanker Hazmat - Paulínia to Bauru
        {
            "meta": VehicleMetadata(
                vehicle_id="BR-VH-106",
                plate="PLN3C61",
                vin="9BWZZZ377VT001066",
                fleet_name="PetroTrans Distribuição",
                category=VehicleCategory.FUEL_TANKER,
                manufacturer="DAF",
                model="XF 530 Super Space 6x4",
                manufacture_year=2023,
                driver_id="DRV-0155",
                driver_name="Gilberto Mendes Prado"
            ),
            "route": ROUTE_SP300_HAZMAT_FUEL,
            "odometer": 167800.0
        },
        # 7. Field Service Support 4x4 - Minas Gerais Estrada Real
        {
            "meta": VehicleMetadata(
                vehicle_id="BR-VH-107",
                plate="MGH7B14",
                vin="9BWZZZ377VT001077",
                fleet_name="Minas Apoio & Engenharia",
                category=VehicleCategory.FLEET_PICKUP,
                manufacturer="Toyota",
                model="Hilux D-4D 2.8 4x4",
                manufacture_year=2024,
                driver_id="DRV-0310",
                driver_name="Lucas Henrique Souza"
            ),
            "route": ROUTE_MG_ESTRADA_REAL,
            "odometer": 38900.0
        },
        # 8. Mining Heavy Tipper - Itabira MG Iron Ore Pit
        {
            "meta": VehicleMetadata(
                vehicle_id="BR-VH-108",
                plate="VAL5M22",
                vin="9BWZZZ377VT001088",
                fleet_name="Vale Mineração Pesada",
                category=VehicleCategory.MINING_TRUCK,
                manufacturer="Mercedes-Benz",
                model="Actros 4844 8x4 Basculante",
                manufacture_year=2022,
                driver_id="DRV-0402",
                driver_name="José Roberto Fagundes"
            ),
            "route": ROUTE_CARAJAS_MINING_HEAVY,
            "odometer": 89400.0
        },
        # 9. ICU Ambulance - Brasília DF Emergency Corridor
        {
            "meta": VehicleMetadata(
                vehicle_id="BR-VH-109",
                plate="SAM1U92",
                vin="9BWZZZ377VT001099",
                fleet_name="SAMU / UTI Móvel Emergência",
                category=VehicleCategory.AMBULANCE_ICU,
                manufacturer="Renault",
                model="Master 2.3 dCi UTI Avançada",
                manufacture_year=2025,
                driver_id="DRV-0911",
                driver_name="Dr. André Luiz Brandão / Enf. Paulo"
            ),
            "route": ROUTE_DF_EMERGENCY_MOBILE,
            "odometer": 42100.0
        },
        # 10. Car Carrier (Cegonha) - Betim MG to Atibaia SP
        {
            "meta": VehicleMetadata(
                vehicle_id="BR-VH-110",
                plate="BTM6K88",
                vin="9BWZZZ377VT001100",
                fleet_name="TransAuto Betim Log",
                category=VehicleCategory.CAR_CARRIER,
                manufacturer="Volvo",
                model="VM 330 6x2 Cegonheiro",
                manufacture_year=2023,
                driver_id="DRV-0188",
                driver_name="Claudio Barbosa Lima"
            ),
            "route": ROUTE_BR381_FERNAO_DIAS,
            "odometer": 143200.0
        },
    ]

    fleet = []
    for cfg in fleet_configs:
        sim = VehicleSimulator(
            metadata=cfg["meta"],
            route=cfg["route"],
            initial_odometer_km=cfg["odometer"]
        )
        fleet.append(sim)
    return fleet
