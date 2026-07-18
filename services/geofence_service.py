"""
Geofence validation using the Haversine formula — is a reported GPS
coordinate within the allowed radius of the registered office location?
"""
import math


def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6_371_000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def is_within_geofence(lat, lon, office_lat, office_lon, radius_m):
    """Returns (is_inside: bool, distance_m: float)."""
    distance = haversine_distance_m(lat, lon, office_lat, office_lon)
    return distance <= radius_m, distance
