#!/usr/bin/env python3
"""
Advanced usage example for Flight Tracker Analyzer

This script demonstrates how to use the flight_tracker_analyzer module
to perform advanced analysis of GPX flight data.
"""

from flight_tracker_analyzer import GPXParser, FlightTrack
import statistics

def analyze_flight(gpx_file):
    """
    Perform comprehensive flight analysis.
    
    Args:
        gpx_file: Path to the GPX file
    """
    print(f"Analyzing flight data from: {gpx_file}\n")
    
    # Parse the GPX file
    track = GPXParser.parse_file(gpx_file)
    
    # Get trajectory data
    lats, lons, elevations = track.get_trajectory_data()
    
    # Calculate speeds
    h_speeds = track.get_horizontal_speeds()
    v_speeds = track.get_vertical_speeds()
    
    # Filter out None values
    valid_h_speeds = [s for s in h_speeds if s is not None]
    valid_v_speeds = [s for s in v_speeds if s is not None]
    
    print("=" * 60)
    print("FLIGHT ANALYSIS REPORT")
    print("=" * 60)
    
    # Basic information
    print(f"\n📍 TRAJECTORY INFORMATION")
    print(f"   Total waypoints: {len(track.points)}")
    print(f"   Start position: {lats[0]:.6f}°, {lons[0]:.6f}°")
    print(f"   End position: {lats[-1]:.6f}°, {lons[-1]:.6f}°")
    
    # Elevation analysis
    print(f"\n⛰️  ELEVATION ANALYSIS")
    print(f"   Minimum: {min(elevations):.1f} m")
    print(f"   Maximum: {max(elevations):.1f} m")
    print(f"   Average: {statistics.mean(elevations):.1f} m")
    print(f"   Total elevation gain: {max(elevations) - min(elevations):.1f} m")
    
    if track.points[0].time:
        # Speed analysis (only if time data is available)
        print(f"\n🚀 HORIZONTAL SPEED ANALYSIS")
        print(f"   Average: {statistics.mean(valid_h_speeds):.2f} m/s ({statistics.mean(valid_h_speeds)*3.6:.2f} km/h)")
        print(f"   Median: {statistics.median(valid_h_speeds):.2f} m/s ({statistics.median(valid_h_speeds)*3.6:.2f} km/h)")
        print(f"   Maximum: {max(valid_h_speeds):.2f} m/s ({max(valid_h_speeds)*3.6:.2f} km/h)")
        print(f"   Minimum: {min(valid_h_speeds):.2f} m/s ({min(valid_h_speeds)*3.6:.2f} km/h)")
        if len(valid_h_speeds) > 1:
            print(f"   Std deviation: {statistics.stdev(valid_h_speeds):.2f} m/s")
        
        print(f"\n📈 VERTICAL SPEED ANALYSIS")
        print(f"   Average climb/descent: {statistics.mean(valid_v_speeds):.2f} m/s")
        print(f"   Max climb rate: {max(valid_v_speeds):.2f} m/s ({max(valid_v_speeds)*60:.1f} m/min)")
        print(f"   Max descent rate: {min(valid_v_speeds):.2f} m/s ({min(valid_v_speeds)*60:.1f} m/min)")
        
        # Time analysis
        duration = (track.points[-1].time - track.points[0].time).total_seconds()
        print(f"\n⏱️  TIME ANALYSIS")
        print(f"   Start time: {track.points[0].time}")
        print(f"   End time: {track.points[-1].time}")
        print(f"   Duration: {duration/60:.1f} minutes ({duration/3600:.2f} hours)")
        
        # Calculate total distance
        total_distance = sum(valid_h_speeds) * (duration / len(valid_h_speeds))
        print(f"   Estimated distance: {total_distance/1000:.2f} km")
    
    # Phase analysis (climb, cruise, descent)
    print(f"\n✈️  FLIGHT PHASES")
    climbing = sum(1 for v in valid_v_speeds if v > 0.5)
    descending = sum(1 for v in valid_v_speeds if v < -0.5)
    cruising = len(valid_v_speeds) - climbing - descending
    
    total_segments = len(valid_v_speeds)
    print(f"   Climbing segments: {climbing} ({climbing/total_segments*100:.1f}%)")
    print(f"   Cruising segments: {cruising} ({cruising/total_segments*100:.1f}%)")
    print(f"   Descending segments: {descending} ({descending/total_segments*100:.1f}%)")
    
    print(f"\n{'=' * 60}\n")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python advanced_example.py <gpx_file>")
        sys.exit(1)
    
    analyze_flight(sys.argv[1])
