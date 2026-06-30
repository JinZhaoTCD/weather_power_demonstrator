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
- **Text overlay animation** – Transparent-background PNG text sequences that can be independently positioned and scaled in TouchDesigner, fully synchronized with grid animation timeline

### Physical model implementation (See branch "physical-irl-sandbox")

- **Physical sandbox model of irl grid** - 3D printed grid components (Wind Farm, Coal/Gas Plant, Solar PV Farm, Transformer, Transmission Tower) scaled to map size, with accurate position on the map
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

- **Source**: All-Island Ten Year Transmission Forecast Statement
- **Access**: [Study files](https://cms.eirgrid.ie/all-island-ten-year-transmission-forecast-statement)
- **Author**: Xi Wang
- **File**: `All Island transmission grid parameter.xlsx`
- **Sheets**: `Bus` (node locations), `Branch` (transmission lines), `Generator` (power plants)

### 4.Coordinate Reference System (CRS)

All geographic data unified to **EPSG:2157 (Irish Transverse Mercator)**:

- Bus: WGS84 → ITM via `pyproj.Transformer`
- Boundary: GeoJSON (EPSG:4326) → EPSG:2157 via `geopandas-transformer`
- CLC: native EPSG:2157

## Dependencies & Licenses

This project uses two types of third-party libraries:

### 1. SEEIT Proprietary Library

- **Copyright**: © 1996-2026 SEEIT. All Rights Reserved.
- **Trademark**: SEEIT is a registered trademark.
- **License**: This is proprietary software. Unauthorized reproduction, in whole or in part, is prohibited under French law.
- **Disclaimer**: SEEIT assumes no responsibility for any damages arising from the use of the device or software.
- **Obtaining the library**: You must obtain this library directly from SEEIT through official channels. **This repository contains NO SEEIT proprietary code.**

### 2. Adafruit NeoPixel Library

- **Source**: [Adafruit NeoPixel](https://github.com/adafruit/Adafruit_NeoPixel)
- **Copyright**: Adafruit Industries
- **License**: GNU Lesser General Public License v3.0 (LGPL-3.0)
- **Disclaimer**: This library is distributed WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the LGPL-3.0 license for details.
- **Compliance**: This project uses the library as provided. Any modifications to the library itself will be made available under LGPL-3.0.

## Visual Features

- Dynamic storm intensity (ramps up, peaks, fades out)
- Risk-based line coloring: normal → low → medium → high → tripped → recovering
- Flow particles on operational lines
- Generator icons (⚡) at bus locations
- Backup line with glow and particle flow when activated

## Branches

- `animation` – Grid animation code
- `hardware` – Physical-irl-sandbox

## Credits

- **Dr. Jin Zhao** - Project administration, conceptualization, funding acquisition.
- **Dr. HanJiang Dong** – Project management, supervision, initial animation framework, and adding CLC land cover background.
- **Dr. Yang Shen** - Project supervision, sandbox consturction, material purchasing, and 3D printing of grid models.  
- **Xi Wang** – Constructed and curated the 67-bus All-Island transmission grid model at 220 kV and above, used as the core network dataset for the demonstrator, including bus, branch, generator, and geospatial coordinate information; processed and validated the network topology; and mapped grid components to Irish geographic coordinates.
- **Leshan Hu**  
  - **Software & animation**: Transparent PNG sequence output, backup line reconfiguration logic, performance optimizations (merged 50k+ → 5 polygons for CLC), geospatial preprocessing and CRS harmonisation (EPSG:4326 → EPSG:2157), TouchDesigner compositing, projector alignment, text overlay animation (transparent PNG text sequences for status labels and phase descriptions, independently movable/scalable in TouchDesigner and synchronized with grid timeline).
  - **Physical hardware & firmware**:
    - Dual SPI LED output - Two WS281x/NeoPixel LED strips are driven on separate SPI buses to avoid stutter when both strips animate at the same time.
    - Explicit SPI selection - The Python LED controller uses a small spidev wrapper so the main and backup strips are assigned directly to LinuxSPI(0, 0) and LinuxSPI(3, 0) instead of relying on board.SPI() auto-detection.
    - USB relay control (`relay_command.cpp`) – custom C++ program for state switching; resolved driver incompatibility by sourcing legacy serial USB driver.
    - Cross-process communication – `subprocess.Popen` architecture enabling non-blocking coordination between Python animation and C++ relay commands.
    - Event-driven state machine – 12-phase fault injection timeline (main trip → backup activation → recovery) with precise timing control.
    - Electrical assembly – hand-soldered load LED matrix, wire jumping at WS281x/NeoPixel LED strips turning points , and wiring harness using strip board for safety consideration.
  - **Environment & debugging**:
    - Resolved incompatible vendor-provided relay driver; sourced and validated legacy USB-to-serial driver.
    - Library migration – identified, tested, and ported between multiple NeoPixel libraries for RPi 5 compatibility.
    - Python runtime - Python 3.11 virtual environment (demo311) with GPIO/SPI dependencies including adafruit-blinka, adafruit-circuitpython-neopixel-spi, spidev, lgpio, and RPi.GPIO.
