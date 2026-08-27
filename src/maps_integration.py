"""
Google Maps Platform Integration (Directions and Elevation APIs) with offline geodesic fallback.
Allows downloading real road polylines and elevation data dynamically when an API key is provided,
or seamlessly using high-precision geodesic interpolation.
"""

import math
import logging
from typing import List, Tuple, Optional, Dict, Any
import aiohttp
from src.config import settings

logger = logging.getLogger("telemetry.maps")


def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points in meters using Haversine formula."""
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


def calculate_bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the initial compass bearing (heading) from point 1 to point 2 in degrees (0-359.9)."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)

    y = math.sin(delta_lambda) * math.cos(phi2)
    x = (math.cos(phi1) * math.sin(phi2) -
         math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda))
    
    bearing = math.degrees(math.atan2(y, x))
    return (bearing + 360.0) % 360.0


def interpolate_coordinate(
    lat1: float, lon1: float, alt1: float,
    lat2: float, lon2: float, alt2: float,
    fraction: float
) -> Tuple[float, float, float]:
    """Linear interpolation between two 3D spatial points."""
    fraction = max(0.0, min(1.0, fraction))
    lat = lat1 + (lat2 - lat1) * fraction
    lon = lon1 + (lon2 - lon1) * fraction
    alt = alt1 + (alt2 - alt1) * fraction
    return lat, lon, alt


class GoogleMapsClient:
    """
    Client for interacting with Google Maps Directions & Elevation APIs.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GOOGLE_MAPS_API_KEY
        self.directions_url = "https://maps.googleapis.com/maps/api/directions/json"
        self.elevation_url = "https://maps.googleapis.com/maps/api/elevation/json"

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 10)

    async def fetch_route_directions(
        self, origin: Tuple[float, float], destination: Tuple[float, float], waypoints: Optional[List[Tuple[float, float]]] = None
    ) -> Optional[Dict[str, Any]]:
        """Fetch directions from Google Maps Directions API."""
        if not self.is_configured:
            logger.debug("Google Maps API key not set; using local route waypoints.")
            return None

        params = {
            "origin": f"{origin[0]},{origin[1]}",
            "destination": f"{destination[0]},{destination[1]}",
            "key": self.api_key,
            "mode": "driving",
        }
        if waypoints:
            params["waypoints"] = "|".join([f"{w[0]},{w[1]}" for w in waypoints])

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.directions_url, params=params, timeout=10.0) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("status") == "OK":
                            logger.info("Successfully fetched route from Google Maps Directions API.")
                            return data
                        else:
                            logger.warning("Google Maps Directions returned status: %s", data.get("status"))
        except Exception as e:
            logger.warning("Failed to query Google Maps Directions API: %s", e)

        return None

    async def fetch_elevation_batch(self, locations: List[Tuple[float, float]]) -> List[float]:
        """Fetch real elevation data for a list of coordinates from Google Maps Elevation API."""
        if not self.is_configured or not locations:
            return []

        loc_str = "|".join([f"{lat},{lon}" for lat, lon in locations[:50]])
        params = {"locations": loc_str, "key": self.api_key}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.elevation_url, params=params, timeout=10.0) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("status") == "OK":
                            return [res.get("elevation", 0.0) for res in data.get("results", [])]
        except Exception as e:
            logger.warning("Failed to query Google Maps Elevation API: %s", e)

        return []
