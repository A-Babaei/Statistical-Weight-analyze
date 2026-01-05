# ============================================================
# Weight Statistical Analysis – Final Clean Version
# Author: A. Babaei
# ============================================================

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from statsmodels.stats.multitest import multipletests

# ============================================================
# PATHS
# ============================================================

DATA_PATH = r"g:\Master\Experiment\Statistics\Weights\Weight_Statistical_analyze_Transposed.xlsx"
OUT_DIR = r"g:\Master\Experiment\Statistics\Weights\Results"
os.makedirs(OUT_DIR, exist_ok=True)

# ============================================================
# STYLE
# ============================================================

sns.set(style="whitegrid", context="talk")
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42

# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_excel(DATA_PATH)

# Rename columns
df.columns = ["Group"] + [f"Week_{i}" for i in range(1, 13)]

# Assign subject IDs
df["Subject"] = [f"PD_{i+1}" if i < 9 else f"CO_{i-8}" for i in range(len(df))]

# ============================================================
# LONG FORMAT
# ============================================================

df_long = df.melt(
    id_vars=["Subject", "Group"],
    var_name="Week",
    value_name="Weight"
)

df_long["WeekNum"] = df_long["Week"].str.extract(r"(\d+)").astype(int)

# ============================================================
# PHASE ASSIGNMENT
# ============================================================

def phase_label(w):
    if w <= 4:
        return "Pre-DBS"
    elif w <= 8:
        return "DBS"
    else:
        return "Post-DBS"

df_long["Phase"] = df_long["WeekNum"].apply(phase_label)

# ============================================================
# SUBSET GROUPS (THIS FIXES YOUR ERROR)
# ============================================================

df_pd = df_long[df_long["Group"] == "PD"]
df_co = df_long[df_long["Group"] == "CO"]

# ============================================================
# PHASE MEANS (PD ONLY – FOR RAINCLOUD)
# ============================================================

phase_means_pd = (
    df_pd
    .groupby(["Subject", "Phase"])["Weight"]
    .mean()
    .reset_index()
)

# ============================================================
# STATISTICS (PD ONLY)
# ============================================================

pre = phase_means_pd[phase_means_pd["Phase"] == "Pre-DBS"]["Weight"].values
dbs = phase_means_pd[phase_means_pd["Phase"] == "DBS"]["Weight"].values

t_stat, p_val = stats.ttest_rel(pre, dbs)
dz = (dbs - pre).mean() / (dbs - pre).std(ddof=1)

print("\nPD Weight Pre-DBS vs DBS:")
print("t =", round(t_stat, 3), "p =", round(p_val, 4), "Cohen's dz =", round(dz, 2))

# ============================================================
# RAINCLOUD-STYLE FIGURE: PD rats (Pre-DBS / DBS / Post-DBS)
# ============================================================

PHASE_ORDER = ["Pre-DBS", "DBS", "Post-DBS"]

plt.figure(figsize=(7,5))

# 1) Violin plot (distribution)
sns.violinplot(
    data=phase_means_pd,
    x="Phase",
    y="Weight",
    order=PHASE_ORDER,
    inner=None,
    cut=0,
    linewidth=0,
    color="#4C72B0"   # same blue tone as before
)

# 2) Boxplot inside violin
sns.boxplot(
    data=phase_means_pd,
    x="Phase",
    y="Weight",
    order=PHASE_ORDER,
    width=0.25,
    showcaps=True,
    boxprops={
        "facecolor": "none",
        "edgecolor": "black",
        "linewidth": 1.4
    },
    whiskerprops={"linewidth": 1.4},
    medianprops={"color": "black", "linewidth": 1.6},
    showfliers=False
)

# 3) Individual points ("rain")
sns.stripplot(
    data=phase_means_pd,
    x="Phase",
    y="Weight",
    order=PHASE_ORDER,
    jitter=0.12,
    size=8,
    color="#55A868",        # green points (high contrast)
    edgecolor="black",
    linewidth=0.6
)

# Labels
plt.xlabel("")
plt.ylabel("Mean Body Weight (g)")
plt.title("Body Weight – PD Rats Across Experimental Phases")

plt.tight_layout()
plt.savefig(
    f"{OUT_DIR}/Fig_PD_Weight_Raincloud_Pre_DBS_Post.png",
    dpi=600
)
plt.show()
