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
- `--stats`: Display flight statistics including speeds and elevation data

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
- Axes for longitude, latitude, and elevation

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

## Requirements

- Python 3.6+
- plotly >= 5.0.0 (for 3D visualization)

## License

MIT License
