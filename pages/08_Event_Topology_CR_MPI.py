from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Forward J/ψ pT by event topology", layout="wide")
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "topology"

st.title("Forward-rapidity J/ψ transverse-momentum distributions")
st.caption(r"$pp,\ \sqrt{s}=13\ \mathrm{TeV},\quad 2.5<|y|<4.0$")

st.info(
    "These files contain event-level (pT, y) pairs but do not provide generated-event totals "
    "or per-run σgen. The spectra are therefore unit-area, shape-normalised pT densities, "
    "not absolute cross sections or per-event yields. Their numerical scale will consequently "
    "differ from the cross-section-normalised spectra in the paper."
)

@st.cache_data
def load_sample(topology, config):
    arrays = []
    for seed in (103, 104):
        path = DATA / f"{topology}_cr_{config}_{seed}.txt"
        if not path.exists():
            raise FileNotFoundError(f"Missing data file: {path}")
        a = np.loadtxt(path, dtype=float, ndmin=2)
        if a.shape[1] < 2:
            raise ValueError(f"{path.name} must have two columns: pT and y.")
        a = a[:, :2]
        a = a[np.isfinite(a).all(axis=1)]
        arrays.append(a)
    return np.vstack(arrays)

st.sidebar.header("Kinematic selections")
pt_min = st.sidebar.number_input("Minimum pT (GeV/c)", 0.0, 9.0, 0.0, 0.5)
pt_max = st.sidebar.number_input("Maximum pT (GeV/c)", 1.0, 30.0, 10.0, 1.0)
bin_width = st.sidebar.selectbox("pT bin width (GeV/c)", [0.25, 0.5, 1.0], index=2)
y_min = st.sidebar.number_input("Minimum |y|", 0.0, 5.0, 2.5, 0.1)
y_max = st.sidebar.number_input("Maximum |y|", 0.1, 6.0, 4.0, 0.1)

if pt_max <= pt_min or y_max <= y_min:
    st.error("The upper limits must be greater than the lower limits.")
    st.stop()

edges = np.arange(pt_min, pt_max, float(bin_width))
edges = np.unique(np.append(edges, pt_max))
centres = (edges[:-1] + edges[1:]) / 2
widths = np.diff(edges)

# Match the paper's compact two-column/two-row composition.
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "font.size": 9,
    "axes.labelsize": 10,
    "axes.titlesize": 10,
    "legend.fontsize": 8,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "axes.linewidth": 0.8,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.top": True,
    "ytick.right": True,
})

fig, ax = plt.subplots(
    2, 2, figsize=(10.2, 6.2), sharex="col",
    gridspec_kw={"height_ratios": [3.0, 1.0], "hspace": 0.08, "wspace": 0.18}
)

styles = {
    "integrated": {"label": r"$S_0$ integrated", "color": "black", "marker": "o", "mfc": "white"},
    "jetty": {"label": "Jetty", "color": "red", "marker": "^", "mfc": "red"},
    "isotropic": {"label": "Isotropic", "color": "black", "marker": "v", "mfc": "black"},
}
summary = []

for col, (config, panel_title) in enumerate([
    ("on", r"(a) CR+MPI ON, $2.5<|y|<4.0$"),
    ("off", r"(b) CR+MPI OFF, $2.5<|y|<4.0$")
]):
    spectra = {}
    for topology in ("integrated", "jetty", "isotropic"):
        data = load_sample(topology, config)
        pt, rapidity = data[:, 0], np.abs(data[:, 1])
        mask = (
            (pt >= pt_min) & (pt <= pt_max) &
            (rapidity >= y_min) & (rapidity < y_max)
        )
        selected = pt[mask]
        counts, _ = np.histogram(selected, bins=edges)
        n = int(counts.sum())
        density = counts / (n * widths) if n else np.zeros(len(widths))
        error = np.sqrt(counts) / (n * widths) if n else np.zeros(len(widths))
        spectra[topology] = (density, error, counts, n)
        summary.append({
            "Configuration": panel_title,
            "Event class": styles[topology]["label"],
            "Selected entries": n,
            "Combined input pairs": len(data),
        })

        s = styles[topology]
        positive = density > 0
        ax[0, col].errorbar(
            centres[positive], density[positive], yerr=error[positive],
            color=s["color"], marker=s["marker"], markerfacecolor=s["mfc"],
            markeredgecolor=s["color"], markersize=5, linewidth=0.8,
            elinewidth=0.7, capsize=0, linestyle="-", label=s["label"]
        )

    base, base_err, _, _ = spectra["integrated"]
    for topology in ("jetty", "isotropic"):
        density, error, _, _ = spectra[topology]
        valid = (base > 0) & (density > 0)
        ratio = np.full_like(base, np.nan, dtype=float)
        ratio_err = np.full_like(base, np.nan, dtype=float)
        ratio[valid] = density[valid] / base[valid]
        rel_a = np.divide(error, density, out=np.zeros_like(error), where=density > 0)
        rel_b = np.divide(base_err, base, out=np.zeros_like(base_err), where=base > 0)
        ratio_err[valid] = ratio[valid] * np.sqrt(rel_a[valid]**2 + rel_b[valid]**2)
        s = styles[topology]
        ax[1, col].errorbar(
            centres[valid], ratio[valid], yerr=ratio_err[valid],
            color=s["color"], marker=s["marker"], markerfacecolor=s["mfc"],
            markeredgecolor=s["color"], markersize=4.5, linewidth=0.7,
            elinewidth=0.65, capsize=0, linestyle="none", label=s["label"]
        )

    ax[0, col].set_title(panel_title, pad=7)
    ax[0, col].set_yscale("log")
    # Use the actual populated density range rather than forcing a cross-section
    # scale that is not supported by these unit-area input distributions.
    positive_values = np.concatenate([
        spectra[k][0][spectra[k][0] > 0] for k in spectra
    ])
    if len(positive_values):
        lo = max(positive_values.min() * 0.35, 1e-6)
        hi = positive_values.max() * 2.0
        ax[0, col].set_ylim(lo, hi)
    ax[0, col].legend(frameon=False, loc="upper right", handlelength=1.5, borderpad=0.2, labelspacing=0.25)
    ax[1, col].axhline(1.0, color="black", linestyle="--", linewidth=0.7)
    ax[1, col].set_ylim(0, 4)
    ax[1, col].set_yticks([0, 2, 4])
    for row in (0, 1):
        ax[row, col].set_xlim(pt_min, pt_max)
        ax[row, col].tick_params(which="both", direction="in", top=True, right=True, length=3)
        ax[row, col].spines["top"].set_visible(True)
        ax[row, col].spines["right"].set_visible(True)

    ax[1, col].set_xlabel(r"$p_T$ [GeV/$c$]")

ax[0, 0].set_ylabel(r"Shape-normalised $\mathrm{d}P/\mathrm{d}p_T$ [$(\mathrm{GeV}/c)^{-1}$]")
ax[1, 0].set_ylabel(r"Ratio to $S_0$ integrated")
ax[1, 1].set_ylabel("")
ax[0, 1].set_ylabel("")
fig.align_ylabels()
fig.subplots_adjust(left=0.105, right=0.985, top=0.92, bottom=0.11)

st.pyplot(fig, use_container_width=True)
plt.close(fig)

st.caption(
    "The lower panels show jetty and isotropic spectra divided bin-by-bin by the "
    "$S_0$-integrated spectrum in the same generator configuration. The dashed line marks unity."
)
st.subheader("Selected sample statistics")
stats = pd.DataFrame(summary)
st.dataframe(stats, hide_index=True, use_container_width=True)
st.download_button(
    "Download sample statistics (CSV)",
    stats.to_csv(index=False).encode("utf-8"),
    file_name="forward_jpsi_topology_statistics.csv",
    mime="text/csv"
)
