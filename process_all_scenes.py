import os
import rasterio
import numpy as np
import logging
import datetime
import time
import argparse
import csv
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from indices.index_calculations import (
    calculate_ndvi, calculate_savi, calculate_evi,
    calculate_arvi, calculate_nbr, calculate_nbwi,
    calculate_ndbi, calculate_gci
)

# === CLI Arguments ===
parser = argparse.ArgumentParser(description="Batch process vegetation indices.")
parser.add_argument('--scene', type=str, help="Name of a specific scene folder to process.")
parser.add_argument('--input', type=str, default="data/input", help="Input folder containing scenes.")
parser.add_argument('--output', type=str, default="data/output", help="Output folder for results.")
parser.add_argument(
    '--indices',
    nargs='+',
    choices=["NDVI", "SAVI", "EVI", "ARVI", "NBR", "NBWI", "NDBI", "GCI"],
    help="List of indices to compute. If omitted, all indices will be calculated."
)
args = parser.parse_args()

INPUT_ROOT = args.input
OUTPUT_ROOT = args.output
SELECTED_INDICES = args.indices or ["NDVI", "SAVI", "EVI", "ARVI", "NBR", "NBWI", "NDBI", "GCI"]

# === Logging Setup ===
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = os.path.join(log_dir, f"batch_run_{timestamp}.log")

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s"
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger().addHandler(console)

# === Band File Map ===
band_files = {
    "B2": "B2.tif",
    "B3": "B3.tif",
    "B4": "B4.tif",
    "B5": "B5.tif",
    "B6": "B6.tif",
    "B7": "B7.tif",
}

def load_band(path):
    try:
        with rasterio.open(path) as src:
            return src.read(1).astype('float32'), src.profile
    except Exception as e:
        logging.error(f"Failed to load band: {path} — {e}")
        return None, None

def save_index(index_array, name, profile, output_dir):
    try:
        os.makedirs(output_dir, exist_ok=True)
        profile.update(dtype=rasterio.float32, count=1)
        out_path = os.path.join(output_dir, f"{name}.tif")
        with rasterio.open(out_path, 'w', **profile) as dst:
            dst.write(index_array.astype(rasterio.float32), 1)
        logging.info(f"✅ Saved {out_path}")
        return True
    except Exception as e:
        logging.error(f"❌ Failed to save {name}: {e}")
        return False

def process_scene(scene_path, selected_indices):
    scene_name = os.path.basename(scene_path)
    logging.info(f"\n📦 Processing scene: {scene_name}")
    start_time = time.time()

    bands = {}
    profile = None
    results = {"scene": scene_name, "time_sec": 0}

    for band_key, filename in band_files.items():
        path = os.path.join(scene_path, filename)
        if os.path.exists(path):
            bands[band_key], profile = load_band(path)
            if bands[band_key] is None:
                logging.warning(f"⚠️ Could not load {filename} in {scene_name}")
        else:
            logging.warning(f"⚠️ Missing {filename} in {scene_name}")

    output_dir = os.path.join(OUTPUT_ROOT, scene_name)

    try:
        if {"B4", "B5"}.issubset(bands) and "NDVI" in selected_indices:
            results["NDVI"] = save_index(calculate_ndvi(bands["B5"], bands["B4"]), "NDVI", profile, output_dir)
        if {"B4", "B5"}.issubset(bands) and "SAVI" in selected_indices:
            results["SAVI"] = save_index(calculate_savi(bands["B5"], bands["B4"]), "SAVI", profile, output_dir)
        if {"B2", "B4", "B5"}.issubset(bands) and "EVI" in selected_indices:
            results["EVI"] = save_index(calculate_evi(bands["B5"], bands["B4"], bands["B2"]), "EVI", profile, output_dir)
        if {"B3", "B4", "B5"}.issubset(bands) and "ARVI" in selected_indices:
            results["ARVI"] = save_index(calculate_arvi(bands["B5"], bands["B4"], bands["B3"]), "ARVI", profile, output_dir)
        if {"B5", "B7"}.issubset(bands) and "NBR" in selected_indices:
            results["NBR"] = save_index(calculate_nbr(bands["B5"], bands["B7"]), "NBR", profile, output_dir)
        if {"B3", "B5"}.issubset(bands) and "NBWI" in selected_indices:
            results["NBWI"] = save_index(calculate_nbwi(bands["B3"], bands["B5"]), "NBWI", profile, output_dir)
        if {"B5", "B6"}.issubset(bands) and "NDBI" in selected_indices:
            results["NDBI"] = save_index(calculate_ndbi(bands["B6"], bands["B5"]), "NDBI", profile, output_dir)
        if {"B3", "B7"}.issubset(bands) and "GCI" in selected_indices:
            results["GCI"] = save_index(calculate_gci(bands["B7"], bands["B3"]), "GCI", profile, output_dir)
    except Exception as e:
        logging.error(f"Unexpected error in {scene_name}: {e}")

    elapsed = time.time() - start_time
    results["time_sec"] = round(elapsed, 2)
    logging.info(f"✅ Finished {scene_name} in {elapsed:.2f}s")
    return results

def save_summary(results, output_dir):
    csv_path = os.path.join(output_dir, f"summary_{timestamp}.csv")
    fieldnames = ["scene", "NDVI", "SAVI", "EVI", "ARVI", "NBR", "NBWI", "NDBI", "GCI", "time_sec"]
    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    logging.info(f"📄 Summary CSV saved to {csv_path}")

# === Run Batch ===
logging.info("🚀 Batch index processing started...\n")

scene_folders = [args.scene] if args.scene else [
    folder for folder in os.listdir(INPUT_ROOT)
    if os.path.isdir(os.path.join(INPUT_ROOT, folder))
]

all_results = []

if len(scene_folders) == 1:
    result = process_scene(os.path.join(INPUT_ROOT, scene_folders[0]), SELECTED_INDICES)
    all_results.append(result)
else:
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(process_scene, os.path.join(INPUT_ROOT, folder), SELECTED_INDICES): folder
            for folder in scene_folders
        }

        for future in tqdm(as_completed(futures), total=len(futures), desc="📦 Processing Scenes", unit="scene"):
            try:
                result = future.result()
                all_results.append(result)
            except Exception as e:
                logging.error(f"❌ Error in {futures[future]}: {e}")

save_summary(all_results, OUTPUT_ROOT)
logging.info("\n🎉 All scenes processed.")
