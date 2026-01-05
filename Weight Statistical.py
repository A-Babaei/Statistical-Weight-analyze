# ============================================================
# Longitudinal Body Weight Analysis – PD vs Control
# Final, cleaned, publication-ready
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
# STYLE & COLORS (Nature / color-blind safe)
# ============================================================

sns.set(style="whitegrid", context="talk")
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42

PD_COLOR = "#D55E00"   # vermillion
CO_COLOR = "#0072B2"   # blue
PHASE_ORDER = ["Pre-DBS", "DBS", "Post-DBS"]

# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_excel(DATA_PATH)
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

def phase_label(w):
    if w <= 4:
        return "Pre-DBS"
    elif w <= 8:
        return "DBS"
    else:
        return "Post-DBS"

df_long["Phase"] = df_long["WeekNum"].apply(phase_label)

# ============================================================
# PHASE MEANS PER SUBJECT
# ============================================================

phase_means = (
    df_long
    .groupby(["Subject", "Group", "Phase"])["Weight"]
    .mean()
    .reset_index()
)

# -------------------------
# Supplementary Table S1
# -------------------------
phase_means.to_csv(
    f"{OUT_DIR}/Table_S1_Weight_PhaseMeans.csv",
    index=False
)

# ============================================================
# SUBJECT-LEVEL DBS EFFECTS (PD)
# ============================================================

pd_data = phase_means[phase_means["Group"] == "PD"]

subject_table = (
    pd_data
    .pivot_table(index="Subject", columns="Phase", values="Weight")
    .reset_index()
)

subject_table["Delta_DBS_minus_Pre"] = subject_table["DBS"] - subject_table["Pre-DBS"]
subject_table["Percent_Change"] = (
    subject_table["Delta_DBS_minus_Pre"] / subject_table["Pre-DBS"]
) * 100

# -------------------------
# Supplementary Table S2
# -------------------------
subject_table.to_csv(
    f"{OUT_DIR}/Table_S2_PD_SubjectLevel_WeightEffects.csv",
    index=False
)

# ============================================================
# POST-HOC STATISTICS (PD, HOLM-CORRECTED)
# ============================================================

comparisons = [("Pre-DBS", "DBS"), ("DBS", "Post-DBS"), ("Pre-DBS", "Post-DBS")]
stats_rows = []
pvals = []

for a, b in comparisons:
    x = subject_table[a].values
    y = subject_table[b].values
    t, p = stats.ttest_rel(x, y)
    dz = (y - x).mean() / (y - x).std(ddof=1)
    stats_rows.append([a, b, t, p, dz])
    pvals.append(p)

# Holm correction
reject, pvals_corr, _, _ = multipletests(pvals, method="holm")

posthoc_df = pd.DataFrame(
    stats_rows,
    columns=["Phase1", "Phase2", "t_stat", "p_raw", "Cohens_dz"]
)
posthoc_df["p_holm"] = pvals_corr
posthoc_df["Significant"] = reject

# -------------------------
# Supplementary Table S3
# -------------------------
posthoc_df.to_csv(
    f"{OUT_DIR}/Table_S3_PD_Posthoc_HolmCorrected.csv",
    index=False
)

# ============================================================
# OPTIONAL: FRIEDMAN TEST (ROBUSTNESS)
# ============================================================

friedman_stat, friedman_p = stats.friedmanchisquare(
    subject_table["Pre-DBS"],
    subject_table["DBS"],
    subject_table["Post-DBS"]
)

print("\nFriedman test (PD): Chi² =", round(friedman_stat, 3), "p =", round(friedman_p, 4))

# ============================================================
# FIGURE 1 – WEIGHT TRAJECTORIES (CLEAN LEGEND)
# ============================================================

plt.figure(figsize=(9,6))

# Individual trajectories (no legend)
sns.lineplot(
    data=df_long,
    x="WeekNum",
    y="Weight",
    hue="Group",
    estimator=None,
    alpha=0.25,
    legend=False
)

# Mean trajectories (single legend)
sns.lineplot(
    data=df_long,
    x="WeekNum",
    y="Weight",
    hue="Group",
    linewidth=3,
    palette={"PD": PD_COLOR, "CO": CO_COLOR}
)

plt.axvspan(0.5, 4.5, alpha=0.1)
plt.axvspan(4.5, 8.5, alpha=0.2)
plt.axvspan(8.5, 12.5, alpha=0.1)

plt.xlabel("Week")
plt.ylabel("Body Weight (g)")
plt.title("Body Weight Trajectories Across Experimental Phases")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/Fig_Weight_Trajectories.png", dpi=600)
plt.show()

# ============================================================
# FIGURE 2 – RAINCLOUD-STYLE PHASE COMPARISON (CLEAN)
# ============================================================

plt.figure(figsize=(7,5))

# Violin
sns.violinplot(
    data=phase_means,
    x="Phase",
    y="Weight",
    hue="Group",
    order=PHASE_ORDER,
    palette=[CO_COLOR, PD_COLOR],
    inner=None,
    cut=0,
    dodge=True,
    linewidth=0,
    legend=False
)

# Box
sns.boxplot(
    data=phase_means,
    x="Phase",
    y="Weight",
    hue="Group",
    order=PHASE_ORDER,
    width=0.25,
    showcaps=True,
    boxprops={"facecolor": "none"},
    showfliers=False,
    dodge=True,
    legend=False
)

# Points (high contrast)
sns.stripplot(
    data=phase_means,
    x="Phase",
    y="Weight",
    hue="Group",
    order=PHASE_ORDER,
    dodge=True,
    jitter=0.12,
    size=6,
    palette=[CO_COLOR, PD_COLOR],
    edgecolor="black",
    linewidth=0.6,
    legend=False
)

# Paired lines
# for subj in phase_means["Subject"].unique():
  #  y = (
   #     phase_means[phase_means["Subject"] == subj]
    #    .set_index("Phase")
     #   .loc[PHASE_ORDER]["Weight"]
      #  .values
    #)
    #plt.plot([0,1,2], y, color="gray", alpha=0.4, linewidth=1)

# Single clean legend
handles = [
    plt.Line2D([0],[0], marker='o', color='w',
               markerfacecolor=CO_COLOR, markeredgecolor='black',
               markersize=8, label='Control'),
    plt.Line2D([0],[0], marker='o', color='w',
               markerfacecolor=PD_COLOR, markeredgecolor='black',
               markersize=8, label='PD')
]
plt.legend(handles=handles, title="Group")

plt.xlabel("")
plt.ylabel("Mean Body Weight (g)")
plt.title("Body Weight by Experimental Phase")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/Fig_Weight_Raincloud.png", dpi=600)
plt.show()

print("\nAll analyses, tables, and figures generated successfully.")

import matplotlib.pyplot as plt
import seaborn as sns

# Style
sns.set(style="whitegrid", context="talk")

plt.figure(figsize=(6,5))

# 1) Violin plot (distribution)
sns.violinplot(
    data=df_pd,
    x="Stimulation",
    y="SucrosePreference",
    order=["OFF", "ON"],
    inner=None,
    cut=0,
    linewidth=0,
    color="#4C72B0"   # blue tone like your figure
)

# 2) Boxplot inside violin
sns.boxplot(
    data=df_pd,
    x="Stimulation",
    y="SucrosePreference",
    order=["OFF", "ON"],
    width=0.25,
    showcaps=True,
    boxprops={"facecolor": "none", "edgecolor": "black", "linewidth": 1.4},
    whiskerprops={"linewidth": 1.4},
    medianprops={"color": "black", "linewidth": 1.6},
    showfliers=False
)

# 3) Individual points (high contrast)
sns.stripplot(
    data=df_pd,
    x="Stimulation",
    y="SucrosePreference",
    order=["OFF", "ON"],
    jitter=0.12,
    size=8,
    color="#55A868",     # green dots (high contrast)
    edgecolor="black",
    linewidth=0.6
)

# Labels
plt.xlabel("")
plt.ylabel("Sucrose Preference (%)")
plt.title("Sucrose Preference – PD Rats (DBS OFF vs ON)")

plt.tight_layout()
plt.savefig(f"{OUT_DIR}/Fig_PD_Raincloud_Final.png", dpi=600)
plt.show()
