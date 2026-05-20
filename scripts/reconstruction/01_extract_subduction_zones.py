import pygplates
import numpy as np
import pandas as pd
from pathlib import Path

# ============================================================
# User settings
# ============================================================

ROTATION_FILE = "data/rotations.rot"
TOPOLOGY_FILE = "data/topologies.gpml"
SUBDUCTION_FILE = "data/subduction_zones.gpml"

OUTPUT_DIR = Path("outputs/trench_coordinates")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RECONSTRUCTION_TIMES = [50, 90, 140]   # Ma


# ============================================================
# Load reconstruction model
# ============================================================

rotation_model = pygplates.RotationModel(ROTATION_FILE)

# Subduction zones can be loaded as GPlates feature collections
subduction_features = pygplates.FeatureCollection(SUBDUCTION_FILE)


# ============================================================
# Reconstruct subduction zones through time
# ============================================================

def extract_reconstructed_subduction_zones(time_ma):
    """
    Reconstruct subduction zone geometries at a given geological time.

    Returns a pandas DataFrame with longitude, latitude, time, and feature id.
    """

    reconstructed_features = []

    pygplates.reconstruct(
        subduction_features,
        rotation_model,
        reconstructed_features,
        time_ma
    )

    rows = []

    for reconstructed_feature in reconstructed_features:
        feature = reconstructed_feature.get_feature()
        reconstructed_geometry = reconstructed_feature.get_reconstructed_geometry()

        if reconstructed_geometry is None:
            continue

        feature_id = str(feature.get_feature_id())

        # Geometry can be polyline or multipoint depending on source file
        if isinstance(reconstructed_geometry, pygplates.PolylineOnSphere):
            points = reconstructed_geometry.get_points()
        else:
            try:
                points = reconstructed_geometry.get_points()
            except Exception:
                continue

        for point in points:
            lat, lon = point.to_lat_lon()

            rows.append({
                "time_ma": time_ma,
                "feature_id": feature_id,
                "lon": lon,
                "lat": lat
            })

    return pd.DataFrame(rows)


# ============================================================
# Run extraction
# ============================================================

for time_ma in RECONSTRUCTION_TIMES:
    df = extract_reconstructed_subduction_zones(time_ma)

    out_file = OUTPUT_DIR / f"subduction_zone_coordinates_{time_ma}Ma.csv"
    df.to_csv(out_file, index=False)

    print(f"Saved {out_file} with {len(df)} points")
