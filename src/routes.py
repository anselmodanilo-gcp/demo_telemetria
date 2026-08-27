"""
Brazilian Real-World Waypoints, Topography, and Route Definitions for Commercial Fleets.
Contains 10 unique, realistic routes spanning major Brazilian economic corridors,
urban logistics centers, mining operations, and emergency corridors.
"""

from typing import List, Dict, Any, NamedTuple
from dataclasses import dataclass


class Waypoint(NamedTuple):
    lat: float
    lon: float
    alt_m: float
    speed_limit_kmh: float
    road_name: str
    city: str
    state: str
    stop_duration_s: float = 0.0  # Optional stop e.g. toll booth, delivery, intersection


@dataclass
class RouteProfile:
    route_id: str
    route_name: str
    description: str
    total_estimated_km: float
    waypoints: List[Waypoint]


# 1. BR-116 Régis Bittencourt: São Paulo (SP) -> Curitiba (PR) [Caminhão Frigorífico]
ROUTE_BR116_SP_PR = RouteProfile(
    route_id="ROUTE_BR116_SP_PR",
    route_name="SP x Curitiba (BR-116 Régis Bittencourt)",
    description="Corredor Logístico Sul - Transporte frigorificado de congelados",
    total_estimated_km=405.0,
    waypoints=[
        Waypoint(-23.6015, -46.6970, 720.0, 60.0, "Marginal Pinheiros", "São Paulo", "SP"),
        Waypoint(-23.6190, -46.7280, 745.0, 70.0, "Rod. Régis Bittencourt km 272", "Taboão da Serra", "SP"),
        Waypoint(-23.6480, -46.8520, 775.0, 80.0, "BR-116 km 282", "Embu das Artes", "SP"),
        Waypoint(-23.7020, -46.9530, 810.0, 80.0, "BR-116 km 295", "Itapecerica da Serra", "SP"),
        Waypoint(-23.7850, -47.0120, 730.0, 75.0, "BR-116 km 312", "São Lourenço da Serra", "SP"),
        Waypoint(-23.9310, -47.0680, 685.0, 80.0, "BR-116 km 330", "Juquitiba", "SP"),
        Waypoint(-24.0500, -47.1650, 450.0, 60.0, "Serra do Cafezal (Descida)", "Miracatu", "SP"),
        Waypoint(-24.1200, -47.2300, 120.0, 60.0, "Serra do Cafezal - Curva da Ferradura", "Miracatu", "SP"),
        Waypoint(-24.2810, -47.4580, 25.0, 80.0, "BR-116 km 385", "Miracatu", "SP"),
        Waypoint(-24.4950, -47.8420, 25.0, 80.0, "BR-116 Vale do Ribeira", "Registro", "SP", stop_duration_s=8.0),
        Waypoint(-24.6950, -48.0450, 35.0, 80.0, "BR-116 km 470", "Jacupiranga", "SP"),
        Waypoint(-24.7350, -48.1250, 75.0, 80.0, "BR-116 km 485", "Cajati", "SP"),
        Waypoint(-24.7560, -48.4050, 550.0, 60.0, "Subida da Serra do Azeite", "Barra do Turvo", "SP"),
        Waypoint(-24.8750, -48.6520, 880.0, 70.0, "Divisa SP/PR - Represa Capivari-Cachoeira", "Campina Grande do Sul", "PR"),
        Waypoint(-25.2100, -49.0750, 915.0, 80.0, "BR-116 km 45", "Campina Grande do Sul", "PR"),
        Waypoint(-25.3620, -49.1950, 925.0, 70.0, "BR-116 Linha Verde Norte", "Pinhais", "PR"),
        Waypoint(-25.4380, -49.2710, 934.0, 60.0, "Linha Verde / Av. Victor Ferreira", "Curitiba", "PR"),
    ]
)

# 2. BR-163 Corredor do Agro: Rondonópolis (MT) -> Campo Grande (MS) [Bitrem Graneleiro]
ROUTE_BR163_MT_MS = RouteProfile(
    route_id="ROUTE_BR163_MT_MS",
    route_name="Rondonópolis (MT) x Campo Grande (MS) - BR-163",
    description="Eixo Rodoviário do Agronegócio - Escoamento de Soja e Milho (Bitrem 9 Eixos)",
    total_estimated_km=510.0,
    waypoints=[
        Waypoint(-16.4670, -54.6360, 227.0, 70.0, "BR-163 Polo Intermodal", "Rondonópolis", "MT"),
        Waypoint(-16.7550, -54.6850, 240.0, 80.0, "BR-163 km 85", "Ouro Branco do Sul", "MT"),
        Waypoint(-17.2150, -54.1500, 220.0, 80.0, "BR-163 Trecho Sul MT", "Itiquira", "MT"),
        Waypoint(-17.5100, -54.5120, 440.0, 80.0, "Divisa MT/MS - BR-163 km 840", "Sonora", "MS"),
        Waypoint(-18.0200, -54.5800, 282.0, 80.0, "BR-163 Trecho Pantanal", "Pedro Gomes", "MS"),
        Waypoint(-18.5060, -54.7520, 238.0, 70.0, "BR-163 Travessia Rio Taquari", "Coxim", "MS", stop_duration_s=12.0),
        Waypoint(-18.9180, -54.8430, 330.0, 80.0, "BR-163 km 680", "Rio Verde de Mato Grosso", "MS"),
        Waypoint(-19.3950, -54.5720, 658.0, 80.0, "BR-163 Chapadão", "São Gabriel do Oeste", "MS"),
        Waypoint(-19.8650, -54.3650, 629.0, 80.0, "BR-163 km 540", "Bandeirantes", "MS"),
        Waypoint(-20.1450, -54.4050, 589.0, 80.0, "BR-163 km 500", "Jaraguari", "MS"),
        Waypoint(-20.4480, -54.6290, 532.0, 60.0, "Anel Rodoviário / Av. Gury Marques", "Campo Grande", "MS"),
    ]
)

# 3. Distribuição Urbana em São Paulo: Ceagesp -> Moema -> Jardins [VUC Urbano]
ROUTE_SP_URBAN_DELIVERY = RouteProfile(
    route_id="ROUTE_SP_URBAN_DELIVERY",
    route_name="Distribuição Urbana Grande São Paulo (Ceagesp / Faria Lima / Jardins)",
    description="Entregas comerciais refrigeradas em áreas com restrição de circulação (ZMRC)",
    total_estimated_km=32.0,
    waypoints=[
        Waypoint(-23.5350, -46.7360, 725.0, 40.0, "Portão 4 CEAGESP", "São Paulo", "SP", stop_duration_s=16.0),
        Waypoint(-23.5480, -46.7120, 722.0, 50.0, "Av. Marginal Pinheiros (Pista Local)", "São Paulo", "SP"),
        Waypoint(-23.5670, -46.6950, 724.0, 50.0, "Ponte Eusébio Matoso / Pinheiros", "São Paulo", "SP"),
        Waypoint(-23.5820, -46.6830, 735.0, 40.0, "Av. Brigadeiro Faria Lima", "São Paulo", "SP", stop_duration_s=8.0),
        Waypoint(-23.5950, -46.6860, 730.0, 45.0, "Av. Pres. Juscelino Kubitschek", "São Paulo", "SP"),
        Waypoint(-23.6060, -46.6920, 730.0, 45.0, "Av. Eng. Luís Carlos Berrini", "São Paulo", "SP"),
        Waypoint(-23.6120, -46.6630, 755.0, 40.0, "Av. Ibirapuera / Moema", "São Paulo", "SP", stop_duration_s=12.0),
        Waypoint(-23.5880, -46.6530, 760.0, 50.0, "Av. 23 de Maio / Corredor Norte-Sul", "São Paulo", "SP"),
        Waypoint(-23.5630, -46.6540, 820.0, 40.0, "Av. Paulista (MASP)", "São Paulo", "SP"),
        Waypoint(-23.5680, -46.6670, 815.0, 30.0, "Rua Oscar Freire / Jardins", "São Paulo", "SP", stop_duration_s=20.0),
    ]
)

# 4. Rio de Janeiro Express: Porto Maravilha -> Cabo Frio (Ponte Rio-Niterói / BR-101 / RJ-124) [Van Expressa]
ROUTE_RJ_COASTAL_LOGISTICS = RouteProfile(
    route_id="ROUTE_RJ_COASTAL_LOGISTICS",
    route_name="Rio de Janeiro (Porto) x Região dos Lagos (Cabo Frio)",
    description="Logística expressa e-commerce / peças offshore via Ponte Rio-Niterói e Via Lagos",
    total_estimated_km=155.0,
    waypoints=[
        Waypoint(-22.8970, -43.1890, 5.0, 50.0, "Porto Maravilha / Av. Rodrigues Alves", "Rio de Janeiro", "RJ"),
        Waypoint(-22.8750, -43.1620, 60.0, 80.0, "Ponte Rio-Niterói (Vão Central)", "Niterói", "RJ"),
        Waypoint(-22.8720, -43.0850, 10.0, 70.0, "Acesso Alameda São Boaventura", "Niterói", "RJ"),
        Waypoint(-22.8120, -42.9850, 20.0, 90.0, "BR-101 Trevo de Manilha", "Itaboraí", "RJ"),
        Waypoint(-22.7150, -42.6280, 40.0, 90.0, "BR-101 km 270", "Rio Bonito", "RJ"),
        Waypoint(-22.6850, -42.4200, 30.0, 100.0, "RJ-124 Via Lagos km 15", "Silva Jardim", "RJ"),
        Waypoint(-22.7520, -42.2150, 20.0, 100.0, "RJ-124 km 42", "Iguaba Grande", "RJ"),
        Waypoint(-22.8420, -42.1020, 15.0, 80.0, "RJ-140 km 8", "São Pedro da Aldeia", "RJ"),
        Waypoint(-22.8800, -42.0280, 4.0, 60.0, "Av. Assumpção / Centro", "Cabo Frio", "RJ"),
    ]
)

# 5. Linha Executiva Rodoviária: São Paulo (Tietê) -> Rio de Janeiro (Novo Rio) - Via Dutra [Ônibus Rodoviário]
ROUTE_BR116_DUTRA_PASSENGER = RouteProfile(
    route_id="ROUTE_BR116_DUTRA_PASSENGER",
    route_name="São Paulo (Tietê) x Rio de Janeiro (Novo Rio) - Via Dutra BR-116",
    description="Transporte interestadual rodoviário de passageiros classe executiva leito",
    total_estimated_km=430.0,
    waypoints=[
        Waypoint(-23.5160, -46.6240, 725.0, 50.0, "Terminal Rodoviário do Tietê", "São Paulo", "SP"),
        Waypoint(-23.4680, -46.4950, 759.0, 80.0, "BR-116 Via Dutra km 220", "Guarulhos", "SP"),
        Waypoint(-23.3980, -46.3200, 755.0, 90.0, "BR-116 Dutra km 198", "Arujá", "SP"),
        Waypoint(-23.1920, -45.8820, 600.0, 90.0, "BR-116 Dutra km 150", "São José dos Campos", "SP"),
        Waypoint(-23.0280, -45.5580, 550.0, 90.0, "BR-116 Dutra km 112", "Taubaté", "SP"),
        Waypoint(-22.8520, -45.2280, 530.0, 90.0, "BR-116 Dutra km 70", "Aparecida", "SP", stop_duration_s=8.0),
        Waypoint(-22.5400, -44.7800, 480.0, 90.0, "BR-116 Dutra km 10 (Divisa SP/RJ)", "Queluz", "SP"),
        Waypoint(-22.4680, -44.4480, 400.0, 80.0, "BR-116 Dutra km 305", "Resende", "RJ"),
        Waypoint(-22.5200, -44.1050, 380.0, 80.0, "BR-116 Rod. Presidente Dutra", "Volta Redonda", "RJ"),
        Waypoint(-22.6850, -43.8920, 450.0, 60.0, "Serra das Araras (Topo)", "Piraí", "RJ"),
        Waypoint(-22.7520, -43.7850, 60.0, 50.0, "Serra das Araras (Base)", "Paracambi", "RJ"),
        Waypoint(-22.7580, -43.4520, 25.0, 80.0, "BR-116 Dutra km 175", "Nova Iguaçu", "RJ"),
        Waypoint(-22.8980, -43.2080, 3.0, 50.0, "Terminal Rodoviário Novo Rio", "Rio de Janeiro", "RJ"),
    ]
)

# 6. Distribuição de Combustíveis: REPLAN Paulínia -> Bauru (SP-300 / Rod. Mal. Rondon) [Caminhão Tanque]
ROUTE_SP300_HAZMAT_FUEL = RouteProfile(
    route_id="ROUTE_SP300_HAZMAT_FUEL",
    route_name="REPLAN Paulínia x Bauru (SP-330 / SP-300 Mal. Rondon)",
    description="Transporte rodoviário de produtos perigosos - Gasolina / Diesel S10 granel líquido",
    total_estimated_km=240.0,
    waypoints=[
        Waypoint(-22.7210, -47.1520, 590.0, 40.0, "Refinaria de Paulínia (REPLAN)", "Paulínia", "SP", stop_duration_s=16.0),
        Waypoint(-22.8250, -47.0980, 685.0, 70.0, "Rod. Eng. Ermênio de Oliveira Penteado", "Campinas", "SP"),
        Waypoint(-22.7380, -47.3320, 570.0, 80.0, "SP-304 Rod. Luiz de Queiroz", "Americana", "SP"),
        Waypoint(-22.7250, -47.6490, 547.0, 70.0, "SP-304 Anel Viário", "Piracicaba", "SP"),
        Waypoint(-22.8800, -48.4420, 804.0, 65.0, "SP-300 Cuesta de Botucatu (Subida)", "Botucatu", "SP"),
        Waypoint(-22.7320, -48.5720, 709.0, 80.0, "SP-300 Rod. Marechal Rondon", "São Manuel", "SP"),
        Waypoint(-22.5980, -48.7950, 550.0, 80.0, "SP-300 km 295", "Lençóis Paulista", "SP"),
        Waypoint(-22.3140, -49.0580, 526.0, 60.0, "SP-300 Distrito Industrial Bauru", "Bauru", "SP"),
    ]
)

# 7. Apoio Operacional Estrada Real MG: Belo Horizonte -> Ouro Preto -> Cons. Lafaiete [Picape 4x4]
ROUTE_MG_ESTRADA_REAL = RouteProfile(
    route_id="ROUTE_MG_ESTRADA_REAL",
    route_name="Belo Horizonte x Ouro Preto x Conselheiro Lafaiete (BR-356 / BR-040)",
    description="Inspeção técnica e apoio de infraestrutura em terreno montanhoso",
    total_estimated_km=145.0,
    waypoints=[
        Waypoint(-19.9200, -43.9380, 858.0, 60.0, "Av. Raja Gabaglia / Anel Rodoviário", "Belo Horizonte", "MG"),
        Waypoint(-20.0150, -43.9550, 1020.0, 70.0, "BR-356 Trevo de Nova Lima", "Nova Lima", "MG"),
        Waypoint(-20.1250, -43.9780, 1420.0, 60.0, "Serra da Moeda / Topo do Mundo", "Nova Lima", "MG"),
        Waypoint(-20.2520, -43.8050, 830.0, 70.0, "BR-356 Vale dos Inconfidentes", "Itabirito", "MG"),
        Waypoint(-20.3850, -43.5040, 1180.0, 40.0, "Praça Tiradentes / Centro Histórico", "Ouro Preto", "MG", stop_duration_s=14.0),
        Waypoint(-20.3780, -43.4150, 697.0, 50.0, "Rod. dos Inconfidentes", "Mariana", "MG"),
        Waypoint(-20.5200, -43.6550, 890.0, 60.0, "MG-129 Estrada Real", "Ouro Branco", "MG"),
        Waypoint(-20.6620, -43.7850, 995.0, 60.0, "BR-040 km 630", "Conselheiro Lafaiete", "MG"),
    ]
)

# 8. Mineração Pesada Fora de Estrada: Mina Cauê / Conceição Itabira (MG) [Actros 4844 8x4]
ROUTE_CARAJAS_MINING_HEAVY = RouteProfile(
    route_id="ROUTE_CARAJAS_MINING_HEAVY",
    route_name="Complexo Minerador Itabira (Mina Cauê x Usina Conceição)",
    description="Ciclo fora-de-estrada pesado de transporte de minério de ferro em cavas profundas",
    total_estimated_km=18.0,
    waypoints=[
        Waypoint(-19.6150, -43.2380, 680.0, 25.0, "Cava Sul - Ponto de Carregamento Escavadeira 04", "Itabira", "MG", stop_duration_s=20.0),
        Waypoint(-19.6200, -43.2320, 740.0, 30.0, "Rampa Interna de Transporte R-02", "Itabira", "MG"),
        Waypoint(-19.6280, -43.2250, 810.0, 35.0, "Acesso Britador Primário Cauê", "Itabira", "MG", stop_duration_s=15.0),
        Waypoint(-19.6380, -43.2100, 835.0, 40.0, "Estrada de Serviço Mina Conceição", "Itabira", "MG"),
        Waypoint(-19.6450, -43.1980, 810.0, 35.0, "Usina de Beneficiamento de Minério", "Itabira", "MG"),
        Waypoint(-19.6520, -43.1850, 940.0, 30.0, "Rampa Pilha de Homogeneização", "Itabira", "MG"),
        Waypoint(-19.6350, -43.1750, 760.0, 25.0, "Pátio Ferroviário de Carregamento de Vagões", "Itabira", "MG", stop_duration_s=18.0),
    ]
)

# 9. UTI Móvel Emergência: Brasília DF (Hospital de Base -> Eixo Monumental -> Lago Sul) [Ambulância]
ROUTE_DF_EMERGENCY_MOBILE = RouteProfile(
    route_id="ROUTE_DF_EMERGENCY_MOBILE",
    route_name="Brasília DF - Corredor de Emergência (HBDF x Lago Sul)",
    description="Deslocamento prioritário com sirene ativa para resgate / transferência UTI móvel",
    total_estimated_km=22.0,
    waypoints=[
        Waypoint(-15.7980, -47.8920, 1170.0, 50.0, "Hospital de Base do DF (HBDF) Pronto Socorro", "Brasília", "DF", stop_duration_s=10.0),
        Waypoint(-15.7920, -47.8880, 1175.0, 70.0, "Eixo Monumental Oeste / Torre de TV", "Brasília", "DF"),
        Waypoint(-15.7985, -47.8640, 1160.0, 80.0, "Esplanada dos Ministérios / Catedral", "Brasília", "DF"),
        Waypoint(-15.8010, -47.8520, 1150.0, 80.0, "Praça dos Três Poderes", "Brasília", "DF"),
        Waypoint(-15.8190, -47.8480, 1050.0, 75.0, "Via L4 Sul", "Brasília", "DF"),
        Waypoint(-15.8270, -47.8310, 1010.0, 70.0, "Ponte Juscelino Kubitschek (Ponte JK)", "Brasília", "DF"),
        Waypoint(-15.8360, -47.8220, 1045.0, 60.0, "SHIS QI 15 Lago Sul", "Brasília", "DF"),
        Waypoint(-15.8450, -47.8760, 1080.0, 50.0, "Hospital Brasília / Pronto Atendimento", "Brasília", "DF", stop_duration_s=15.0),
    ]
)

# 10. Transporte de Veículos (Cegonha): Polo Betim MG -> BR-381 Fernão Dias -> Atibaia SP [Caminhão Cegonha]
ROUTE_BR381_FERNAO_DIAS = RouteProfile(
    route_id="ROUTE_BR381_FERNAO_DIAS",
    route_name="Polo Betim (MG) x Atibaia (SP) - BR-381 Fernão Dias",
    description="Transporte de veículos novos (Cegonha 11 carros) Betim/MG para centros de distribuição SP",
    total_estimated_km=520.0,
    waypoints=[
        Waypoint(-19.9720, -44.1980, 860.0, 60.0, "Complexo Automotivo Stellantis Betim", "Betim", "MG", stop_duration_s=15.0),
        Waypoint(-20.0450, -44.3050, 780.0, 80.0, "BR-381 Fernão Dias km 510", "Igarapé", "MG"),
        Waypoint(-20.3950, -44.7550, 940.0, 80.0, "BR-381 km 560", "Itaguara", "MG"),
        Waypoint(-20.7680, -44.9200, 980.0, 80.0, "BR-381 km 615", "Oliveira", "MG"),
        Waypoint(-21.1450, -45.0850, 840.0, 80.0, "BR-381 km 680", "Perdões", "MG"),
        Waypoint(-21.2480, -45.0020, 919.0, 80.0, "BR-381 Trevo de Lavras", "Lavras", "MG"),
        Waypoint(-21.6980, -45.2550, 890.0, 80.0, "BR-381 km 750", "Três Corações", "MG", stop_duration_s=10.0),
        Waypoint(-22.2350, -45.9350, 832.0, 80.0, "BR-381 km 850", "Pouso Alegre", "MG"),
        Waypoint(-22.8550, -46.3150, 960.0, 75.0, "Serra da Mantiqueira / Divisa MG-SP", "Extrema", "MG"),
        Waypoint(-22.9520, -46.5420, 817.0, 75.0, "BR-381 km 20", "Bragança Paulista", "SP"),
        Waypoint(-23.1180, -46.5560, 803.0, 70.0, "Entroncamento Rod. Dom Pedro I (SP-065)", "Atibaia", "SP"),
    ]
)

ALL_ROUTES: List[RouteProfile] = [
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
]
