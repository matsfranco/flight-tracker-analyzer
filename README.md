# Flight Tracker Analyzer
GPX processor for analyzing flight data with interactive 3D visualization

## Overview

This Python script processes GPX files to extract and analyze flight data with a focus on interactive visualization. Key features:

- **Interactive 3D trajectory visualization** with dynamic time-based segmentation
- **Synchronized multi-chart display** with elevation, vertical speed, and ground speed over time
- **Time range navigation** with range slider and synchronized zooming/panning
- **Aviation standard units** - speeds in knots, vertical rates in ft/min, distances in nautical miles
- **Elevation scaling** for better visualization of altitude changes
- **Dynamic 3D markers** that move with time range selections
- **Comprehensive flight statistics** using aviation standard units

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
- `--plot`: Generate an interactive 3D trajectory plot with synchronized charts
- `--output`: Specify output HTML file for the plot (default: flight_trajectory_3d.html)
- `--elevation-scale`: Scale factor for elevation visualization (default: 1.0). Use values > 1.0 to exaggerate elevation changes (e.g., 5.0 for 5x scaling, 10.0 for 10x scaling)
- `--stats`: Display comprehensive flight statistics

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

## 🚀 Core Innovation

This project implements **time-aware 3D trajectory visualization** - a breakthrough feature that adds time as a 4th dimension to 3D flight paths. Unlike static 3D visualizations, this system dynamically segments the 3D trajectory based on time range selections, with start and end markers that move in real-time to reflect the selected time period.

**Technical Achievement:**
- Time data embedded as a 4th dimension in 3D traces using `customdata`
- JavaScript event system that maps time ranges to 3D trajectory indices  
- Dynamic trace updates using Plotly.restyle() for seamless marker movement
- Synchronized multi-chart system with range slider control

## Key Features

### Interactive 3D Visualization

The centerpiece is an interactive HTML visualization with four synchronized charts:

1. **3D Flight Trajectory** (top): Spatial view with dynamic time-based segmentation
   - Full trajectory shown in light gray for context
   - Active segment highlighted with color-coded elevation
   - Dynamic start (green diamond) and end (red diamond) markers
   - Interactive rotation, zoom, and pan controls
   - Elevation scaling to emphasize altitude variations

2. **Elevation vs Time**: Altitude changes throughout the flight in feet
3. **Vertical Speed vs Time**: Climb/descent rates in ft/min with noise filtering  
4. **Ground Speed vs Time**: Speed variations in knots with noise filtering

### Revolutionary Time Navigation

- **Range Slider**: Interactive time selection at the bottom of the visualization
- **Dynamic 3D Segmentation**: The 3D chart updates in real-time to show only the selected time period
- **Moving Markers**: Start and end markers dynamically move to reflect the selected time range
- **Synchronized Charts**: All charts zoom and pan together automatically
- **Seamless Integration**: Complete flight analysis with time-aware 3D trajectory

### Advanced Signal Processing

- **Smoothed data** (thick lines): Moving average filtered signals showing trends
- **Raw data** (thin dotted lines): Original unfiltered data for reference  
- **Adaptive filtering**: Window size automatically adjusts based on data density
- **Noise reduction**: Eliminates GPS measurement errors while preserving flight characteristics

## Sample Output

When running with `--plot --stats`, you'll see:

**Console Output:**
```
Parsing GPX file: sample_flight.gpx
Found 21 track points
3D trajectory plot saved to flight_trajectory_3d.html
Elevation scaled by factor: 5.0x

=== Flight Statistics ===
Total points: 21
Flight duration: 10.0 minutes (0.17 hours)
Elevation range: 32.8ft - 1312.3ft
Flight area: 0.5NM × 0.6NM (East-West × North-South)
Horizontal speed (avg): 4.5 knots (max: 4.6 knots)
Vertical rates: Max climb: 328 ft/min, Max descent: -328 ft/min
```

**Interactive Visualization:**
- Opens `flight_trajectory_3d.html` in your browser
- Four synchronized charts with time navigation
- 3D trajectory with dynamic segmentation and moving markers
- Range slider for interactive time period selection

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

## Interactive Usage Guide

1. **Generate the visualization:**
   ```bash
   python flight_tracker_analyzer.py your_flight.gpx --plot --elevation-scale 5.0
   ```

2. **Open the HTML file** in your web browser

3. **Use the time navigation:**
   - Drag the range slider handles at the bottom to select time periods
   - Watch the 3D trajectory update to show only the selected segment
   - See the start and end markers move to new positions
   - All charts automatically synchronize to the same time range

4. **Explore the data:**
   - Hover over any point for detailed information
   - Rotate and zoom the 3D view for different perspectives
   - Use the elevation scaling to better see altitude variations

## Project Structure

```
flight-tracker-analyzer/
├── flight_tracker_analyzer.py     # Main analysis script with interactive visualization
├── test_flight_tracker_analyzer.py # Unit tests
├── requirements.txt               # Python dependencies
├── sample_flight.gpx             # Sample GPX file for testing
├── activity_17627335103.gpx      # Larger sample flight (71 minutes)
├── test_no_time.gpx              # Test file without timestamps
└── README.md                     # This file
```

## Development and Testing

Run the unit tests:
```bash
python -m pytest test_flight_tracker_analyzer.py -v
```

Test with different GPX files:
```bash
# Short flight (10 minutes, 21 points)
python flight_tracker_analyzer.py sample_flight.gpx --plot --stats

# Longer flight (71 minutes, 2986 points)  
python flight_tracker_analyzer.py activity_17627335103.gpx --plot --stats --elevation-scale 3
```

## Requirements

- Python 3.6+
- plotly >= 5.0.0 (for interactive 3D visualization)

Install dependencies:
```bash
pip install -r requirements.txt
```

## License

MIT License
