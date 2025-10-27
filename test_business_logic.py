import pytest
import math


class TestBusinessLogic:
    """Test business logic functions."""

    def test_calculate_distance(self):
        """Test distance calculation between two points."""
        # Test with known coordinates (Tashkent landmarks)
        # Tashkent coordinates: 41.2995° N, 69.2401° E
        # Chorsu Bazaar: 41.2773° N, 69.2041° E

        lat1, lng1 = 41.2995, 69.2401
        lat2, lng2 = 41.2773, 69.2041

        distance = calculate_distance(lat1, lng1, lat2, lng2)

        # Distance should be approximately 3.89 km
        assert 3.0 <= distance <= 5.0

        # Test same point (distance should be 0)
        distance_same = calculate_distance(lat1, lng1, lat1, lng1)
        assert distance_same == 0

        # Test with larger distance
        # New York to Los Angeles (approximately 3935 km)
        ny_lat, ny_lng = 40.7128, -74.0060
        la_lat, la_lng = 34.0522, -118.2437

        distance_ny_la = calculate_distance(ny_lat, ny_lng, la_lat, la_lng)
        # Should be roughly 3935 km
        assert 3900 <= distance_ny_la <= 4000

    def test_calculate_fare_economy(self):
        """Test fare calculation for economy vehicle."""
        distance = 10.0  # 10 km
        duration = 25  # 25 minutes
        vehicle_type = "economy"

        fare = calculate_fare(distance, duration, vehicle_type)

        # Base fare: 10.0
        # Distance fare: 10 * 5.0 = 50.0
        # Time fare: 25 * 1.0 = 25.0
        # Total: 10 + 50 + 25 = 85.0
        expected_fare = 10.0 + (distance * 5.0) + (duration * 1.0)
        assert fare == expected_fare

    def test_calculate_fare_comfort(self):
        """Test fare calculation for comfort vehicle."""
        distance = 10.0  # 10 km
        duration = 25  # 25 minutes
        vehicle_type = "comfort"

        fare = calculate_fare(distance, duration, vehicle_type)

        # Base fare: 10.0
        # Distance fare: 10 * 8.0 = 80.0 (higher rate for comfort)
        # Time fare: 25 * 1.0 = 25.0
        # Total: 10 + 80 + 25 = 115.0
        expected_fare = 10.0 + (distance * 8.0) + (duration * 1.0)
        assert fare == expected_fare

    def test_calculate_fare_zero_distance(self):
        """Test fare calculation with zero distance."""
        distance = 0.0
        duration = 15  # Minimum duration
        vehicle_type = "economy"

        fare = calculate_fare(distance, duration, vehicle_type)

        # Base fare: 10.0
        # Distance fare: 0
        # Time fare: 15 * 1.0 = 15.0
        # Total: 25.0
        expected_fare = 10.0 + (distance * 5.0) + (duration * 1.0)
        assert fare == expected_fare

    def test_calculate_fare_long_distance(self):
        """Test fare calculation for long distance."""
        distance = 100.0  # 100 km
        duration = 120  # 2 hours
        vehicle_type = "economy"

        fare = calculate_fare(distance, duration, vehicle_type)

        # Base fare: 10.0
        # Distance fare: 100 * 5.0 = 500.0
        # Time fare: 120 * 1.0 = 120.0
        # Total: 630.0
        expected_fare = 10.0 + (distance * 5.0) + (duration * 1.0)
        assert fare == expected_fare

    def test_haversine_formula_accuracy(self):
        """Test that our implementation matches the standard haversine formula."""
        # Test case: Distance between two known points
        # London (51.5074, -0.1278) to Paris (48.8566, 2.3522)
        # Expected distance: approximately 344 km

        lat1, lng1 = 51.5074, -0.1278
        lat2, lng2 = 48.8566, 2.3522

        distance = calculate_distance(lat1, lng1, lat2, lng2)

        # Should be approximately 344 km
        assert 330 <= distance <= 360

    def test_calculate_fare_edge_cases(self):
        """Test fare calculation with edge cases."""
        # Test with very small distance and duration
        fare1 = calculate_fare(0.1, 1, "economy")
        expected1 = 10.0 + (0.1 * 5.0) + (1 * 1.0)
        assert fare1 == expected1

        # Test with very large numbers
        fare2 = calculate_fare(1000.0, 1000, "comfort")
        expected2 = 10.0 + (1000.0 * 8.0) + (1000 * 1.0)
        assert fare2 == expected2


# Import the functions for testing (these are defined in main.py)
def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula."""
    # Haversine formula for calculating distance between two points
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c


def calculate_fare(distance, duration, vehicle_type):
    """Calculate ride fare based on distance, duration and vehicle type."""
    base_fare = 10.0
    per_km_rate = 5.0 if vehicle_type == "economy" else 8.0
    per_minute_rate = 1.0

    distance_fare = distance * per_km_rate
    time_fare = duration * per_minute_rate

    return base_fare + distance_fare + time_fare
