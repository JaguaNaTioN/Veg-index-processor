# 🌿 Vegetation Index Processor

This Python-based tool allows you to batch process satellite scenes (from Landsat imagery) to compute key vegetation and water indices such as NDVI, SAVI, EVI, ARVI, NBR, NBWI, NDBI, and GCI. It supports single-scene or multi-scene processing, logs each step, generates GeoTIFF outputs, and compiles a summary CSV report.

---

## 🚀 Features

- Batch process multiple satellite image scenes.
- Supports major remote sensing indices:
  - NDVI, SAVI, EVI, ARVI, NBR, NBWI, NDBI, and GCI.
- Multi-threaded for faster performance.
- Handles missing bands gracefully and logs issues.
- Generates summary CSV reports of processing status and time.
- CLI for flexible and reproducible workflows.

---

## ✅ Prerequisites

- Python 3.6+
- `pip` for package installation

Install required packages:

```bash
pip install -r requirements.txt
```

> Required libraries include: `rasterio`, `numpy`, `tqdm`, and others.

---

## 📦 Installation

Clone the repository and navigate into it:

```bash
git clone https://github.com/JaguaNaTioN/veg-index-processor.git
cd veg-index-processor
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ⚙️ Usage

### Basic Command

Process all scenes from `data/input` and save results to `data/output`:

```bash
python process_all_scenes.py
```

### Advanced Options

```bash
python process_all_scenes.py \
    --input data/input \
    --output data/output \
    --indices NDVI SAVI EVI
```

| Argument     | Description |
|--------------|-------------|
| `--scene`    | (Optional) Specific scene folder name |
| `--input`    | Root folder of input scenes (default: `data/input`) |
| `--output`   | Destination for results (default: `data/output`) |
| `--indices`  | Space-separated list of indices to compute (default: all) |

---

## 🗂 Directory Structure

```
veg-index-processor/
│
├── data/
│   ├── input/                # Input scenes: each must contain band files (e.g., B2.tif, B3.tif)
│   └── output/               # Output results: GeoTIFFs and summary CSV
│
├── indices/
│   └── index_calculations.py  # Index computation logic
│
├── logs/
│   └── batch_run_*.log       # Timestamped log files
│
├── process_all_scenes.py     # Main processing script (moved from scripts/)
│
├── requirements.txt
└── README.md
```

---

## 📄 Output

For each scene, the following is generated:

- GeoTIFF files for each selected index
- A timestamped CSV summary report
- Log entries for each processing step

Example summary row:

| scene        | NDVI | SAVI | EVI | ... | time_sec |
|--------------|------|------|-----|-----|----------|
| scene001     | ✅    | ✅    | ✅   | ... | 12.32     |

---

## 🤝 Contributing

Got improvements or ideas? Feel free to fork this repository and submit a pull request. Contributions are welcome.

---

## 📜 License

This project is licensed under the MIT License. See `LICENSE` file for details.

---

## 📬 Contact

Created by [JaguaNaTioN] — For questions, reach out via [cmajumba@outlook.com] or open an issue in the repository.

---

## 🔗 Acknowledgements

- [Rasterio](https://rasterio.readthedocs.io/)
- [NumPy](https://numpy.org/)
- [TQDM](https://tqdm.github.io/)
