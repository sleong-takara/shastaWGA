# Barnyard Doublet Rate Analysis

Perform a barnyard (human/mouse) doublet rate analysis on a well barcode purity Excel file and produce a scatterplot.

## Usage

`/barnyard-doublet-rate [path/to/file.xlsx]`

If no path is given, look for `assets/data/*.xlsx` or ask the user to specify one.

## What this command does

Given an Excel file with columns including `Sample`, `Uniquely_Mapped_Reads_human`, and `Uniquely_Mapped_Reads_mouse`:

1. **Neg Ctrl threshold**: Find all wells where `Sample == "Neg Ctrl"`. For each, compute `total_unique_reads = Uniquely_Mapped_Reads_human + Uniquely_Mapped_Reads_mouse`. The threshold is the **maximum** total unique reads among all Neg Ctrl wells.

2. **Mix well classification**: Among wells where `Sample == "Mix"` and `total_unique_reads > threshold`:
   - `human_purity = Uniquely_Mapped_Reads_human / total_unique_reads`
   - `mouse_purity = Uniquely_Mapped_Reads_mouse / total_unique_reads`
   - **Singlet**: `human_purity >= 0.8` OR `mouse_purity >= 0.8`
   - **Doublet**: `human_purity > 0.2 AND human_purity < 0.8 AND mouse_purity > 0.2 AND mouse_purity < 0.8`

3. **Doublet rate**: `n_doublets / (n_doublets + n_singlets) * 100`

4. **Scatterplot** saved to `assets/output/doublet_scatterplot.png`:
   - X axis: `Uniquely_Mapped_Reads_human`, Y axis: `Uniquely_Mapped_Reads_mouse`
   - Plot Mix (gray), K562 (red), 3T3 (blue) wells **above the threshold**
   - Two purity-arm dashed lines from origin:
     - Human purity = 0.8: slope = 0.25 (i.e., `mouse = 0.25 * human`)
     - Mouse purity = 0.8: slope = 4.0 (i.e., `mouse = 4 * human`)
   - Title shows the doublet rate

## Implementation

Write (or overwrite) `assets/scripts/doublet_analysis.py` using the template below, then run it with Python. Report the Neg Ctrl threshold, singlet count, doublet count, and doublet rate to the user, and confirm the plot was saved.

```python
"""
doublet_analysis.py
-------------------
Doublet rate analysis for barnyard (human/mouse) single-cell experiment.
"""

import os, sys, shutil, tempfile
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# --- Paths ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_FILE   = os.path.join(PROJECT_DIR, "data", "$FILENAME")   # replace $FILENAME
OUTPUT_DIR  = os.path.join(PROJECT_DIR, "output")
PLOT_FILE   = os.path.join(OUTPUT_DIR, "doublet_scatterplot.png")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_excel(path):
    try:
        return pd.read_excel(path)
    except PermissionError:
        tmp = os.path.join(tempfile.gettempdir(), "wells_tmp.xlsx")
        shutil.copy2(path, tmp)
        return pd.read_excel(tmp)

df = load_excel(DATA_FILE)
df["total_unique_reads"] = df["Uniquely_Mapped_Reads_human"] + df["Uniquely_Mapped_Reads_mouse"]

# Neg Ctrl threshold
neg_ctrl = df[df["Sample"] == "Neg Ctrl"]
threshold = neg_ctrl["total_unique_reads"].max()
print(f"Neg Ctrl threshold: {threshold:,}")

# Mix wells above threshold
mix = df[(df["Sample"] == "Mix") & (df["total_unique_reads"] > threshold)].copy()
mix["human_purity"] = mix["Uniquely_Mapped_Reads_human"] / mix["total_unique_reads"]
mix["mouse_purity"] = mix["Uniquely_Mapped_Reads_mouse"] / mix["total_unique_reads"]

def classify(row):
    hp, mp = row["human_purity"], row["mouse_purity"]
    if hp >= 0.8 or mp >= 0.8:
        return "singlet"
    elif hp > 0.2 and hp < 0.8 and mp > 0.2 and mp < 0.8:
        return "doublet"
    return "unclassified"

mix["classification"] = mix.apply(classify, axis=1)
n_s = (mix["classification"] == "singlet").sum()
n_d = (mix["classification"] == "doublet").sum()
rate = n_d / (n_d + n_s) * 100
print(f"Singlets: {n_s}  Doublets: {n_d}  Doublet rate: {rate:.2f}%")

# Scatterplot
colors = {"Mix": "gray", "K562": "red", "3T3": "blue"}
fig, ax = plt.subplots(figsize=(8, 7))
for sample, color in colors.items():
    sub = df[(df["Sample"] == sample) & (df["total_unique_reads"] > threshold)]
    ax.scatter(sub["Uniquely_Mapped_Reads_human"], sub["Uniquely_Mapped_Reads_mouse"],
               c=color, alpha=0.5, s=10, label=sample, rasterized=True)

all_above = df[df["Sample"].isin(colors) & (df["total_unique_reads"] > threshold)]
line_max = max(all_above["Uniquely_Mapped_Reads_human"].max(),
               all_above["Uniquely_Mapped_Reads_mouse"].max())
x = np.array([0, line_max])
ax.plot(x, 0.25 * x, "k--", linewidth=1.5, label="Human purity = 0.8")
ax.plot(x / 4, x, "k-.", linewidth=1.5, label="Mouse purity = 0.8")
ax.text(line_max*0.55, line_max*0.55*0.25 + line_max*0.02,
        "Human purity = 0.8", fontsize=7, rotation=14)
ax.text(line_max*0.18, line_max*0.18*4*0.92,
        "Mouse purity = 0.8", fontsize=7, rotation=76)

ax.set_xlabel("Uniquely Mapped Reads (Human)", fontsize=11)
ax.set_ylabel("Uniquely Mapped Reads (Mouse)", fontsize=11)
ax.set_title(f"Barnyard Plot — Doublet Rate: {rate:.2f}%", fontsize=13)
ax.legend(fontsize=9, markerscale=2)
ax.set_xlim(left=0); ax.set_ylim(bottom=0)
plt.tight_layout()
plt.savefig(PLOT_FILE, dpi=150)
plt.close()
print(f"Plot saved to: {PLOT_FILE}")
```
