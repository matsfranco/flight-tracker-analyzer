#!/usr/bin/env python3
"""
Flight Tracker Analyzer - GPX File Processor

This script processes GPX files from Garmin Flight Activities to extract
latitude, longitude, and elevation data. It can:
- Plot 3D trajectory of the flight path
- Calculate horizontal speed based on lat/lon variations
- Calculate vertical speed based on elevation changes
"""

import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Tuple, Optional
import math


class FlightDataPoint:
    """Represents a single data point in a flight track."""
    
    def __init__(self, lat: float, lon: float, ele: float, time: Optional[datetime] = None):
        self.lat = lat
        self.lon = lon
        self.ele = ele
        self.time = time
        
    def __repr__(self):
        return f"FlightDataPoint(lat={self.lat}, lon={self.lon}, ele={self.ele}, time={self.time})"


class FlightTrack:
    """Represents a complete flight track with analysis capabilities."""
    
    def __init__(self, points: List[FlightDataPoint]):
        self.points = points
        
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the great circle distance between two points on earth (in meters).
        
        Args:
            lat1, lon1: First point coordinates in decimal degrees
            lat2, lon2: Second point coordinates in decimal degrees
            
        Returns:
            Distance in meters
        """
        R = 6371000  # Earth's radius in meters
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        # Haversine formula
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def get_horizontal_speeds(self) -> List[Optional[float]]:
        """
        Calculate horizontal speed between consecutive points.
        
        Returns:
            List of speeds in m/s. First element is None (no previous point).
        """
        speeds = [None]  # First point has no speed
        
        for i in range(1, len(self.points)):
            p1 = self.points[i - 1]
            p2 = self.points[i]
            
            distance = self.haversine_distance(p1.lat, p1.lon, p2.lat, p2.lon)
            
            # If we have timestamps, use them for accurate speed calculation
            if p1.time and p2.time:
                time_diff = (p2.time - p1.time).total_seconds()
                if time_diff > 0:
                    speed = distance / time_diff
                else:
                    speed = 0.0
            else:
                # Without time data, we can't calculate actual speed
                # Return distance instead
                speed = distance
            
            speeds.append(speed)
        
        return speeds
    
    def get_vertical_speeds(self) -> List[Optional[float]]:
        """
        Calculate vertical speed (climb/descent rate) between consecutive points.
        
        Returns:
            List of vertical speeds in m/s. First element is None.
        """
        speeds = [None]  # First point has no vertical speed
        
        for i in range(1, len(self.points)):
            p1 = self.points[i - 1]
            p2 = self.points[i]
            
            elevation_change = p2.ele - p1.ele
            
            # If we have timestamps, use them for accurate speed calculation
            if p1.time and p2.time:
                time_diff = (p2.time - p1.time).total_seconds()
                if time_diff > 0:
                    v_speed = elevation_change / time_diff
                else:
                    v_speed = 0.0
            else:
                # Without time data, return elevation change
                v_speed = elevation_change
            
            speeds.append(v_speed)
        
        return speeds
    
    def get_trajectory_data(self) -> Tuple[List[float], List[float], List[float]]:
        """
        Get trajectory data for plotting.
        
        Returns:
            Tuple of (latitudes, longitudes, elevations)
        """
        lats = [p.lat for p in self.points]
        lons = [p.lon for p in self.points]
        eles = [p.ele for p in self.points]
        return lats, lons, eles


class GPXParser:
    """Parser for GPX files."""
    
    # GPX namespace
    NS = {'gpx': 'http://www.topografix.com/GPX/1/1'}
    
    @classmethod
    def parse_file(cls, filepath: str) -> FlightTrack:
        """
        Parse a GPX file and extract flight track data.
        
        Args:
            filepath: Path to the GPX file
            
        Returns:
            FlightTrack object containing all track points
        """
        tree = ET.parse(filepath)
        root = tree.getroot()
        
        points = []
        
        # Try with namespace
        trackpoints = root.findall('.//gpx:trkpt', cls.NS)
        
        # If no points found, try without namespace (some GPX files don't use it)
        if not trackpoints:
            # Remove namespace from tag names
            for elem in root.iter():
                if '}' in elem.tag:
                    elem.tag = elem.tag.split('}', 1)[1]
            trackpoints = root.findall('.//trkpt')
        
        for trkpt in trackpoints:
            lat = float(trkpt.get('lat'))
            lon = float(trkpt.get('lon'))
            
            # Get elevation
            ele_elem = trkpt.find('ele') or trkpt.find('gpx:ele', cls.NS)
            ele = float(ele_elem.text) if ele_elem is not None else 0.0
            
            # Get time if available
            time_elem = trkpt.find('time') or trkpt.find('gpx:time', cls.NS)
            time = None
            if time_elem is not None:
                try:
                    # Parse ISO 8601 format (handles both with and without microseconds)
                    time_str = time_elem.text
                    time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    pass
            
            points.append(FlightDataPoint(lat, lon, ele, time))
        
        return FlightTrack(points)


def plot_3d_trajectory(track: FlightTrack, output_file: str = 'flight_trajectory_3d.html'):
    """
    Plot 3D trajectory using plotly.
    
    Args:
        track: FlightTrack object
        output_file: Output HTML file path
    """
    try:
        import plotly.graph_objects as go
    except ImportError:
        print("Error: plotly is required for 3D plotting. Install it with: pip install plotly")
        return
    
    lats, lons, eles = track.get_trajectory_data()
    
    # Create 3D scatter plot
    fig = go.Figure(data=[go.Scatter3d(
        x=lons,
        y=lats,
        z=eles,
        mode='lines+markers',
        marker=dict(
            size=3,
            color=eles,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Elevation (m)")
        ),
        line=dict(
            color='darkblue',
            width=2
        ),
        name='Flight Path'
    )])
    
    fig.update_layout(
        title='Flight Trajectory 3D',
        scene=dict(
            xaxis_title='Longitude',
            yaxis_title='Latitude',
            zaxis_title='Elevation (m)',
        ),
        width=1000,
        height=800
    )
    
    fig.write_html(output_file)
    print(f"3D trajectory plot saved to {output_file}")


def main():
    """Main function to demonstrate usage."""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(
        description='Process GPX files from Garmin Flight Activities'
    )
    parser.add_argument('gpx_file', help='Path to the GPX file')
    parser.add_argument('--plot', action='store_true', 
                       help='Generate 3D plot of the trajectory')
    parser.add_argument('--output', default='flight_trajectory_3d.html',
                       help='Output file for the 3D plot (default: flight_trajectory_3d.html)')
    parser.add_argument('--stats', action='store_true',
                       help='Display flight statistics')
    
    args = parser.parse_args()
    
    # Parse GPX file with error handling
    try:
        print(f"Parsing GPX file: {args.gpx_file}")
        track = GPXParser.parse_file(args.gpx_file)
        print(f"Found {len(track.points)} track points")
        
        if len(track.points) == 0:
            print("Error: No track points found in the GPX file")
            sys.exit(1)
            
    except FileNotFoundError:
        print(f"Error: File '{args.gpx_file}' not found")
        sys.exit(1)
    except ET.ParseError as e:
        print(f"Error: Failed to parse GPX file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to process GPX file: {e}")
        sys.exit(1)
    
    if args.stats:
        # Display statistics
        lats, lons, eles = track.get_trajectory_data()
        h_speeds = track.get_horizontal_speeds()
        v_speeds = track.get_vertical_speeds()
        
        print("\n=== Flight Statistics ===")
        print(f"Total points: {len(track.points)}")
        print(f"Elevation range: {min(eles):.1f}m - {max(eles):.1f}m")
        
        # Calculate horizontal speed stats (skip None values)
        valid_h_speeds = [s for s in h_speeds if s is not None]
        if valid_h_speeds:
            if track.points[0].time:
                # If we have time data, speeds are in m/s
                print(f"Horizontal speed (avg): {sum(valid_h_speeds)/len(valid_h_speeds):.1f} m/s "
                      f"({sum(valid_h_speeds)/len(valid_h_speeds)*3.6:.1f} km/h)")
                print(f"Horizontal speed (max): {max(valid_h_speeds):.1f} m/s "
                      f"({max(valid_h_speeds)*3.6:.1f} km/h)")
            else:
                print(f"Horizontal distance (avg between points): {sum(valid_h_speeds)/len(valid_h_speeds):.1f} m")
        
        # Calculate vertical speed stats
        valid_v_speeds = [s for s in v_speeds if s is not None]
        if valid_v_speeds:
            if track.points[0].time:
                print(f"Vertical speed (avg): {sum(valid_v_speeds)/len(valid_v_speeds):.2f} m/s")
                max_climb = max(valid_v_speeds)
                max_descent = min(valid_v_speeds)
                print(f"Max climb rate: {max_climb:.2f} m/s ({max_climb*60:.1f} m/min)")
                print(f"Max descent rate: {max_descent:.2f} m/s ({max_descent*60:.1f} m/min)")
            else:
                print(f"Elevation change (avg between points): {sum(valid_v_speeds)/len(valid_v_speeds):.2f} m")
        
        if track.points[0].time and track.points[-1].time:
            duration = (track.points[-1].time - track.points[0].time).total_seconds()
            print(f"Flight duration: {duration/60:.1f} minutes ({duration/3600:.2f} hours)")
    
    if args.plot:
        # Generate 3D plot
        plot_3d_trajectory(track, args.output)


if __name__ == '__main__':
    main()
