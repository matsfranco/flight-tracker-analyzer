#!/usr/bin/env python3
"""
Unit tests for Flight Tracker Analyzer
"""

import unittest
import os
import tempfile
from datetime import datetime
from flight_tracker_analyzer import (
    FlightDataPoint, 
    FlightTrack, 
    GPXParser
)


class TestFlightDataPoint(unittest.TestCase):
    """Test FlightDataPoint class"""
    
    def test_creation(self):
        """Test creating a FlightDataPoint"""
        point = FlightDataPoint(37.7749, -122.4194, 100.0)
        self.assertEqual(point.lat, 37.7749)
        self.assertEqual(point.lon, -122.4194)
        self.assertEqual(point.ele, 100.0)
        self.assertIsNone(point.time)
    
    def test_creation_with_time(self):
        """Test creating a FlightDataPoint with timestamp"""
        time = datetime(2025, 10, 18, 10, 0, 0)
        point = FlightDataPoint(37.7749, -122.4194, 100.0, time)
        self.assertEqual(point.time, time)


class TestFlightTrack(unittest.TestCase):
    """Test FlightTrack class"""
    
    def setUp(self):
        """Set up test data"""
        # Create a simple track with 3 points
        self.points = [
            FlightDataPoint(37.7749, -122.4194, 10.0, datetime(2025, 10, 18, 10, 0, 0)),
            FlightDataPoint(37.7750, -122.4190, 50.0, datetime(2025, 10, 18, 10, 0, 30)),
            FlightDataPoint(37.7755, -122.4185, 100.0, datetime(2025, 10, 18, 10, 1, 0))
        ]
        self.track = FlightTrack(self.points)
    
    def test_haversine_distance(self):
        """Test haversine distance calculation"""
        # Distance between two points near San Francisco
        # Approximate distance should be a few hundred meters
        dist = FlightTrack.haversine_distance(37.7749, -122.4194, 37.7750, -122.4190)
        self.assertGreater(dist, 0)
        self.assertLess(dist, 1000)  # Should be less than 1km
    
    def test_get_trajectory_data(self):
        """Test getting trajectory data"""
        lats, lons, eles = self.track.get_trajectory_data()
        self.assertEqual(len(lats), 3)
        self.assertEqual(len(lons), 3)
        self.assertEqual(len(eles), 3)
        self.assertEqual(lats[0], 37.7749)
        self.assertEqual(eles[2], 100.0)
    
    def test_horizontal_speeds(self):
        """Test horizontal speed calculation"""
        speeds = self.track.get_horizontal_speeds()
        self.assertEqual(len(speeds), 3)
        self.assertIsNone(speeds[0])  # First point has no speed
        self.assertIsNotNone(speeds[1])
        self.assertIsNotNone(speeds[2])
        self.assertGreater(speeds[1], 0)  # Speed should be positive
    
    def test_vertical_speeds(self):
        """Test vertical speed calculation"""
        speeds = self.track.get_vertical_speeds()
        self.assertEqual(len(speeds), 3)
        self.assertIsNone(speeds[0])  # First point has no speed
        self.assertIsNotNone(speeds[1])
        self.assertIsNotNone(speeds[2])
        # All points are ascending, so speeds should be positive
        self.assertGreater(speeds[1], 0)
        self.assertGreater(speeds[2], 0)


class TestGPXParser(unittest.TestCase):
    """Test GPX parser"""
    
    def test_parse_sample_file(self):
        """Test parsing the sample GPX file"""
        # Use the sample file if it exists
        sample_file = 'sample_flight.gpx'
        if os.path.exists(sample_file):
            track = GPXParser.parse_file(sample_file)
            self.assertIsNotNone(track)
            self.assertGreater(len(track.points), 0)
            # Check that points have valid data
            for point in track.points:
                self.assertIsNotNone(point.lat)
                self.assertIsNotNone(point.lon)
                self.assertIsNotNone(point.ele)
    
    def test_parse_custom_gpx(self):
        """Test parsing a custom GPX file"""
        gpx_content = """<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="Test" xmlns="http://www.topografix.com/GPX/1/1">
  <trk>
    <trkseg>
      <trkpt lat="37.7749" lon="-122.4194">
        <ele>10.0</ele>
        <time>2025-10-18T10:00:00Z</time>
      </trkpt>
      <trkpt lat="37.7750" lon="-122.4190">
        <ele>50.0</ele>
        <time>2025-10-18T10:00:30Z</time>
      </trkpt>
    </trkseg>
  </trk>
</gpx>"""
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gpx', delete=False) as f:
            f.write(gpx_content)
            temp_file = f.name
        
        try:
            track = GPXParser.parse_file(temp_file)
            self.assertEqual(len(track.points), 2)
            self.assertEqual(track.points[0].lat, 37.7749)
            self.assertEqual(track.points[0].lon, -122.4194)
            self.assertEqual(track.points[0].ele, 10.0)
            self.assertEqual(track.points[1].ele, 50.0)
        finally:
            os.unlink(temp_file)


if __name__ == '__main__':
    unittest.main()
