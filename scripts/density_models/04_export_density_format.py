import pandas as pd
from pathlib import Path

INPUT_DIR = Path("outputs/global_grids")
OUTPUT_DIR = Path("outputs/density_format")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def export_density_input(grid_file, output_file, layer_depth_km):
    """
    Convert global slab grid into a simple density heterogeneity format.

    Output format:
    lon lat depth_km density_value
    """

    df = pd.read_csv(grid_file)
    df["depth_km"] = layer_depth_km

    df = df[["lon", "lat", "depth_km", "value"]]
    df.to_csv(output_file, sep=" ", index=False, header=False)


for grid_file in INPUT_DIR.glob("slab_grid_*Ma_*km.csv"):
    name = grid_file.stem

    depth_text = name.split("_")[-1].replace("km", "")
    depth_km = float(depth_text)

    output_file = OUTPUT_DIR / f"{name}_density_input.txt"

    export_density_input(grid_file, output_file, depth_km)

    print(f"Saved {output_file}")
