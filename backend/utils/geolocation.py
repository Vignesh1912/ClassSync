import math

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance in meters between two points 
    on the earth (specified in decimal degrees) using Haversine formula.
    """
    # Earth radius in meters
    R = 6371000.0

    # Convert decimal degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Haversine formula
    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0) ** 2
    
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

def is_within_radius(slat: float, slon: float, clat: float, clon: float, radius_m: float) -> tuple[bool, float]:
    """
    Check if a student's coordinate (slat, slon) is within the radius_m boundary
    of the classroom center (clat, clon).
    Returns a tuple (is_within_radius, distance_in_meters).
    """
    try:
        dist = haversine_distance(slat, slon, clat, clon)
        return (dist <= radius_m), dist
    except (TypeError, ValueError):
        # Fallback if bad data is parsed
        return False, float('inf')
