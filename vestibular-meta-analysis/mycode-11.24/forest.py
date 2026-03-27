# ==================
# 2. FOREST PLOTS
# ==================
# pip install forestplot matplotlib pandas

import pandas as pd
from forestplot import forestplot
import matplotlib.pyplot as plt
from pathlib import Path

input_file = r"C:\PATH\TO\all_meta_rows.csv"     # <---- CHANGE
output_dir = Path(r"C:\PATH\TO\output\forest")   # <---- CHANGE
output_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(input_file)

# Clean + compute basic stuff
df["Etiology"] = df["Etiology"].str.lower()
df["Side"] = df["Side"].astype(str)

# simple inverse-variance weights
df["weight_raw"] = 1.0 / df["Hedges_g_variance"]
df = df[df["Hedges_g_variance"].notna()]

# normalize weights WITHIN each etiology
df["weight_pct"] = (
    df.groupby("Etiology")["weight_raw"]
      .transform(lambda x: x / x.sum() * 100.0)
)

# build study label like 2014-Husain.1
df["Author_clean"] = df["Author"].astype(str).str.split().str[0].str.replace(",", "", regex=False)
df["StudyBase"] = df["Year"].astype(str) + "-" + df["Author_clean"]
df["Study"] = df.groupby("StudyBase").cumcount().add(1)
df["Study"] = df["StudyBase"] + "." + df["Study"].astype(str)

# which etiologies to plot
etiologies = sorted(df["Etiology"].dropna().unique())

separator_row = {
    "Study": " ",
    "ROI": " ",
    "Big Area": " ",
    "N": " ",
    "Est (95% CI)": " ",
    "Weight (%)": " ",
    "Effect": None,
    "CI Lower": None,
    "CI Upper": None,
}

for et in etiologies:
    sub = df[df["Etiology"] == et].copy()
    if sub.empty:
        continue

    # left & right
    left  = sub[sub["Side"] == "L"].copy()
    right = sub[sub["Side"] == "R"].copy()

    left  = left.sort_values("Hedges_g_exact", ascending=False)
    right = right.sort_values("Hedges_g_exact", ascending=False)

    def to_table(part):
        return pd.DataFrame({
            "Study": part["Study"],
            "ROI": part["ROI_Homogenized"],
            "Big Area": part["Big_Area"],
            "N": part["Sample_Size_Patients"],
            "Est (95% CI)": (
                part["Hedges_g_exact"].map("{:.2f}".format) + " [" +
                part["CI_lower"].map("{:.2f}".format) + ", " +
                part["CI_upper"].map("{:.2f}".format) + "]"
            ),
            "Weight (%)": part["weight_pct"].map("{:.2f}".format),
            "Effect": part["Hedges_g_exact"],
            "CI Lower": part["CI_lower"],
            "CI Upper": part["CI_upper"],
        })

    data_left = to_table(left)
    data_right = to_table(right)

    combined = pd.concat(
        [data_right, pd.DataFrame([separator_row]), data_left],
        ignore_index=True
    )

    fig = forestplot(
        combined,
        estimate="Effect",
        ll="CI Lower",
        hl="CI Upper",
        varlabel="Study",
        annote=["ROI", "Big Area", "N", "Est (95% CI)"],
        annoteheaders=["ROI", "Big Area", "N", "Est (95% CI)"],
        rightannote=["Weight (%)"],
        right_annoteheaders=["Weight (%)"],
        xlabel="Hedges g",
        table=True,
        figsize=(12, 0.35 * len(combined)),
        align="center",
        fontsize=9,
    )

    fig.set_title(f"Forest Plot ({et})")
    fig.get_figure().tight_layout()

    out_svg = output_dir / f"forest_{et}.svg"
    out_png = output_dir / f"forest_{et}.png"
    fig.get_figure().savefig(out_svg, bbox_inches="tight")
    fig.get_figure().savefig(out_png, dpi=300, bbox_inches="tight")
    plt.close(fig.get_figure())
