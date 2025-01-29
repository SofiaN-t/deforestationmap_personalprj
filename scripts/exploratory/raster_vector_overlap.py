## Functions
import sys
import os
import time
import rasterio
import geopandas as gpd
from rasterio.features import geometry_mask

# Check if running in an interactive environment eg when running line-by-line
def is_interactive():
    import __main__ as main
    return not hasattr(main, '__file__')

# Add the root directory to the sys.path if not running interactively
if not is_interactive():
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..\..')))
    print(os.path.join(os.path.dirname(__file__), '..\..'))

# Load configuration file
from utils import load_config
config = load_config()

raster_filepath = os.path.abspath(config['data_paths']['raw']['radd'])
vector_filepath = os.path.abspath(config['data_paths']['processed']['coffee_plots'])

# Open raster and vector data
start_time = time.time()

src=rasterio.open(raster_filepath)

intersection_results = {}
with rasterio.open(raster_filepath) as src:
    vector_data = gpd.read_file(vector_filepath)
    transform = src.transform
    vector_mask_full = geometry_mask(vector_data.geometry, out_shape=(src.height, src.width), transform=transform, invert=True)
    
    # Define window size and process each chunk
    for ji, window in src.block_windows(1):
        raster_data = src.read(1, window=window)
        threshold = 0
        raster_mask = (raster_data > threshold).astype(int)
        
        # Extract the corresponding part of the vector mask
        vector_mask = vector_mask_full[
            window.row_off:window.row_off + window.height,
            window.col_off:window.col_off + window.width
        ]
        
        intersection = raster_mask & vector_mask
        if intersection.any():
            local_indices = intersection.nonzero()  # Local to the current window

            # Convert local indices to global indices
            global_row_indices = local_indices[0] + window.row_off
            global_col_indices = local_indices[1] + window.col_off

            # Store the global indices
            intersection_results[ji] = (global_row_indices, global_col_indices)

print("Finding intersections took --- %s seconds ---" % (time.time() - start_time))

        # Optionally, print or store the global indices
       # print(f"Window {ji}: Local indices {local_indices}")
       # print(f"Window {ji}: Global indices (rows, cols) {list(zip(global_row_indices, global_col_indices))}")