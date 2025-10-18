# flight-tracker-analyzer
GPX processor to analyze Garmin Flight Activities data

## Overview

This Python script processes GPX files from Garmin Flight Activities to extract and analyze flight data. It provides:
- 3D trajectory visualization
- Horizontal speed calculation based on latitude/longitude variations
- Vertical speed calculation based on elevation changes
- Comprehensive flight statistics

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
- `--stats`: Display flight statistics including speeds and elevation data

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
- Elevation (meters)
- Timestamp (if available)

### Speed Calculations

**Horizontal Speed**: Calculated using the Haversine formula to compute the great circle distance between consecutive GPS points, then dividing by the time difference.

**Vertical Speed**: Calculated from elevation changes between consecutive points divided by time difference.

### 3D Visualization

The interactive 3D plot shows:
- Flight path as a line with markers
- Color-coded elevation (using Viridis colorscale)
- Interactive controls to rotate, zoom, and pan
- Consistent meter-based coordinate system for all three axes
- Optional elevation scaling to emphasize vertical variations
- Hover information showing actual coordinates and elevations

## Sample Output

When running with `--stats`, you'll see output like:
```
Parsing GPX file: sample_flight.gpx
Found 21 track points

=== Flight Statistics ===
Total points: 21
Elevation range: 10.0m - 400.0m
Horizontal speed (avg): 18.5 m/s (66.6 km/h)
Horizontal speed (max): 19.2 m/s (69.1 km/h)
Vertical speed (avg): 0.00 m/s
Max climb rate: 1.67 m/s (100.0 m/min)
Max descent rate: -1.67 m/s (-100.0 m/min)
Flight duration: 10.0 minutes (0.17 hours)
```

## Use as a Library

You can also use the script as a Python library:

```python
from flight_tracker_analyzer import GPXParser, FlightTrack

# Parse a GPX file
track = GPXParser.parse_file('sample_flight.gpx')

# Get trajectory data
lats, lons, elevations = track.get_trajectory_data()

# Calculate speeds
horizontal_speeds = track.get_horizontal_speeds()
vertical_speeds = track.get_vertical_speeds()

# Access individual points
for point in track.points:
    print(f"Lat: {point.lat}, Lon: {point.lon}, Elevation: {point.ele}")
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
