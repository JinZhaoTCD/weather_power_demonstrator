
"""
Ireland Power Grid Reconfiguration Animation

Animate the situation where a storm moving across Irish transmission grid (220kV+). Lines trip near storm,
recover after, and one target line gets replaced by a backup.

Output: transparent PNG sequence for TouchDesigner compositing.
"""


import os
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from matplotlib.patches import Circle
from pyproj import Transformer

# File paths (update these to match your local setup)
GEOJSON_PATH = "ireland.geojson"
EXCEL_PATH = "All Island transmission grid parameter.xlsx"
OUTPUT_FOLDER = r"D:\IRL_terrain\Image\testout"
CLC_FILE = "CLC18_IE_ITM.shp"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Animation settings
N_FRAMES = 300 # Total frames (300 frames = 37.5 seconds at 8 fps)
DPI = 150
fig_height = 9 # Set the height of final output image(inches), width is calculated with the w/h ratio of the geojason file

# Storm danger zones (meters from storm center)
R_HIGH = 45000
R_MED = 70000
R_LOW = 100000

# Timing (frames)
RECOVERY_DURATION = 20 # How long a line takes to recover
NEW_LINE_FADE_IN = 40 # How long backup line takes to fade in

# Which line to replace with backup
TARGET_EDGE_ID = 2
other_bus_backup = 2039

# Background
BG = "none"

# Line states
LINE_NORMAL = "#5A6E7C"
LINE_LOW = "#FFD966"
LINE_MED = "#FF9F4A"
LINE_HIGH = "#FF4D4F"
LINE_TRIPPED = "#F0F4F8"
LINE_RECOVERING = "#3DDB97"
LINE_RECOVERED = "#4CC9F0"

# Backup line
LINE_NEW_START = "#FF3366"

# Partials representing powerflow
FLOW_NORMAL = "#4CC9F0"
FLOW_RECOVER = "#72EFDD"

# Buses and generators
BUS_NORMAL = "#8A9BB0"
GEN_ICON_COLOR = "#FFD966"

# Ireland border (from .geojason file)
BORDER_COLOR = "#2A2A2A"
BORDER_WIDTH = 1.2

# Storm circle color
HIGH_RISK = "#FF4444"
MEDIUM_RISK = "#FF8844"
LOW_RISK = "#4EA8DE"

# land cover colors (Corine classes)
SIMPLIFIED_COLORS = {
    1: "#7E746E",  # artificial
    2: "#7F8F63",  # agriculture
    3: "#5E7D57",  # forest
    4: "#6E8B75",  # wetlands
    5: "#4E6F7A",  # water
}

# clc data buffer to boost up rendering
clc_processed = None



# DATA LOADING

print("Reading data...")
ireland_map = gpd.read_file(GEOJSON_PATH)
bus_df = pd.read_excel(EXCEL_PATH, sheet_name="Bus")
branch_df = pd.read_excel(EXCEL_PATH, sheet_name="Branch")
gen_df = pd.read_excel(EXCEL_PATH, sheet_name="Generator")
bus_df = bus_df.dropna(subset=["bus_id", "Lontitude", "Latitude"]).copy()
bus_df["bus_id"] = pd.to_numeric(bus_df["bus_id"], errors="coerce").astype(int)
bus_df["Lontitude"] = pd.to_numeric(bus_df["Lontitude"], errors="coerce")
bus_df["Latitude"] = pd.to_numeric(bus_df["Latitude"], errors="coerce")

branch_df["fbus"] = pd.to_numeric(branch_df["fbus"], errors="coerce").astype(int)
branch_df["tbus"] = pd.to_numeric(branch_df["tbus"], errors="coerce").astype(int)

gen_df["bus"] = pd.to_numeric(gen_df["bus"], errors="coerce").astype(int)
gen_bus_set = set(gen_df["bus"].tolist())



# Convert coordinates from WGS84 to Irish Transverse Mercator (EPSG:2157) to prevent deformation

print("Converting coordinates...")
if ireland_map.crs is None:
    ireland_map = ireland_map.set_crs("EPSG:2157", allow_override=True)
else:
    ireland_map = ireland_map.to_crs("EPSG:2157")

transformer = Transformer.from_crs("EPSG:4326", "EPSG:2157", always_xy=True)
bus_coords = {}
for _, row in bus_df.iterrows():
    x, y = transformer.transform(float(row["Lontitude"]), float(row["Latitude"]))
    bus_coords[row["bus_id"]] = (x, y)

map_bounds = ireland_map.total_bounds
map_minx, map_miny, map_maxx, map_maxy = map_bounds
margin_x = (map_maxx - map_minx) * 0.05
margin_y = (map_maxy - map_miny) * 0.05

xlim = (map_minx - margin_x, map_maxx + margin_x)
ylim = (map_miny - margin_y, map_maxy + margin_y)
map_aspect = (map_maxx - map_minx) / (map_maxy - map_miny)
fig_width = fig_height * map_aspect


# Grid construction

edges = []
for _, row in branch_df.iterrows():
    fbus, tbus = row["fbus"], row["tbus"]
    if fbus in bus_coords and tbus in bus_coords:
        x1, y1 = bus_coords[fbus]
        x2, y2 = bus_coords[tbus]
        edges.append({
            "id": len(edges),
            "fbus": fbus, "tbus": tbus,
            "x1": x1, "y1": y1,
            "x2": x2, "y2": y2,
            "mid_x": (x1 + x2) / 2,
            "mid_y": (y1 + y2) / 2,
        })
edges_df = pd.DataFrame(edges)
print(f"Total lines: {len(edges_df)}")

if TARGET_EDGE_ID not in edges_df['id'].values:
    TARGET_EDGE_ID = edges_df.iloc[0]['id']
    print(f"New target line: {TARGET_EDGE_ID}")


# Processing CLC data, merge polygon with the same color together

print("Loading and preprocessing CLC data...")
clc = gpd.read_file(CLC_FILE)
clc = clc.to_crs("EPSG:2157")
clc_clip = gpd.clip(clc, ireland_map)

code_col = None
for col in ["CODE_18", "CODE18", "code_18", "code18", "GRIDCODE", "gridcode"]:
    if col in clc_clip.columns:
        code_col = col
        break
if code_col is None:
    code_col = clc_clip.columns[0]


clc_clip[code_col] = clc_clip[code_col].astype(str)
clc_clip["clc_l1"] = clc_clip[code_col].str[0].astype(int)
clc_clip = clc_clip[clc_clip["clc_l1"].isin(SIMPLIFIED_COLORS.keys())].copy()
clc_clip["plot_color"] = clc_clip["clc_l1"].map(SIMPLIFIED_COLORS)

clc_processed = clc_clip.dissolve(by="clc_l1")
print(f"CLC preprocessed. Polygons: {len(clc_processed)} (merged from {len(clc_clip)})")


# Loading storm trace

center_x = (map_minx + map_maxx) / 2
center_y = (map_miny + map_maxy) / 2
storm_x = np.linspace(xlim[0], xlim[1], N_FRAMES)
storm_y = center_y + (map_maxy - map_miny) * 0.2 * np.sin(np.linspace(0, 2 * np.pi, N_FRAMES))
storm_track = list(zip(storm_x, storm_y))

def clip_alpha(a):
    return max(0.0, min(1.0, float(a)))


def pulse(frame, speed=0.28):
    return 0.9 + 0.2 * np.sin(frame * speed)


line_states = {}
"""initiating variables for simulation"""
for _, row in edges_df.iterrows():
    line_states[row["id"]] = {
        "phase": np.random.rand(),
        "base_speed": 0.02,
        "damage": 0.0,
        "recover": 0,
        "status": "normal",
        "recovery_progress": 0,
        "recovery_start": None,
    }


# Creat backup line for reconfiguration

backup_line = {
    "fbus": None, "tbus": None, "x1": 0, "y1": 0, "x2": 0, "y2": 0,
    "activated": False, "phase": 0, "deactivating": False, "deactivate_start_frame": 0,
}
target_temp = edges_df.loc[edges_df["id"] == TARGET_EDGE_ID].iloc[0]
fbus_backup = target_temp["fbus"]

if other_bus_backup in bus_coords:
    backup_line.update({
        "fbus": fbus_backup, "tbus": other_bus_backup,
        "x1": bus_coords[fbus_backup][0], "y1": bus_coords[fbus_backup][1],
        "x2": bus_coords[other_bus_backup][0], "y2": bus_coords[other_bus_backup][1],
    })
    print(f"Backup line: {fbus_backup} -> {other_bus_backup}")

reconfiguration_triggered = False
"""HELPER FUNCTIONS"""
def euclid_dist(x1, y1, x2, y2):
    return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def interpolate_point(x1, y1, x2, y2, t):
    return x1 + t * (x2 - x1), y1 + t * (y2 - y1)

# Color mapping & line initiating

def risk_from_dist(d, rh, rm, rl):
    if d < rh: return "high"
    if d < rm: return "medium"
    if d < rl: return "low"
    return "normal"


def get_line_color_by_risk(risk, status):
    if status == "tripped": return LINE_TRIPPED
    if status == "recovering": return LINE_RECOVERING
    if status == "disturbed": return LINE_HIGH if risk == "high" else LINE_MED
    if risk == "normal": return LINE_NORMAL
    if risk == "low": return LINE_LOW
    if risk == "medium": return LINE_MED
    return LINE_HIGH


def get_flow_color_by_risk(risk, status):
    if status == "tripped": return None
    if status == "recovering": return FLOW_RECOVER
    if status == "disturbed": return FLOW_RECOVER
    if risk == "normal": return FLOW_NORMAL
    return FLOW_RECOVER


def get_recovery_color(progress):
    r = min(1.0, progress * 3)
    g = min(1.0, progress * 2)
    b = 1.0 - progress
    return (r, g, b), 2.5 - progress


def get_line_width_by_risk(risk, status):
    if status == "tripped": return 1.5
    if status == "recovering": return 2.0
    if risk == "high": return 3.0
    if risk == "medium": return 2.5
    return 1.5


plt.style.use("dark_background")

def draw_clc_background(ax):
    clc_processed.plot(
        ax=ax,
        color=clc_processed["plot_color"],
        linewidth=0,
        edgecolor="none",
        zorder=1
    )
    ireland_map.boundary.plot(
        ax=ax,
        color=BORDER_COLOR,
        linewidth=BORDER_WIDTH,
        zorder=2
    )
"""MAIN ANIMATION(CALLED ONCE PER FRAME)"""



def update(frame):
    global reconfiguration_triggered

    ax.clear()
    ax.set_facecolor(BG)
    ax.patch.set_alpha(0)
    fig.patch.set_alpha(0)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])

    draw_clc_background(ax)

    cx, cy = storm_track[frame]
    progress = frame / N_FRAMES

    if progress < 0.35:
        intensity = 0.5 + progress / 0.35
    elif progress < 0.5:
        intensity = 1.5
    else:
        intensity = max(0.3, 1.5 - (progress - 0.5) / 0.5 * 1.2)

    dyn_r_high = R_HIGH * intensity
    dyn_r_med = R_MED * intensity
    dyn_r_low = R_LOW * intensity

    if frame > 0:
        hx, hy = zip(*storm_track[:frame + 1])
        ax.plot(hx, hy, "--", color="#4EA8DE", lw=1.5, alpha=0.5, zorder=1)


    ax.scatter(cx, cy, s=220, marker="X", color="#FF4444",
               linewidths=2, edgecolor="white", zorder=10,
               path_effects=[path_effects.withStroke(linewidth=1, foreground='black')])


    p = pulse(frame)
    rings = [
        (dyn_r_low * p, LOW_RISK, 0.2, 0.8),
        (dyn_r_med * p, MEDIUM_RISK, 0.3, 1.0),
        (dyn_r_high * p, HIGH_RISK, 0.4, 1.2),
    ]

    for radius, color, alpha, linewidth in rings:
        ax.add_patch(Circle((cx, cy), radius, facecolor="none",
                            edgecolor=color, linewidth=linewidth, alpha=alpha * 0.6, zorder=1))
        ax.add_patch(Circle((cx, cy), radius, facecolor=color,
                            edgecolor=None, alpha=alpha * 0.3, zorder=1))

    for _, row in edges_df.iterrows():
        ax.plot([row["x1"], row["x2"]], [row["y1"], row["y2"]],
                color=LINE_NORMAL, lw=0.5, alpha=0.2, zorder=1.5)

    target_row = edges_df.loc[edges_df["id"] == TARGET_EDGE_ID].iloc[0]
    target_state = line_states[TARGET_EDGE_ID]
    tx1, ty1, tx2, ty2 = target_row["x1"], target_row["y1"], target_row["x2"], target_row["y2"]

    td = euclid_dist(target_row["mid_x"], target_row["mid_y"], cx, cy)
    trisk = risk_from_dist(td, dyn_r_high, dyn_r_med, dyn_r_low)

    if target_state["status"] == "normal":
        ax.plot([tx1, tx2], [ty1, ty2], color=get_line_color_by_risk(trisk, "normal"),
                lw=get_line_width_by_risk(trisk, "normal"), alpha=0.9, zorder=4)
        if trisk == "high" and progress < 0.55 and not reconfiguration_triggered:
            target_state["status"] = "tripped"
            reconfiguration_triggered = True
            backup_line["activated"] = True
            print(f"Frame {frame}: Target tripped, backup activated")
    elif target_state["status"] == "tripped":
        if progress > 0.65 and intensity < 0.8:
            target_state["status"] = "recovering"
            target_state["recovery_start"] = frame
    elif target_state["status"] == "recovering":
        elapsed = frame - target_state["recovery_start"]
        target_state["recovery_progress"] = min(1.0, elapsed / RECOVERY_DURATION)
        if target_state["recovery_progress"] >= 1.0:
            target_state["status"] = "normal"
            backup_line["deactivating"] = True
            backup_line["deactivate_start_frame"] = frame

    if target_state["status"] == "recovering":
        c, lw = get_recovery_color(target_state["recovery_progress"])
        ax.plot([tx1, tx2], [ty1, ty2], color=c, lw=lw, alpha=0.9, zorder=4)

    #specific backup line control-using reconfiguration while "tripped"
    if backup_line["fbus"]:
        alpha = 1.0
        if backup_line.get("deactivating"):
            prog = min(1.0, (frame - backup_line["deactivate_start_frame"]) / NEW_LINE_FADE_IN)
            alpha = 1.0 - prog
            if prog >= 1.0:
                backup_line["activated"] = False
                backup_line["deactivating"] = False

        if backup_line["activated"]:
            ax.plot([backup_line["x1"], backup_line["x2"]], [backup_line["y1"], backup_line["y2"]],
                    color=LINE_NEW_START, lw=3, alpha=0.9 * alpha, zorder=5)
            backup_line["phase"] = (backup_line.get("phase", 0) + 0.04) % 1.0
            for off in [0, 0.5]:
                t = (backup_line["phase"] + off) % 1.0
                px, py = interpolate_point(backup_line["x1"], backup_line["y1"],
                                           backup_line["x2"], backup_line["y2"], t)
                ax.scatter(px, py, s=25, color=LINE_NEW_START, alpha=0.8 * alpha,
                           edgecolors="white", zorder=6)
        else:
            ax.plot([backup_line["x1"], backup_line["x2"]], [backup_line["y1"], backup_line["y2"]],
                    color="#6A7A8A", lw=1.5, alpha=0.4, zorder=3)

    for _, row in edges_df.iterrows():
        if row["id"] == TARGET_EDGE_ID:
            continue
        state = line_states[row["id"]]
        d = euclid_dist(row["mid_x"], row["mid_y"], cx, cy)
        risk = risk_from_dist(d, dyn_r_high, dyn_r_med, dyn_r_low)

        if state["status"] != "tripped":
            if risk == "high":
                state["damage"] += 1.0 * intensity
            else:
                state["damage"] = max(0, state["damage"] - 0.5)
            if state["damage"] >= 2.0:
                state["status"] = "tripped"
        else:
            if progress > 0.55 and risk in ["normal", "low"]:
                state["recover"] += 1
            else:
                state["recover"] = 0
            if state["recover"] >= 4:
                state["status"] = "recovering"
                state["recovery_start"] = frame

        if state["status"] == "recovering":
            elapsed = frame - state["recovery_start"]
            state["recovery_progress"] = min(1.0, elapsed / RECOVERY_DURATION)
            if state["recovery_progress"] >= 1.0:
                state["status"] = "normal"
        if state["status"] == "tripped":
            ax.plot([row["x1"], row["x2"]], [row["y1"], row["y2"]], color=LINE_TRIPPED, lw=1.5,
                    linestyle=(0, (4, 4)), alpha=0.6, zorder=3)
        elif state["status"] == "recovering":
            c, lw = get_recovery_color(state["recovery_progress"])
            ax.plot([row["x1"], row["x2"]], [row["y1"], row["y2"]], color=c, lw=lw, alpha=0.8, zorder=4)
        else:
            ax.plot([row["x1"], row["x2"]], [row["y1"], row["y2"]],
                    color=get_line_color_by_risk(risk, state["status"]),
                    lw=get_line_width_by_risk(risk, state["status"]), alpha=0.8, zorder=4)

        flow = get_flow_color_by_risk(risk, state["status"])
        if flow and state["status"] not in ["tripped"]:
            state["phase"] = (state["phase"] + state["base_speed"]) % 1.0
            for off in [0, 0.5]:
                t = (state["phase"] + off) % 1.0
                px, py = interpolate_point(row["x1"], row["y1"], row["x2"], row["y2"], t)
                ax.scatter(px, py, s=18, color=flow, alpha=0.7, edgecolors="none", zorder=5)
    for bid, (x, y) in bus_coords.items():
        size = 6
        color = BUS_NORMAL
        if backup_line.get("activated") and bid in [backup_line["fbus"], backup_line["tbus"]]:
            size = 12
            color = LINE_NEW_START
        ax.scatter(x, y, s=size, color=color, alpha=0.7, zorder=5)
        if bid in gen_bus_set:
            ax.text(x, y, "⚡", fontsize=12, ha='center', va='center', zorder=8,
                    path_effects=[path_effects.withStroke(linewidth=1.5, foreground='black')])



print(f"Target line ID: {TARGET_EDGE_ID}")
print(f"Figure size: {fig_width} x {fig_height} inches")
print("Generating animation...")


fig, ax = plt.subplots(figsize=(fig_width, fig_height), facecolor=BG)
ax.set_facecolor(BG)
fig.patch.set_alpha(0)
ax.patch.set_alpha(0)

for frame in range(N_FRAMES):
    update(frame)
    save_path = os.path.join(OUTPUT_FOLDER, f"frame_{frame:04d}.png")
    plt.savefig(save_path, transparent=True, dpi=DPI, bbox_inches='tight', pad_inches=0)
    if frame % 50 == 0:
        print(f"Saved frame {frame}/{N_FRAMES}")

plt.close(fig)
print(f"Done. Saved {N_FRAMES} frames to {OUTPUT_FOLDER}")
