import os
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BASE = r"E:/Code/Yueqian/yolo-snacks"
ASSETS = os.path.join(BASE, "report_assets")
os.makedirs(ASSETS, exist_ok=True)

# Model -> results.csv mapping
CSV_11S_BASE = os.path.join(BASE, "runs/detect/runs/snacks/results.csv")
CSV_11S_OS   = os.path.join(BASE, "runs/detect/runs/snacks_11s_balanced/results.csv")
CSV_12X_OS   = os.path.join(BASE, "runs/detect/runs/snacks_12x_balanced/results.csv")

MODELS = ["11s-base", "11s-OS", "12x-OS"]
COLORS = ["#4C78A8", "#F58518", "#54A24B"]  # blue, orange, green

# ---------------------------------------------------------------------------
# 1) Regenerate the 12x training-curve plot (results.png) via ultralytics
# ---------------------------------------------------------------------------
results_png_12x = None
try:
    from ultralytics.utils.plotting import plot_results
    plot_results(file=CSV_12X_OS)
    candidate = os.path.join(os.path.dirname(CSV_12X_OS), "results.png")
    if os.path.exists(candidate):
        results_png_12x = candidate
        print("OK 12x results.png ->", candidate)
    else:
        print("WARN: results.png not found at", candidate)
except Exception as e:
    print("ERROR generating 12x results.png:", repr(e))

# ---------------------------------------------------------------------------
# Helper: read epoch + a metric column from a results.csv
# ---------------------------------------------------------------------------
def read_metric(path, col):
    epochs, vals = [], []
    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)
        # strip whitespace from header names
        reader.fieldnames = [h.strip() for h in reader.fieldnames]
        for row in reader:
            row = {k.strip(): (v.strip() if v is not None else v) for k, v in row.items()}
            epochs.append(int(float(row["epoch"])))
            vals.append(float(row[col]))
    return np.array(epochs), np.array(vals)

# ---------------------------------------------------------------------------
# 2) Per-class mAP50-95 grouped horizontal bars
# ---------------------------------------------------------------------------
PERCLS = """class, n, 11s_base, 11s_OS, 12x_OS
Ashi Mashi snacks, 10, 0.995, 0.995, 0.995
Chee pellet ketchup, 23, 0.988, 0.990, 0.983
Chee pellet vinegar, 20, 0.995, 0.995, 0.995
Cheetoz chili chips, 5, 0.995, 0.995, 0.995
Cheetoz ketchup chips, 18, 0.995, 0.995, 0.995
Cheetoz onion and parsley chips, 14, 0.995, 0.995, 0.995
Cheetoz salty chips, 6, 0.995, 0.995, 0.995
Cheetoz snack 30g, 4, 0.964, 0.964, 0.937
Cheetoz snack 90g, 14, 0.973, 0.962, 0.972
Cheetoz vinegar chips, 14, 0.995, 0.995, 0.995
Cheetoz wheelsnack, 16, 0.995, 0.995, 0.995
Maz Maz ketchup chips, 31, 0.983, 0.995, 0.995
Maz Maz potato sticks, 26, 0.969, 0.976, 0.974
Maz Maz salty chips, 13, 0.991, 0.981, 0.974
Maz Maz vinegar chips, 14, 0.972, 0.986, 0.980
Mini Lina, 40, 0.984, 0.984, 0.987
Minoo cream biscuit, 16, 0.952, 0.961, 0.946
Naderi mini cookie, 16, 0.987, 0.989, 0.989
Naderi mini wafer, 4, 0.995, 0.995, 0.995"""

rows = []
for line in PERCLS.strip().splitlines()[1:]:
    parts = [p.strip() for p in line.split(",")]
    # class name may contain no commas in this data, so parts maps directly
    cls = parts[0]
    n = int(parts[1])
    base = float(parts[2]); os_v = float(parts[3]); x12 = float(parts[4])
    rows.append((cls, n, base, os_v, x12))

# sort ascending by 11s_OS value
rows.sort(key=lambda r: r[3])
classes = [r[0] for r in rows]
v_base = [r[2] for r in rows]
v_os   = [r[3] for r in rows]
v_12x  = [r[4] for r in rows]

y = np.arange(len(classes))
bar_h = 0.26

fig, ax = plt.subplots(figsize=(11, 11))
b1 = ax.barh(y + bar_h, v_base, height=bar_h, color=COLORS[0], label=MODELS[0])
b2 = ax.barh(y,         v_os,   height=bar_h, color=COLORS[1], label=MODELS[1])
b3 = ax.barh(y - bar_h, v_12x,  height=bar_h, color=COLORS[2], label=MODELS[2])

ax.set_yticks(y)
ax.set_yticklabels(classes)
ax.set_xlim(0.92, 1.0)
ax.set_xlabel("mAP50-95")
ax.set_title("Per-class mAP50-95 (3 models)")
ax.legend(loc="lower left")
ax.grid(axis="x", linestyle="--", alpha=0.4)

for bars in (b1, b2, b3):
    for rect in bars:
        w = rect.get_width()
        ax.text(w + 0.0015, rect.get_y() + rect.get_height() / 2,
                f"{w:.3f}", va="center", ha="left", fontsize=6.5)

ax.set_xlim(0.92, 1.0 + 0.01)
fig.tight_layout()
percls_path = os.path.join(ASSETS, "percls_compare.png")
fig.savefig(percls_path, dpi=150)
plt.close(fig)
print("OK ->", percls_path)

# ---------------------------------------------------------------------------
# 3) Overall metrics grouped bar chart
# ---------------------------------------------------------------------------
mAP50    = [0.9941, 0.9942, 0.9948]
mAP5095  = [0.9851, 0.9865, 0.9839]

groups = ["mAP50", "mAP50-95"]
x = np.arange(len(groups))
bar_w = 0.25

fig, ax = plt.subplots(figsize=(8, 6))
# data per model across the two groups
data_by_model = [
    [mAP50[0], mAP5095[0]],
    [mAP50[1], mAP5095[1]],
    [mAP50[2], mAP5095[2]],
]
bars_list = []
for i, (model, color) in enumerate(zip(MODELS, COLORS)):
    offset = (i - 1) * bar_w
    bars = ax.bar(x + offset, data_by_model[i], width=bar_w, color=color, label=model)
    bars_list.append(bars)

for bars in bars_list:
    for rect in bars:
        h = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2, h + 0.0004,
                f"{h:.4f}", ha="center", va="bottom", fontsize=8)

ax.set_xticks(x)
ax.set_xticklabels(groups)
ax.set_ylim(0.97, 1.0)
ax.set_ylabel("Score")
ax.set_title("Overall metrics (3 models)")
ax.legend(loc="lower right")
ax.grid(axis="y", linestyle="--", alpha=0.4)
fig.tight_layout()
overall_path = os.path.join(ASSETS, "overall_compare.png")
fig.savefig(overall_path, dpi=150)
plt.close(fig)
print("OK ->", overall_path)

# ---------------------------------------------------------------------------
# 4) Loss curves: 1x2 subplots, val/box_loss and val/cls_loss vs epoch
# ---------------------------------------------------------------------------
csv_map = [
    (MODELS[0], CSV_11S_BASE, COLORS[0]),
    (MODELS[1], CSV_11S_OS,   COLORS[1]),
    (MODELS[2], CSV_12X_OS,   COLORS[2]),
]

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for model, path, color in csv_map:
    ep, box = read_metric(path, "val/box_loss")
    axes[0].plot(ep, box, label=model, color=color, linewidth=1.6)
    ep2, cls = read_metric(path, "val/cls_loss")
    axes[1].plot(ep2, cls, label=model, color=color, linewidth=1.6)

axes[0].set_title("Validation box_loss vs epoch")
axes[0].set_xlabel("Epoch")
axes[0].set_ylabel("val/box_loss")
axes[0].legend()
axes[0].grid(linestyle="--", alpha=0.4)

axes[1].set_title("Validation cls_loss vs epoch")
axes[1].set_xlabel("Epoch")
axes[1].set_ylabel("val/cls_loss")
axes[1].legend()
axes[1].grid(linestyle="--", alpha=0.4)

fig.suptitle("Validation loss curves (overfitting check)")
fig.tight_layout()
loss_path = os.path.join(ASSETS, "loss_curves.png")
fig.savefig(loss_path, dpi=150)
plt.close(fig)
print("OK ->", loss_path)

print("RESULTS_PNG_12X=", results_png_12x)
print("DONE")
