# 📗 README — Body Weight Analysis Code

## **Project**

**Longitudinal physiological recovery following parafascicular deep brain stimulation**

**Author:** A. Babaei
**Program:** M.Sc. Bioelectrical Engineering
**Associated Manuscript:** Targeting a thalamic control node for Parkinson’s disease therapy

---

## **Overview**

This repository contains Python code for the **longitudinal analysis of body weight**, used as a physiological indicator of disease burden and recovery in a hemiparkinsonian rat model.

Body weight is analyzed as a **non-motor physiological outcome**, complementing behavioral assays such as the EPM and sucrose preference test.

The code:

* Implements **phase-based longitudinal analysis**
* Quantifies **DBS-associated recovery**
* Provides **effect sizes and corrected statistics**
* Generates **clear, publication-quality visualizations**

---

## **Input Data**

### Required file

```
Weight_Statistical_analyze_Transposed.xlsx
```

### Data structure

* **Rows:** Individual animals

  * First 9: PD
  * Next 9: Control
* **Columns:** Weekly body weight measurements:

  * Week_1 … Week_12

---

## **Experimental Phases**

The analysis aggregates weekly data into biologically meaningful phases:

* **Pre-DBS:** Weeks 1–4 (lesion development)
* **DBS:** Weeks 5–8 (stimulation ON)
* **Post-DBS:** Weeks 9–12 (after stimulation)

Mean body weight per subject is computed for each phase.

---

## **Statistical Analysis**

### Design

* **Within-subject:** Phase comparisons (Pre-DBS vs DBS vs Post-DBS)
* **Between-subject:** PD vs Control

### Tests

* Paired comparisons within PD group
* **Holm–Bonferroni correction** for multiple phase comparisons
* **Effect size:** Cohen’s *dz*

### Focus

* Reversal of lesion-associated weight loss
* Stability of recovery after DBS cessation
* Comparison with physiological growth in controls

---

## **Outputs**

### Supplementary Tables

* **S1:** Phase-wise mean body weight (all subjects)
* **S2:** Subject-level DBS weight effects (Δ and % change)
* **S3:** Holm-corrected phase comparisons with effect sizes

### Figures

* Longitudinal trajectory plot (12 weeks)
* Raincloud-style phase comparison (PD vs Control)

All figures are saved at **600 dpi**.

---

## **How to Run**

1. Update paths in the script:

```python
DATA_PATH = r"G:\...\Weight_Statistical_analyze_Transposed.xlsx"
OUT_DIR   = r"G:\...\Weight_Results"
```

2. Run:

```bash
python Weight_Longitudinal_Analysis_FINAL.py
```

---

## **Interpretation Notes**

* Body weight is treated as an **integrative physiological marker**, not a motor endpoint.
* DBS-induced weight recovery is interpreted as normalization of disease-associated systemic decline.
* Sustained post-DBS effects support a **network-level therapeutic mechanism**.

---

## **Citation**

If you use or adapt this code, please cite or acknowledge:

> Babaei, A. Bioelectrical Engineering. Longitudinal physiological effects of parafascicular deep brain stimulation in Parkinsonian rats.
