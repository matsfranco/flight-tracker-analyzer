#!/usr/bin/env python3
"""
Flight Tracker Analyzer - GPX File Processor

This script processes GPX files from Garmin Flight Activities to extract
latitude, longitude, and elevation data. It can:
- Plot 3D trajectory of the flight path
- Calculate horizontal speed based on lat/lon variations (displayed in knots)
- Calculate vertical speed based on elevation changes (displayed in ft/min)
- Display distances in nautical miles and elevations in feet
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


def meters_to_feet(meters: float) -> float:
    """Convert meters to feet."""
    return meters * 3.28084


def meters_to_nautical_miles(meters: float) -> float:
    """Convert meters to nautical miles."""
    return meters * 0.000539957


def mps_to_knots(mps: float) -> float:
    """Convert meters per second to knots (nautical miles per hour)."""
    return mps * 1.94384


def mps_to_fpm(mps: float) -> float:
    """Convert meters per second to feet per minute."""
    return mps * 196.85


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


def create_elevation_time_chart(track: FlightTrack) -> Optional[object]:
    """
    Create an elevation vs time chart.
    
    Args:
        track: FlightTrack object
        
    Returns:
        Plotly trace for elevation vs time chart or None if no time data
    """
    try:
        import plotly.graph_objects as go
    except ImportError:
        return None
    
    # Check if we have time data
    if not track.points or not track.points[0].time:
        print("Warning: No time data available for elevation vs time chart")
        return None
    
    # Extract time and elevation data
    times = []
    elevations_feet = []
    
    for point in track.points:
        if point.time:
            times.append(point.time)
            elevations_feet.append(meters_to_feet(point.ele))
    
    if not times:
        return None
    
    # Calculate elapsed time from start
    start_time = times[0]
    elapsed_minutes = [(t - start_time).total_seconds() / 60.0 for t in times]
    
    # Create elevation trace
    elevation_trace = go.Scatter(
        x=elapsed_minutes,
        y=elevations_feet,
        mode='lines+markers',
        name='Elevation',
        line=dict(color='darkgreen', width=2),
        marker=dict(size=3, color='darkgreen'),
        hovertemplate='<b>Elevation vs Time</b><br>' +
                     'Time: %{x:.1f} min<br>' +
                     'Elevation: %{y:.1f} ft<br>' +
                     '<extra></extra>'
    )
    
    return elevation_trace, elapsed_minutes, elevations_feet


def create_speed_time_chart(track: FlightTrack) -> Optional[object]:
    """
    Create a speed vs time chart.
    
    Args:
        track: FlightTrack object
        
    Returns:
        Plotly trace for speed vs time chart or None if no time data
    """
    try:
        import plotly.graph_objects as go
    except ImportError:
        return None
    
    # Check if we have time data
    if not track.points or not track.points[0].time:
        print("Warning: No time data available for speed vs time chart")
        return None
    
    # Get horizontal speeds (in m/s)
    speeds_ms = track.get_horizontal_speeds()
    
    # Extract time data and convert speeds to knots
    times = []
    speeds_knots = []
    
    for i, point in enumerate(track.points):
        if point.time and speeds_ms[i] is not None:
            times.append(point.time)
            # Convert m/s to knots (nautical miles per hour)
            speeds_knots.append(mps_to_knots(speeds_ms[i]))
    
    if not times:
        return None
    
    # Calculate elapsed time from start
    start_time = times[0]
    elapsed_minutes = [(t - start_time).total_seconds() / 60.0 for t in times]
    
    # Create speed trace
    speed_trace = go.Scatter(
        x=elapsed_minutes,
        y=speeds_knots,
        mode='lines+markers',
        name='Ground Speed',
        line=dict(color='darkred', width=2),
        marker=dict(size=3, color='darkred'),
        hovertemplate='<b>Speed vs Time</b><br>' +
                     'Time: %{x:.1f} min<br>' +
                     'Speed: %{y:.1f} knots<br>' +
                     '<extra></extra>'
    )
    
    return speed_trace, elapsed_minutes, speeds_knots


def plot_3d_trajectory(track: FlightTrack, output_file: str = 'flight_trajectory_3d.html', 
                      elevation_scale: float = 1.0):
    """
    Plot 3D trajectory and elevation vs time chart using plotly with subplots.
    
    Args:
        track: FlightTrack object
        output_file: Output HTML file path
        elevation_scale: Scale factor for elevation (e.g., 10.0 to exaggerate elevation by 10x)
    """
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        print("Error: plotly is required for 3D plotting. Install it with: pip install plotly")
        return
    
    # Get trajectory data
    x_coords, y_coords, eles = track.get_trajectory_data()
    
    # Convert elevations to feet for display
    eles_feet = [meters_to_feet(ele) for ele in eles]
    
    # Apply elevation scaling for 3D plot
    scaled_eles = [ele * elevation_scale for ele in eles]
    
    # Create subplot layout: 3D plot on top, elevation and speed charts below
    fig = make_subplots(
        rows=3, cols=1,
        row_heights=[0.6, 0.2, 0.2],
        specs=[
            [{"type": "scatter3d"}],
            [{"type": "xy"}],
            [{"type": "xy"}]
        ],
        subplot_titles=("3D Flight Trajectory", "Elevation vs Time", "Ground Speed vs Time"),
        vertical_spacing=0.08
    )
    
    # Create the 3D trajectory trace
    trajectory_trace = go.Scatter3d(
        x=x_coords,
        y=y_coords,
        z=scaled_eles,
        mode='lines+markers',
        marker=dict(
            size=3,
            color=eles_feet,  # Use elevation in feet for color scale
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Elevation (ft)", x=1.02, y=0.8)  # Position colorbar to the right
        ),
        line=dict(
            color='darkblue',
            width=2
        ),
        name='Flight Path',
        hovertemplate='<b>Position</b><br>' +
                     'Easting: %{x:.1f}m<br>' +
                     'Northing: %{y:.1f}m<br>' +
                     'Elevation: %{customdata:.1f}ft<br>' +
                     '<extra></extra>',
        customdata=eles_feet  # Pass elevations in feet for hover
    )
    
    # Add 3D trajectory to first subplot (row 1)
    fig.add_trace(trajectory_trace, row=1, col=1)
    
    # Create elevation vs time chart
    elevation_chart_data = create_elevation_time_chart(track)
    if elevation_chart_data:
        elevation_trace, elapsed_minutes, elevations_feet = elevation_chart_data
        fig.add_trace(elevation_trace, row=2, col=1)
        
        # Update elevation chart layout
        fig.update_xaxes(title_text="Time (minutes)", row=2, col=1)
        fig.update_yaxes(title_text="Elevation (ft)", row=2, col=1)
    else:
        # Add a placeholder text if no time data
        fig.add_annotation(
            text="No time data available for elevation chart",
            x=0.5, y=0.5,
            xref="x2", yref="y2",
            showarrow=False,
            font=dict(size=12, color="gray"),
            row=2, col=1
        )
    
    # Create speed vs time chart
    speed_chart_data = create_speed_time_chart(track)
    if speed_chart_data:
        speed_trace, elapsed_minutes_speed, speeds_knots = speed_chart_data
        fig.add_trace(speed_trace, row=3, col=1)
        
        # Update speed chart layout
        fig.update_xaxes(title_text="Time (minutes)", row=3, col=1)
        fig.update_yaxes(title_text="Ground Speed (knots)", row=3, col=1)
    else:
        # Add a placeholder text if no time data
        fig.add_annotation(
            text="No time data available for speed chart",
            x=0.5, y=0.5,
            xref="x3", yref="y3",
            showarrow=False,
            font=dict(size=12, color="gray"),
            row=3, col=1
        )
    
    # Get reference coordinates for title
    ref_lat = track.points[0].lat if track.points else 0
    ref_lon = track.points[0].lon if track.points else 0
    
    # Update title to show elevation scaling if applied
    scale_info = f" (elevation scale: {elevation_scale}x)" if elevation_scale != 1.0 else ""
    
    # Update 3D scene layout
    fig.update_layout(
        title=f'Flight Analysis{scale_info}<br><sub>Coordinates in meters relative to origin: {ref_lat:.6f}°, {ref_lon:.6f}°</sub>',
        scene=dict(
            xaxis_title='Easting (m)',
            yaxis_title='Northing (m)', 
            zaxis_title=f'Elevation (m){" x" + str(elevation_scale) if elevation_scale != 1.0 else ""}',
            aspectmode='data'  # This ensures equal scaling on all axes
        ),
        width=1400,
        height=1000,  # Increased height for three charts
        showlegend=True
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
        
        # Convert and display elevation in feet
        eles_feet = [meters_to_feet(ele) for ele in eles]
        print(f"Elevation range: {min(eles_feet):.1f}ft - {max(eles_feet):.1f}ft")
        print(f"Elevation range (meters): {min(eles):.1f}m - {max(eles):.1f}m")
        
        # Calculate coordinate ranges in meters and convert to nautical miles
        x_range = max(x_coords) - min(x_coords)
        y_range = max(y_coords) - min(y_coords)
        x_range_nm = meters_to_nautical_miles(x_range)
        y_range_nm = meters_to_nautical_miles(y_range)
        print(f"Flight area: {x_range_nm:.1f}NM × {y_range_nm:.1f}NM (East-West × North-South)")
        print(f"Flight area (meters): {x_range:.0f}m × {y_range:.0f}m (East-West × North-South)")
        
        # Calculate horizontal speed stats (skip None values)
        valid_h_speeds = [s for s in h_speeds if s is not None]
        if valid_h_speeds:
            if track.points[0].time:
                # Convert to knots for aviation standard
                avg_speed_knots = mps_to_knots(sum(valid_h_speeds)/len(valid_h_speeds))
                max_speed_knots = mps_to_knots(max(valid_h_speeds))
                print(f"Horizontal speed (avg): {avg_speed_knots:.1f} knots "
                      f"({sum(valid_h_speeds)/len(valid_h_speeds):.1f} m/s)")
                print(f"Horizontal speed (max): {max_speed_knots:.1f} knots "
                      f"({max(valid_h_speeds):.1f} m/s)")
            else:
                avg_distance_nm = meters_to_nautical_miles(sum(valid_h_speeds)/len(valid_h_speeds))
                print(f"Horizontal distance (avg between points): {avg_distance_nm:.2f} NM "
                      f"({sum(valid_h_speeds)/len(valid_h_speeds):.1f} m)")
        
        # Calculate vertical speed stats
        valid_v_speeds = [s for s in v_speeds if s is not None]
        if valid_v_speeds:
            if track.points[0].time:
                # Convert to ft/min for aviation standard
                avg_vspeed_fpm = mps_to_fpm(sum(valid_v_speeds)/len(valid_v_speeds))
                max_climb_fpm = mps_to_fpm(max(valid_v_speeds))
                max_descent_fpm = mps_to_fpm(min(valid_v_speeds))
                print(f"Vertical speed (avg): {avg_vspeed_fpm:.0f} ft/min "
                      f"({sum(valid_v_speeds)/len(valid_v_speeds):.2f} m/s)")
                print(f"Max climb rate: {max_climb_fpm:.0f} ft/min "
                      f"({max(valid_v_speeds):.2f} m/s)")
                print(f"Max descent rate: {max_descent_fpm:.0f} ft/min "
                      f"({min(valid_v_speeds):.2f} m/s)")
            else:
                avg_elev_change_ft = meters_to_feet(sum(valid_v_speeds)/len(valid_v_speeds))
                print(f"Elevation change (avg between points): {avg_elev_change_ft:.1f} ft "
                      f"({sum(valid_v_speeds)/len(valid_v_speeds):.2f} m)")
        
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
