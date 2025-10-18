# Flight Trajectory Mapping Guide

## Overview

The Flight Tracker Analyzer now includes mapping integration to provide geographical context for your flight trajectories. This feature helps you understand the relationship between your flight path and the underlying terrain, cities, and landmarks.

## Quick Start

### Basic Map Integration
```bash
python flight_tracker_analyzer.py your_flight.gpx --plot --include-map --elevation-scale 8.0
```

This command will:
1. Generate a 3D plot with a ground reference plane
2. Scale elevation by 8x for better visibility
3. Display flight area coordinates
4. Provide direct links to external mapping services

## Features

### ✅ Ground Reference Plane
- Adds a subtle grid pattern below the flight path
- Helps visualize height above ground
- Semi-transparent to not interfere with trajectory

### ✅ Flight Area Coordinates
- Displays precise lat/lon bounds of your flight
- Shows center coordinates for quick map navigation
- Provides coordinate information for external tools

### ✅ External Mapping Links
- **Google Maps**: Direct link to flight area center
- **OpenStreetMap**: Open-source mapping alternative
- **Google Earth Web**: 3D satellite view of flight area

## External Mapping Workflows

### 1. Google Earth Integration
**Best for: Satellite imagery and 3D terrain context**

1. Copy the generated Google Earth Web link
2. Open in your browser
3. Upload your GPX file using "Import KML file" button
4. View your flight path overlaid on satellite imagery

```bash
# Example output link:
https://earth.google.com/web/@37.779700,-122.414450,1000a,1000d,35y,0h,0t,0r
```

### 2. QGIS Professional Analysis
**Best for: Advanced GIS analysis and multiple data layers**

1. Install QGIS (free from qgis.org)
2. Create new project
3. Add base map layer (OpenStreetMap, Google Satellite, etc.)
4. Import GPX file as GPS track layer
5. Use flight area coordinates for proper zoom/extent

### 3. GPS Visualizer
**Best for: Quick online visualization**

1. Visit GPS Visualizer website
2. Upload your GPX file
3. Choose map background (Google, OpenStreetMap, etc.)
4. Use provided coordinates to center the map

### 4. Garmin Connect
**Best for: Garmin device users**

1. Upload GPX to Garmin Connect
2. View with satellite, terrain, or street map overlays
3. Analyze flight metrics with geographical context

## Sample Output

When you run with `--include-map`, you'll see:

```
=== External Mapping Options ===
Google Maps (center): https://www.google.com/maps/@37.779700,-122.414450,12z
OpenStreetMap (center): https://www.openstreetmap.org/#map=12/37.779700/-122.414450
Google Earth Web: https://earth.google.com/web/@37.779700,-122.414450,1000a,1000d,35y,0h,0t,0r

Flight area coordinates:
  Center: 37.779700°, -122.414450°
  Bounds: (37.774900°, -122.419400°) to (37.784500°, -122.409500°)

To view your flight with map context:
1. Copy the GPX file to Google Earth Pro or Google Earth Web
2. Use GPS visualization tools like:
   - QGIS (free GIS software)
   - GPS Visualizer (online tool)
   - Garmin Connect (if from Garmin device)
```

## Advanced Use Cases

### Flight Planning Analysis
- Overlay flight paths on terrain maps
- Identify landmarks and navigation points
- Analyze flight paths relative to airports, restricted areas

### Safety Analysis
- Compare actual vs planned routes
- Identify terrain avoidance patterns
- Analyze approach and departure patterns

### Training and Education
- Overlay multiple training flights
- Compare student vs instructor paths
- Analyze traffic patterns at training airports

## Technical Implementation

The mapping integration includes:
- **Ground reference plane**: A subtle 3D grid below the flight path
- **Coordinate transformation**: Automatic conversion between degrees and meters
- **Bounds calculation**: Smart determination of flight area with appropriate padding
- **Link generation**: Automatic creation of properly formatted mapping service URLs

## Troubleshooting

### No Internet Connection
- The basic 3D plot will still work
- Ground reference plane will be displayed
- Coordinate information will be shown for offline use

### Map Services Unavailable
- Fallback to coordinate display
- Alternative mapping service suggestions provided
- GPX file can still be used in offline tools

## Future Enhancements

Potential future features:
- Direct integration with mapping APIs
- Embedded map tiles in HTML output
- Terrain elevation profiles
- Weather overlay integration
- Real-time mapping during live flights

## Examples by Region

### Sample Flight (San Francisco Bay Area)
```bash
python flight_tracker_analyzer.py sample_flight.gpx --plot --include-map --elevation-scale 10.0
```
- Center: 37.779700°, -122.414450°
- Great for viewing over San Francisco Bay
- Excellent landmarks for reference

### Real Flight (Brazilian Airspace)
```bash
python flight_tracker_analyzer.py activity_17627335103.gpx --plot --include-map --elevation-scale 8.0
```
- Center: -23.173030°, -45.798429°
- Large flight area suitable for terrain analysis
- Good example of long-distance flight patterns

This mapping integration transforms your flight data from abstract coordinates into meaningful geographical context, making analysis and presentation much more intuitive and informative.