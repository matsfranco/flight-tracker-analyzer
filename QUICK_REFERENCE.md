# Flight Tracker Analyzer - Quick Reference

## Installation
```bash
pip install -r requirements.txt
```

## Basic Commands

### View Statistics
```bash
python flight_tracker_analyzer.py your_flight.gpx --stats
```

### Generate 3D Plot
```bash
python flight_tracker_analyzer.py your_flight.gpx --plot
```

### Both Statistics and Plot
```bash
python flight_tracker_analyzer.py your_flight.gpx --stats --plot
```

### Custom Output File
```bash
python flight_tracker_analyzer.py your_flight.gpx --plot --output my_flight.html
```

### Advanced Analysis
```bash
python advanced_example.py your_flight.gpx
```

## Python API Examples

### Basic Usage
```python
from flight_tracker_analyzer import GPXParser

track = GPXParser.parse_file('flight.gpx')
lats, lons, elevations = track.get_trajectory_data()
print(f"Flight has {len(track.points)} points")
```

### Calculate Speeds
```python
from flight_tracker_analyzer import GPXParser

track = GPXParser.parse_file('flight.gpx')
horizontal_speeds = track.get_horizontal_speeds()
vertical_speeds = track.get_vertical_speeds()

# Filter None values (first point has no speed)
valid_h_speeds = [s for s in horizontal_speeds if s is not None]
avg_speed_ms = sum(valid_h_speeds) / len(valid_h_speeds)
avg_speed_kmh = avg_speed_ms * 3.6
print(f"Average speed: {avg_speed_kmh:.1f} km/h")
```

### Access Individual Points
```python
from flight_tracker_analyzer import GPXParser

track = GPXParser.parse_file('flight.gpx')
for i, point in enumerate(track.points):
    print(f"Point {i}: Lat={point.lat}, Lon={point.lon}, "
          f"Ele={point.ele}m, Time={point.time}")
```

### Custom Distance Calculation
```python
from flight_tracker_analyzer import FlightTrack

# Calculate distance between two coordinates
distance = FlightTrack.haversine_distance(
    lat1=37.7749, lon1=-122.4194,  # San Francisco
    lat2=37.8044, lon2=-122.2712   # Oakland
)
print(f"Distance: {distance/1000:.2f} km")
```

## Output Interpretation

### Speed Units
- **Horizontal speed**: meters per second (m/s) and kilometers per hour (km/h)
- **Vertical speed**: meters per second (m/s) and meters per minute (m/min)

### 3D Plot Features
- **Interactive**: Rotate, zoom, and pan the 3D view
- **Color coding**: Elevation is color-coded using the Viridis colorscale
- **Hover data**: Hover over points to see exact coordinates and elevation

### Flight Phases
- **Climbing**: Vertical speed > 0.5 m/s
- **Cruising**: Vertical speed between -0.5 and 0.5 m/s
- **Descending**: Vertical speed < -0.5 m/s

## Troubleshooting

### "No module named 'plotly'"
```bash
pip install plotly
```

### "No track points found"
- Verify your GPX file contains `<trkpt>` elements
- Check that the GPX file is not empty or corrupted

### "Failed to parse GPX file"
- Ensure the file is valid XML
- Check that it follows GPX format specifications

## Sample Data
Use `sample_flight.gpx` to test the functionality:
```bash
python flight_tracker_analyzer.py sample_flight.gpx --stats --plot
```
