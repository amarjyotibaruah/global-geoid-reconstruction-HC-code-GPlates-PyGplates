import numpy as np
import pandas as pd
from pathlib import Path

INPUT_DIR = Path("outputs/trench_coordinates")
OUTPUT_DIR = Path("outputs/slab_depth_coordinates")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RECONSTRUCTION_TIMES = [50, 90, 140]

DEPTHS_KM = [100, 200, 300, 400, 500, 600]
DIP_DEGREES = 45.0

EARTH_RADIUS_KM = 6371.0


def move_point_spherical(lon, lat, azimuth_deg, distance_km):
    """
    Move a lon, lat point along a given azimuth by distance_km.
    Azimuth is measured clockwise from north.
    """

    lon1 = np.radians(lon)
    lat1 = np.radians(lat)
    az = np.radians(azimuth_deg)
    angular_distance = distance_km / EARTH_RADIUS_KM

    lat2 = np.arcsin(
        np.sin(lat1) * np.cos(angular_distance)
        + np.cos(lat1) * np.sin(angular_distance) * np.cos(az)
    )

    lon2 = lon1 + np.arctan2(
        np.sin(az) * np.sin(angular_distance) * np.cos(lat1),
        np.cos(angular_distance) - np.sin(lat1) * np.sin(lat2)
    )

    return np.degrees(lon2), np.degrees(lat2)


def estimate_local_trench_azimuth(df):
    """
    Estimate trench azimuth from neighbouring points.
    This is a simplified method.
    For publication work, use ordered trench polylines directly.
    """

    azimuths = []

    for i in range(len(df)):
        if i == 0:
            p1 = df.iloc[i]
            p2 = df.iloc[i + 1]
        elif i == len(df) - 1:
            p1 = df.iloc[i - 1]
            p2 = df.iloc[i]
        else:
            p1 = df.iloc[i - 1]
            p2 = df.iloc[i + 1]

        dlon = p2["lon"] - p1["lon"]
        dlat = p2["lat"] - p1["lat"]

        azimuth = np.degrees(np.arctan2(dlon, dlat))
        azimuths.append(azimuth)

    return np.array(azimuths)


for time_ma in RECONSTRUCTION_TIMES:
    input_file = INPUT_DIR / f"subduction_zone_coordinates_{time_ma}Ma.csv"
    trench_df = pd.read_csv(input_file)

    trench_df["trench_azimuth"] = estimate_local_trench_azimuth(trench_df)

    slab_rows = []

    for _, row in trench_df.iterrows():
        trench_lon = row["lon"]
        trench_lat = row["lat"]
        trench_azimuth = row["trench_azimuth"]

        # Two possible normals to trench
        # You must choose the correct subduction polarity.
        # Here we use +90 as a placeholder.
        slab_azimuth = trench_azimuth + 90.0

        for depth_km in DEPTHS_KM:
            horizontal_offset_km = depth_km / np.tan(np.radians(DIP_DEGREES))

            slab_lon, slab_lat = move_point_spherical(
                trench_lon,
                trench_lat,
                slab_azimuth,
                horizontal_offset_km
            )

            slab_rows.append({
                "time_ma": time_ma,
                "depth_km": depth_km,
                "trench_lon": trench_lon,
                "trench_lat": trench_lat,
                "slab_lon": slab_lon,
                "slab_lat": slab_lat,
                "dip_degrees": DIP_DEGREES
            })

    slab_df = pd.DataFrame(slab_rows)

    output_file = OUTPUT_DIR / f"slab_points_{time_ma}Ma.csv"
    slab_df.to_csv(output_file, index=False)

    print(f"Saved {output_file} with {len(slab_df)} slab points")
