# Ireland's Power Grid Resilience Under Extreme Weather - Demo


## Background

On 28 April 2025, a blackout plunged most of Spain and Portugal into darkness, affecting over 40 million people. At the moment of collapse, more than 70% of generation came from solar and wind—the highest renewable penetration ever recorded during a major grid failure.

Ireland is walking a similar path: wind already supplies over 35% of its electricity, with a target of 80% renewable by 2030. But Ireland faces an additional threat—frequent Atlantic winter storms that can physically damage transmission lines.

**So how does a high-renewable grid behave when a storm hits? Which lines trip first? How does the system reconfigure itself?**

This project visualizes these dynamics through a **virtual animation** and a **physical sandbox model**, offering a tangible window into how grid resilience might be affected by extreme weather.

## System Overview

Visualizes a storm moving across the Irish power grid, showing:

### Virtual animation projection 
- **Real grid infrastructure** – 67 buses and transmission lines (220kV and above) from actual Irish grid data, with precise GPS coordinates mapped to EPSG:2157
- **Storm impact simulation** – Lines trip under extreme weather, with dynamic danger rings based on distance to storm center
- **Automatic grid reconfiguration** – When target line fails, backup line automatically activates, then deactivates after restoration
- **Recovery animation** – Tripped lines gradually recover after storm passes
- **High-precision basemap** – Ireland boundary from GeoJSON + Corine Land Cover (CLC) data at 5-class simplified color scheme
- **Power flow visualization** - using partial effect on grid branches to represent the load
The output is a transparent-background PNG sequence ready for real-time compositing in TouchDesigner with terrain overlays.

### Physical model implementation
(See branch "physical-irl-sandbox" )
- **Phycial sandbox model of irl grid** - 3D printed grid components (Wind Farm, Coal/Gas Plant, Solar PV Farm, Transformer, Transmission Tower) scaled to map size, with accurate position on the map
- **Detailed power grid level structure** - The sand box model further detailed the animation (220kV and above), adding 110kV subnet 
- **Dynamic power flow representation** - Raspberry Pi 5 and programmable relays mapped the state and reconfiguration of critical branches from the digital animation to the physical sandbox model with flowing visual effect
- **Interactive design**  - Live-demonstrable scaled wind turbine models capable of real-time generation



## Data Sources

### 1. Ireland Boundary (GeoJSON)
- **Source**: OpenStreetMap (OSM) / Geo2Day Project
- **Access**: [geo2day.com/europe/ireland.html](https://geo2day.com/europe/ireland.html)
- **File**: `ireland.geojson`
- **Coordinate System**: WGS84 (EPSG:4326) → converted to ITM (EPSG:2157) in code

### 2. Corine Land Cover 2018 (Ireland)
- **Source**: Environmental Protection Agency, Ireland
- **Access**: [data.gov.ie/dataset/corine-landcover-2018](https://data.gov.ie/dataset/corine-landcover-2018)
- **File**: `CLC18_IE_ITM.shp`
- **License**: [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Coordinate System**: ITM (EPSG:2157)

### 3. Irish Transmission Grid Data
- **Source**: Provided by Xi Wang
- **File**: `All Island transmission grid parameter.xlsx`
- **Sheets**: `Bus` (node locations), `Branch` (transmission lines), `Generator` (power plants)

## Coordinate Reference System (CRS)

All geographic data unified to **EPSG:2157 (Irish Transverse Mercator)**:
- Bus: WGS84 → ITM via `pyproj.Transformer`
- Boundary: GeoJSON (EPSG:4326) → EPSG:2157 via `geopandas-transformer
- CLC: native EPSG:2157

## Visual Features

- Dynamic storm intensity (ramps up, peaks, fades out)
- Risk-based line coloring: normal → low → medium → high → tripped → recovering
- Flow particles on operational lines
- Generator icons (⚡) at bus locations
- Backup line with glow and particle flow when activated

## Branches

- `animation` – Grid animation code (this branch)
- `hardware` – Hardware firmware (with Dr. Shen)

## Credits
- **Dr. Dong** – Project supervision, and initial animation framework, added CLC land cover background
- **Dr. Shen** - Supervision, sandbox, material purchasing, and 3D printing of grid models. 
- **Xi Wang** – Compiled grid data from Excel and mapped bus coordinates to the map.
- **Leshan Hu** –  transparent PNG sequence output, backup line reconfiguration logic, performance optimizations (merged 50k+ polygons to 5 for CLC background), reference system transformation(from EPSG 4326 to EPSG 2157), TouchDesigner compositing, and projector alignment to the physical terrain model,