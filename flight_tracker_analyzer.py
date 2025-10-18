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


def lat_lon_to_meters(lat: float, lon: float, ref_lat: float, ref_lon: float) -> Tuple[float, float]:
    """
    Convert latitude and longitude to local coordinates in meters.
    Uses a simple equirectangular projection relative to a reference point.
    
    Args:
        lat, lon: Point coordinates in decimal degrees
        ref_lat, ref_lon: Reference point (origin) in decimal degrees
    
    Returns:
        Tuple of (x, y) coordinates in meters
    """
    # Earth's radius in meters
    R = 6371000
    
    # Convert degrees to radians
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    ref_lat_rad = math.radians(ref_lat)
    ref_lon_rad = math.radians(ref_lon)
    
    # Calculate differences
    delta_lat = lat_rad - ref_lat_rad
    delta_lon = lon_rad - ref_lon_rad
    
    # Convert to meters using equirectangular projection
    # x = R * delta_lon * cos(ref_lat)
    # y = R * delta_lat
    x = R * delta_lon * math.cos(ref_lat_rad)
    y = R * delta_lat
    
    return x, y


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
        Get trajectory data for plotting with coordinates in meters.
        
        Returns:
            Tuple of (x_meters, y_meters, elevations) where x,y are in meters
            relative to the first point as origin.
        """
        if not self.points:
            return [], [], []
        
        # Use first point as reference (origin)
        ref_lat = self.points[0].lat
        ref_lon = self.points[0].lon
        
        x_coords = []
        y_coords = []
        elevations = []
        
        for point in self.points:
            x, y = lat_lon_to_meters(point.lat, point.lon, ref_lat, ref_lon)
            x_coords.append(x)
            y_coords.append(y)
            elevations.append(point.ele)
        
        return x_coords, y_coords, elevations
    
    def get_trajectory_data_degrees(self) -> Tuple[List[float], List[float], List[float]]:
        """
        Get trajectory data in original degrees (for compatibility).
        
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


def plot_3d_trajectory(track: FlightTrack, output_file: str = 'flight_trajectory_3d.html', 
                      elevation_scale: float = 1.0):
    """
    Plot 3D trajectory using plotly with coordinates in meters.
    
    Args:
        track: FlightTrack object
        output_file: Output HTML file path
        elevation_scale: Scale factor for elevation (e.g., 10.0 to exaggerate elevation by 10x)
    """
    try:
        import plotly.graph_objects as go
    except ImportError:
        print("Error: plotly is required for 3D plotting. Install it with: pip install plotly")
        return
    
    x_coords, y_coords, eles = track.get_trajectory_data()
    
    # Apply elevation scaling
    scaled_eles = [ele * elevation_scale for ele in eles]
    
    # Create the main 3D scatter plot
    trajectory_trace = go.Scatter3d(
        x=x_coords,
        y=y_coords,
        z=scaled_eles,
        mode='lines+markers',
        marker=dict(
            size=3,
            color=eles,  # Use original elevation for color scale
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Elevation (m)")
        ),
        line=dict(
            color='darkblue',
            width=2
        ),
        name='Flight Path',
        hovertemplate='<b>Position</b><br>' +
                     'Easting: %{x:.1f}m<br>' +
                     'Northing: %{y:.1f}m<br>' +
                     'Elevation: %{customdata:.1f}m<br>' +
                     '<extra></extra>',
        customdata=eles  # Pass original elevations for hover
    )
    
    fig = go.Figure(data=[trajectory_trace])
    
    # Get reference coordinates for title
    ref_lat = track.points[0].lat if track.points else 0
    ref_lon = track.points[0].lon if track.points else 0
    
    # Update title to show elevation scaling if applied
    scale_info = f" (elevation scale: {elevation_scale}x)" if elevation_scale != 1.0 else ""
    
    fig.update_layout(
        title=f'Flight Trajectory 3D{scale_info}<br><sub>Coordinates in meters relative to origin: {ref_lat:.6f}°, {ref_lon:.6f}°</sub>',
        scene=dict(
            xaxis_title='Easting (m)',
            yaxis_title='Northing (m)', 
            zaxis_title=f'Elevation (m){" x" + str(elevation_scale) if elevation_scale != 1.0 else ""}',
            aspectmode='data'  # This ensures equal scaling on all axes
        ),
        width=1000,
        height=800
    )
    
    fig.write_html(output_file)
    print(f"3D trajectory plot saved to {output_file}")
    print(f"All coordinates are in meters relative to origin: {ref_lat:.6f}°, {ref_lon:.6f}°")


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
    parser.add_argument('--elevation-scale', type=float, default=1.0,
                       help='Scale factor for elevation visualization (default: 1.0). '
                            'Use values > 1.0 to exaggerate elevation changes (e.g., 10.0 for 10x scaling)')
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
        x_coords, y_coords, eles = track.get_trajectory_data()
        lats, lons, _ = track.get_trajectory_data_degrees()  # For lat/lon ranges
        h_speeds = track.get_horizontal_speeds()
        v_speeds = track.get_vertical_speeds()
        
        print("\n=== Flight Statistics ===")
        print(f"Total points: {len(track.points)}")
        print(f"Latitude range: {min(lats):.6f}° - {max(lats):.6f}°")
        print(f"Longitude range: {min(lons):.6f}° - {max(lons):.6f}°")
        print(f"Elevation range: {min(eles):.1f}m - {max(eles):.1f}m")
        
        # Calculate coordinate ranges in meters
        x_range = max(x_coords) - min(x_coords)
        y_range = max(y_coords) - min(y_coords)
        print(f"Flight area: {x_range:.0f}m × {y_range:.0f}m (East-West × North-South)")
        
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
        # Generate 3D plot with elevation scaling
        plot_3d_trajectory(track, args.output, args.elevation_scale)
        if args.elevation_scale != 1.0:
            print(f"Elevation scaled by factor: {args.elevation_scale}x")


if __name__ == '__main__':
    main()
