# flight-tracker-analyzer
GPX processor to analyze Garmin Flight Activities data

## Overview

This Python script processes GPX files from Garmin Flight Activities to extract and analyze flight data. It provides:
- 3D trajectory visualization with elevation scaling
- Horizontal speed calculation in knots (nautical miles per hour)
- Vertical speed calculation in ft/min (feet per minute)
- Flight area measurements in nautical miles (NM)
- Elevation data in feet (ft)
- Comprehensive flight statistics using aviation standard units

## Installation

1. Clone the repository:
```bash
git clone https://github.com/matsfranco/flight-tracker-analyzer.git
cd flight-tracker-analyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Parse a GPX file and display statistics:
```bash
python flight_tracker_analyzer.py sample_flight.gpx --stats
```

### Generate 3D Trajectory Plot

Create an interactive 3D visualization:
```bash
python flight_tracker_analyzer.py sample_flight.gpx --plot --stats
```

This will generate an HTML file (`flight_trajectory_3d.html` by default) with an interactive 3D plot.

### Custom Output File

Specify a custom output file for the plot:
```bash
python flight_tracker_analyzer.py sample_flight.gpx --plot --output my_flight.html
```

### Command Line Options

- `gpx_file`: Path to the GPX file (required)
- `--plot`: Generate a 3D trajectory plot
- `--output`: Specify output HTML file for the plot (default: flight_trajectory_3d.html)
- `--elevation-scale`: Scale factor for elevation visualization (default: 1.0). Use values > 1.0 to exaggerate elevation changes (e.g., 10.0 for 10x scaling)
- `--include-map`: Include background map information and external mapping links
- `--stats`: Display flight statistics including speeds in knots, vertical speeds in ft/min, distances in nautical miles, and elevations in feet

### Background Map Integration

The `--include-map` option provides geographical context for your flight trajectory:

```bash
# Generate plot with mapping information
python flight_tracker_analyzer.py flight.gpx --plot --include-map --elevation-scale 10.0
```

This feature provides:
- **Ground reference plane** in the 3D visualization
- **Direct links** to Google Maps, OpenStreetMap, and Google Earth Web
- **Flight area coordinates** for use in external mapping tools
- **Suggestions** for advanced GPS visualization tools

**External Mapping Options:**
- **Google Earth Pro/Web**: Import the GPX file directly for satellite imagery context
- **QGIS**: Free GIS software for professional analysis with multiple map layers
- **GPS Visualizer**: Online tool for quick map overlay visualization
- **Garmin Connect**: If using Garmin devices, provides native mapping integration

### Elevation Scaling for Better Visualization

Since horizontal distances are typically in tens of kilometers while elevation changes are only in hundreds of meters, elevation variations can be hard to see in 3D plots. Use the `--elevation-scale` parameter to exaggerate elevation changes:

```bash
# Normal scaling (default)
python flight_tracker_analyzer.py sample_flight.gpx --plot

# 5x elevation scaling - good for moderate emphasis
python flight_tracker_analyzer.py sample_flight.gpx --plot --elevation-scale 5.0

# 10x elevation scaling - for strong emphasis on elevation changes
python flight_tracker_analyzer.py sample_flight.gpx --plot --elevation-scale 10.0
```

The scaling factor only affects the visual representation in the 3D plot. All statistics and hover information show the actual elevation values.

## Features

### Data Extraction

The script extracts the following data from GPX files:
- Latitude (decimal degrees)
- Longitude (decimal degrees)  
- Elevation (converted to feet for display)
- Timestamp (if available)

### Speed Calculations

**Horizontal Speed**: Calculated using the Haversine formula to compute the great circle distance between consecutive GPS points, then dividing by the time difference. Displayed in **knots** (nautical miles per hour) - the aviation standard.

**Vertical Speed**: Calculated from elevation changes between consecutive points divided by time difference. Displayed in **ft/min** (feet per minute) - the standard for climb/descent rates.

### Distance and Area Measurements

**Flight Area**: Displayed in **nautical miles (NM)** for East-West and North-South extents.

**Horizontal Distances**: When time data is unavailable, distances between points are shown in nautical miles.

### 3D Visualization

The interactive 3D plot shows:
- Flight path as a line with markers
- Color-coded elevation in feet (using Viridis colorscale)
- Interactive controls to rotate, zoom, and pan
- Consistent meter-based coordinate system for spatial axes
- Optional elevation scaling to emphasize vertical variations
- Hover information showing actual coordinates and elevations in feet

### Multiple Chart Display

The visualization now includes three charts in a single view:
- **3D Flight Trajectory** (top): Spatial view of the flight path
- **Elevation vs Time** (middle): Shows altitude changes throughout the flight in feet
- **Ground Speed vs Time** (bottom): Displays speed variations in knots over time

## Sample Output

When running with `--stats`, you'll see output like:
```
Parsing GPX file: sample_flight.gpx
Found 21 track points

=== Flight Statistics ===
Total points: 21
Latitude range: 37.774900° - 37.784500°
Longitude range: -122.419400° - -122.409500°
Elevation range: 32.8ft - 1312.3ft
Elevation range (meters): 10.0m - 400.0m
Flight area: 0.5NM × 0.6NM (East-West × North-South)
Flight area (meters): 870m × 1067m (East-West × North-South)
Horizontal speed (avg): 4.5 knots (2.3 m/s)
Horizontal speed (max): 4.6 knots (2.4 m/s)
Vertical speed (avg): -0 ft/min (-0.00 m/s)
Max climb rate: 328 ft/min (1.67 m/s)
Max descent rate: -328 ft/min (-1.67 m/s)
Flight duration: 10.0 minutes (0.17 hours)
```

## Aviation Units

The script uses standard aviation units for all measurements:
- **Speeds**: knots (nautical miles per hour)
- **Vertical speeds**: ft/min (feet per minute) 
- **Distances**: nautical miles (NM)
- **Elevations**: feet (ft)
- **Areas**: square nautical miles

Metric equivalents are also shown in parentheses for reference.

## Use as a Library

You can also use the script as a Python library:

```python
from flight_tracker_analyzer import GPXParser, FlightTrack

# Parse a GPX file
track = GPXParser.parse_file('sample_flight.gpx')

# Get trajectory data
lats, lons, elevations = track.get_trajectory_data()

# Calculate speeds (returned in m/s, convert using provided functions)
horizontal_speeds = track.get_horizontal_speeds()  # m/s
vertical_speeds = track.get_vertical_speeds()      # m/s

# Convert to aviation units
from flight_tracker_analyzer import mps_to_knots, mps_to_fpm, meters_to_feet

for i, speed in enumerate(horizontal_speeds):
    if speed is not None:
        speed_knots = mps_to_knots(speed)
        print(f"Point {i}: {speed_knots:.1f} knots")

# Access individual points
for point in track.points:
    elevation_ft = meters_to_feet(point.ele)
    print(f"Lat: {point.lat}, Lon: {point.lon}, Elevation: {elevation_ft:.1f} ft")
```

### Advanced Example

The `advanced_example.py` script demonstrates more sophisticated analysis:

```bash
python advanced_example.py sample_flight.gpx
```

This provides detailed statistics including:
- Trajectory information with start/end positions
- Elevation analysis (min, max, average, total gain)
- Speed statistics (average, median, max, min, standard deviation)
- Flight phase analysis (climbing, cruising, descending percentages)
- Time and distance calculations

## Requirements

- Python 3.6+
- plotly >= 5.0.0 (for 3D visualization)
- requests >= 2.25.0 (for map integration)
- Pillow >= 8.0.0 (for image processing, optional)

## License

MIT License
