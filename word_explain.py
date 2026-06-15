import matplotlib.pyplot as plt
import os

OUTPUT_FOLDER = r"D:\IRL_terrain\Image\explaination"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

N_FRAMES = 300
MATRIX_ROWS = 4
MATRIX_COLS = 5

def get_storm_intensity(frame):
    progress = frame / N_FRAMES
    if progress < 0.35:
        return 0.5 + progress / 0.35 * 1.0
    elif progress < 0.5:
        return 1.5
    else:
        t = (progress - 0.5) / 0.5
        t = max(0.0, min(1.0, t))
        return 1.5 - t * (1.5 - 0.3)

cells = []

cells.append((0, 15, "Normal", "Grid stable", "No anomalies detected"))
cells.append((15, 30, "Storm Alert", "Approaching from west", "Weather radar warning"))
cells.append((30, 45, "Monitoring", "Tracking storm path", "Real-time data analysis"))
cells.append((45, 75, "Warning", "High wind warning", "Prepare for impact"))

cells.append((75, 90, "Peak Intensity", "Maximum storm force", "Winds > 80km/h"))
cells.append((90, 130, "Critical", "Grid at high risk", "Multiple lines tripped"))
cells.append((130, 139, "Line Tripped", "Target line disconnected", "Automatic protection triggered"))
cells.append((139, 160, "Backup Active", "Emergency reroute online", "Redundant path engaged"))

cells.append((160, 230, "Weakening", "Storm intensity dropping", "Winds decreasing"))
cells.append((230, 240, "Repair Started", "Restoration initiated", "Crew dispatched"))
cells.append((240, 255, "Restoring", "Power flow returning", "Gradual load increase"))
cells.append((210, 275, "Stabilizing", "Grid stabilizing", "Voltage normalization"))

cells.append((275, 290, "Complete", "Recovery successful", "Mission accomplished"))
cells.append((290, 300, "End", "Simulation complete", "Final system check"))

def get_current_cell(frame):
    for start, end, icon, title, subtitle in cells:
        if start <= frame <= end:
            return icon, title, subtitle, start, end
    return None, None, None, None, None


for frame in range(N_FRAMES):
    fig, ax = plt.subplots(figsize=(8, 6), facecolor='none')
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')
    ax.axis('off')
    icon, title, subtitle, start, end = get_current_cell(frame)
    intensity = get_storm_intensity(frame)

    ax.text(0.5, 0.7, icon, fontsize=80, ha='center', va='center', color='white')
    ax.text(0.5, 0.5, title, fontsize=24, color='white',
            ha='center', va='center', fontweight='bold')
    ax.text(0.5, 0.4, subtitle, fontsize=14, color='white',
            ha='center', va='center')

    ax.text(0.5, 0.15, f"Storm Intensity: {intensity:.2f}",
            fontsize=10, color='white', ha='center', va='center')
    ax.text(0.5, 0.08, f"Frame: {frame}/{N_FRAMES}  |  Time: {start}-{end}",
            fontsize=9, color='white', ha='center', va='center')

    frame_filename = f"frame_{frame:04d}.png"
    output_path = os.path.join(OUTPUT_FOLDER, frame_filename)
    plt.savefig(output_path, dpi=150, transparent=True, bbox_inches='tight')
    plt.close()

    if frame % 30 == 0:
        print(f" progress: {frame}/{N_FRAMES} ({frame / N_FRAMES * 100:.1f}%)")

print(f"\n✅ Saved {N_FRAMES} frames of PNG sequence")
print(f"   Path: {OUTPUT_FOLDER}")