import numpy as np
import pandas as pd
from pathlib import Path

INPUT_DIR = Path("outputs/slab_depth_coordinates")
OUTPUT_DIR = Path("outputs/global_grids")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RECONSTRUCTION_TIMES = [50, 90, 140]
DEPTHS_KM = [100, 200, 300, 400, 500, 600]

GRID_SPACING_DEG = 1.0
SLAB_VALUE = 5
BACKGROUND_VALUE = 0

lons = np.arange(-180, 180 + GRID_SPACING_DEG, GRID_SPACING_DEG)
lats = np.arange(-90, 90 + GRID_SPACING_DEG, GRID_SPACING_DEG)


def nearest_index(array, value):
    return np.abs(array - value).argmin()


for time_ma in RECONSTRUCTION_TIMES:
    input_file = INPUT_DIR / f"slab_points_{time_ma}Ma.csv"
    slab_df = pd.read_csv(input_file)

    for depth_km in DEPTHS_KM:
        grid = np.full((len(lats), len(lons)), BACKGROUND_VALUE)

        depth_df = slab_df[slab_df["depth_km"] == depth_km]

        for _, row in depth_df.iterrows():
            lon_idx = nearest_index(lons, row["slab_lon"])
            lat_idx = nearest_index(lats, row["slab_lat"])

            grid[lat_idx, lon_idx] = SLAB_VALUE

        rows = []

        for i, lat in enumerate(lats):
            for j, lon in enumerate(lons):
                rows.append({
                    "lon": lon,
                    "lat": lat,
                    "value": grid[i, j]
                })

        grid_df = pd.DataFrame(rows)

        output_file = OUTPUT_DIR / f"slab_grid_{time_ma}Ma_{depth_km}km.csv"
        grid_df.to_csv(output_file, index=False)

        print(f"Saved {output_file}")
