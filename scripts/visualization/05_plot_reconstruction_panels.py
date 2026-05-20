import pygmt
import pandas as pd
from pathlib import Path

TIME_MA = 50

trench_file = f"outputs/trench_coordinates/subduction_zone_coordinates_{TIME_MA}Ma.csv"
slab_file = f"outputs/slab_depth_coordinates/slab_points_{TIME_MA}Ma.csv"

trench_df = pd.read_csv(trench_file)
slab_df = pd.read_csv(slab_file)

fig = pygmt.Figure()

fig.basemap(
    region="g",
    projection="W0/15c",
    frame=True
)

fig.coast(
    land="white",
    water="white",
    shorelines="0.5p,black",
    borders="0.25p,gray"
)

fig.plot(
    x=trench_df["lon"],
    y=trench_df["lat"],
    pen="1p,red"
)

fig.plot(
    x=slab_df["slab_lon"],
    y=slab_df["slab_lat"],
    style="c0.03c",
    fill="black"
)

fig.text(
    x=-170,
    y=75,
    text=f"{TIME_MA} Ma",
    font="18p,Helvetica-Bold,yellow"
)

fig.savefig(f"outputs/figures/reconstruction_{TIME_MA}Ma.png", dpi=300)
