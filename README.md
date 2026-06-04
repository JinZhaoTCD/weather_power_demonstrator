# Ireland Power Grid Reconfiguration Animation

Visualizes a storm moving across the Irish power grid, showing:

- **Real grid infrastructure** – 67 buses and transmission lines (220kV and above) from actual Irish grid data, with precise GPS coordinates mapped to EPSG:2157
- **Storm impact simulation** – Lines trip under extreme weather, with dynamic danger rings based on distance to storm center
- **Automatic grid reconfiguration** – When target line fails, backup line automatically activates, then deactivates after restoration
- **Recovery animation** – Tripped lines gradually recover after storm passes
- **High-precision basemap** – Ireland boundary from GeoJSON + Corine Land Cover (CLC) data at 5-class simplified color scheme

The output is a transparent-background PNG sequence ready for real-time compositing in TouchDesigner with terrain overlays.

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
- Boundary: GeoJSON (EPSG:4326) → EPSG:2157 via `geopandas`
- CLC: native EPSG:2157

## Visual Features

- Dynamic storm intensity (ramps up, peaks, fades out)
- Risk-based line coloring: normal → low → medium → high → tripped → recovering
- Flow particles on operational lines
- Generator icons (⚡) at bus locations
- Backup line with glow and particle flow when activated

## Credits

 **Dr. Dong** – Project supervision and initial animation framework, added CLC land cover background
- **Xi Wang** – Compiled grid data from Excel and mapped bus coordinates to the map.
- **Leshan Hu** –  transparent PNG sequence output, backup line reconfiguration logic, performance optimizations (merged 50k+ polygons to 5 for CLC background), reference system transformation(from EPSG 4326 to EPSG 2157), TouchDesigner compositing, and projector alignment to the physical terrain model.