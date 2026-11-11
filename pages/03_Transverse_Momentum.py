import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from io import StringIO

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Transverse Momentum | J/ψ Physics Explorer",
    page_icon="⚛️",
    layout="wide"
)

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "pt"
ALICE_DIR = DATA_DIR / "experimental"
PYTHIA_DIR = DATA_DIR / "pythia"

C_EMP_DEFAULT = 0.105
DY = 1.5

# =========================================================
# PAGE STYLE
# =========================================================

st.markdown("""
<style>
.stApp {
    background-color: #0b0f19;
    color: #e6eaf2;
}

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3, p, label {
    color: #e6eaf2;
}

div[data-testid="stMetric"] {
    background: #151e2e;
    border: 1px solid #34445f;
    border-radius: 10px;
    padding: 15px;
}

div[data-testid="stMetricLabel"] {
    color: #b7c4d9;
}

div[data-testid="stMetricValue"] {
    color: #ffffff;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================

st.title("Transverse Momentum Distribution")

st.markdown("""
Differential production cross-section of inclusive J/ψ mesons
in proton-proton collisions at √s = 13 TeV.
""")

st.markdown("""
**Forward rapidity:** 2.5 < y < 4.0

**Observable:** d²σ/(dpT dy)

**Empirical normalisation:** C_EMP = 0.105
""")

st.divider()

# =========================================================
# DATA INPUTS
# =========================================================

st.header("1. Experimental and simulation datasets")

st.caption(
    "Upload your own datasets to reproduce the comparison. "
    "Event-level PYTHIA files must contain pT and rapidity columns. "
    "The pre-binned CR-OFF file must contain pT centre, spectrum "
    "and statistical uncertainty."
)

with st.expander("Upload datasets", expanded=False):

    alice_upload = st.file_uploader(
        "ALICE experimental data (HEPData CSV)",
        type=["csv"],
        key="alice_file"
    )

    st.markdown("**CR ON + MPI ON — event-level samples**")

    cron_uploads = st.file_uploader(
        "Upload both CR ON files (600M and 200M)",
        type=["txt", "dat", "csv"],
        accept_multiple_files=True,
        key="cron_files"
    )

    st.markdown("**CR OFF + MPI OFF — simulation samples**")

    croff_event_upload = st.file_uploader(
        "CR OFF event-level sample (200M)",
        type=["txt", "dat", "csv"],
        key="croff_event"
    )

    croff_binned_upload = st.file_uploader(
        "CR OFF pre-binned sample (600M)",
        type=["txt", "dat", "csv"],
        key="croff_binned"
    )

# =========================================================
# NORMALISATION SETTINGS
# =========================================================

st.header("2. PYTHIA simulation")

with st.expander("Simulation settings", expanded=False):

    col1, col2 = st.columns(2)

    with col1:
        cron_events = st.number_input(
            "CR ON + MPI ON generated events",
            min_value=1,
            value=800_000_000,
            step=100_000_000
        )

        cron_sigma = st.number_input(
            "CR ON sigmaGen (mb)",
            min_value=0.001,
            value=3060.361,
            format="%.3f"
        )

    with col2:
        croff_events = st.number_input(
            "CR OFF + MPI OFF generated events",
            min_value=1,
            value=800_000_000,
            step=100_000_000
        )

        croff_sigma = st.number_input(
            "CR OFF sigmaGen (mb)",
            min_value=0.001,
            value=3060.523,
            format="%.3f"
        )

    c_emp = st.number_input(
        "Empirical normalisation factor",
        min_value=0.001,
        max_value=1.0,
        value=C_EMP_DEFAULT,
        step=0.001,
        format="%.3f"
    )

m1, m2, m3 = st.columns(3)

m1.metric("CR ON + MPI ON", f"{cron_events / 1e6:.0f}M events")
m2.metric("CR OFF + MPI OFF", f"{croff_events / 1e6:.0f}M events")
m3.metric("Empirical factor", f"{c_emp:.3f}")

# =========================================================
# ALICE DATA READER
# =========================================================

def read_alice(upload):

    if upload is not None:
        df = pd.read_csv(upload, skiprows=12)
    else:
        path = ALICE_DIR / "alice_pt.csv"

        if not path.exists():
            raise FileNotFoundError(
                "ALICE data not found. Upload the HEPData CSV."
            )

        df = pd.read_csv(path, skiprows=12)

    if len(df.columns) < 12:
        raise ValueError(
            "The ALICE file does not contain the expected HEPData columns."
        )

    out = pd.DataFrame({
        "pt": pd.to_numeric(df.iloc[:, 0], errors="coerce"),
        "low": pd.to_numeric(df.iloc[:, 1], errors="coerce"),
        "high": pd.to_numeric(df.iloc[:, 2], errors="coerce"),
        "value": pd.to_numeric(df.iloc[:, 3], errors="coerce"),
        "stat": pd.to_numeric(df.iloc[:, 4], errors="coerce").abs(),
        "sys": pd.to_numeric(df.iloc[:, 6], errors="coerce").abs(),
        "lumi": pd.to_numeric(df.iloc[:, 8], errors="coerce").abs(),
        "br": pd.to_numeric(df.iloc[:, 10], errors="coerce").abs()
    })

    out = out.dropna()

    out["error"] = np.sqrt(
        out["stat"]**2
        + out["sys"]**2
        + out["lumi"]**2
        + out["br"]**2
    )

    out = out[
        (out["low"] >= 0)
        & (out["high"] <= 8)
    ].copy()

    return out.sort_values("pt").reset_index(drop=True)


# =========================================================
# PYTHIA EVENT-LEVEL READER
# =========================================================

def read_event_file(upload, filename):

    if upload is not None:
        content = upload.getvalue().decode("utf-8")
        data = np.loadtxt(StringIO(content))
    else:
        path = PYTHIA_DIR / filename

        if not path.exists():
            raise FileNotFoundError(
                f"Missing {filename}. Upload the file above."
            )

        data = np.loadtxt(path)

    if data.ndim == 1:
        data = data.reshape(1, -1)

    if data.shape[1] < 2:
        raise ValueError(
            f"{filename} must contain pT and rapidity columns."
        )

    df = pd.DataFrame({
        "pt": data[:, 0],
        "y": data[:, 1]
    })

    return df[
        (df["y"] >= 2.5)
        & (df["y"] < 4.0)
        & (df["pt"] >= 0)
        & (df["pt"] < 8)
    ].copy()


# =========================================================
# CR ON COMBINED EVENT-LEVEL SPECTRUM
# =========================================================

def make_event_spectrum(
    dataframes,
    total_events,
    sigma_mb,
    c_emp
):

    edges = np.array([
        0, 0.5, 1, 2, 3, 4, 5, 6, 7, 8
    ])

    combined = pd.concat(dataframes, ignore_index=True)

    counts, _ = np.histogram(
        combined["pt"],
        bins=edges
    )

    widths = np.diff(edges)
    centres = (edges[:-1] + edges[1:]) / 2

    sigma_nb = sigma_mb * 1e6

    factor = (
        sigma_nb * c_emp
        / (total_events * widths * DY)
    )

    values = counts * factor
    errors = np.sqrt(counts) * factor

    return pd.DataFrame({
        "pt": centres,
        "value": values,
        "error": errors,
        "counts": counts
    })


# =========================================================
# CR OFF PRE-BINNED DATA READER
# =========================================================

def read_binned_croff(upload):

    if upload is not None:
        content = upload.getvalue().decode("utf-8")
        arr = np.loadtxt(StringIO(content))
    else:
        path = PYTHIA_DIR / "inclusive_jpsicroff_600MIL.txt"

        if not path.exists():
            raise FileNotFoundError(
                "CR OFF pre-binned file not found. Upload it above."
            )

        arr = np.loadtxt(path)

    if arr.ndim != 2 or arr.shape[1] < 3:
        raise ValueError(
            "The CR OFF pre-binned file must have three columns."
        )

    if len(arr) != 36:
        raise ValueError(
            "Expected 36 rows: three consecutive 12-bin spectra."
        )

    blocks = arr.reshape(3, 12, 3)

    centres = blocks[0, :, 0]
    values = blocks[:, :, 1].mean(axis=0)
    errors = np.sqrt(
        np.sum(blocks[:, :, 2]**2, axis=0)
    ) / 3.0

    result = pd.DataFrame({
        "pt": centres,
        "value": values,
        "error": errors
    })

    return result[
        (result["pt"] >= 0)
        & (result["pt"] < 8)
    ].copy()


# =========================================================
# PREPARE DATA
# =========================================================

try:

    alice = read_alice(alice_upload)

    if cron_uploads:

        if len(cron_uploads) != 2:
            raise ValueError(
                "Upload both CR ON event-level files: "
                "the 600M and 200M samples."
            )

        cron_frames = [
            read_event_file(file, file.name)
            for file in cron_uploads
        ]

    else:

        cron_frames = [
            read_event_file(
                None,
                "inclusive_jpsi_600M.txt"
            ),
            read_event_file(
                None,
                "inclusive_jpsi_cr1_108.txt"
            )
        ]

    cron = make_event_spectrum(
        cron_frames,
        cron_events,
        cron_sigma,
        c_emp
    )

    croff_event = read_event_file(
        croff_event_upload,
        "inclusive_jpsi_cr_off_101.txt"
    )

    croff_binned = read_binned_croff(
        croff_binned_upload
    )

except Exception as error:

    st.error(f"Data preparation error: {error}")
    st.stop()


# =========================================================
# FIGURE 4 — CLEAN TWO-PANEL PRESENTATION
# =========================================================

st.header("3. Differential cross-section")

st.caption(
    "Inclusive J/ψ differential cross-section as a function "
    "of transverse momentum."
)

fig = make_subplots(
    rows=1,
    cols=2,
    horizontal_spacing=0.16,
    subplot_titles=(
        "CR ON + MPI ON",
        "CR OFF + MPI OFF"
    )
)

# ---------------------------------------------------------
# LEFT PANEL: ALICE
# ---------------------------------------------------------

fig.add_trace(
    go.Scatter(
        x=alice["pt"],
        y=alice["value"],
        mode="markers",
        name="ALICE",
        legendgroup="ALICE",
        showlegend=True,
        marker=dict(
            symbol="diamond",
            size=10,
            color="white",
            line=dict(color="#D62728", width=2)
        ),
        error_y=dict(
            type="data",
            array=alice["error"],
            visible=True,
            color="#D62728",
            thickness=1.3,
            width=3
        ),
        customdata=np.column_stack([
            alice["low"],
            alice["high"],
            alice["error"]
        ]),
        hovertemplate=(
            "<b>ALICE</b><br>"
            "pT = %{x:.3f} GeV/c<br>"
            "Cross-section = %{y:.4g} nb/(GeV/c)<br>"
            "Bin = %{customdata[0]:.2f}–"
            "%{customdata[1]:.2f} GeV/c<br>"
            "Uncertainty = ±%{customdata[2]:.4g}"
            "<extra></extra>"
        )
    ),
    row=1,
    col=1
)

# ---------------------------------------------------------
# LEFT PANEL: PYTHIA CR ON
# ---------------------------------------------------------

fig.add_trace(
    go.Scatter(
        x=cron["pt"],
        y=cron["value"],
        mode="markers",
        name="PYTHIA 8 — CR ON + MPI ON",
        legendgroup="CRON",
        showlegend=True,
        marker=dict(
            symbol="circle",
            size=13,
            color="black",
            line=dict(color="black", width=1)
        ),
        error_y=dict(
            type="data",
            array=cron["error"],
            visible=True,
            color="black",
            thickness=1.3,
            width=3
        ),
        customdata=np.column_stack([
            cron["counts"],
            cron["error"]
        ]),
        hovertemplate=(
            "<b>PYTHIA 8 — CR ON + MPI ON</b><br>"
            "pT = %{x:.3f} GeV/c<br>"
            "Cross-section = %{y:.4g} nb/(GeV/c)<br>"
            "Accepted candidates = %{customdata[0]:.0f}<br>"
            "Statistical uncertainty = ±%{customdata[1]:.4g}"
            "<extra></extra>"
        )
    ),
    row=1,
    col=1
)

# ---------------------------------------------------------
# RIGHT PANEL: ALICE
# ---------------------------------------------------------

fig.add_trace(
    go.Scatter(
        x=alice["pt"],
        y=alice["value"],
        mode="markers",
        name="ALICE",
        legendgroup="ALICE",
        showlegend=False,
        marker=dict(
            symbol="diamond",
            size=10,
            color="white",
            line=dict(color="#D62728", width=2)
        ),
        error_y=dict(
            type="data",
            array=alice["error"],
            visible=True,
            color="#D62728",
            thickness=1.3,
            width=3
        ),
        customdata=np.column_stack([
            alice["low"],
            alice["high"],
            alice["error"]
        ]),
        hovertemplate=(
            "<b>ALICE</b><br>"
            "pT = %{x:.3f} GeV/c<br>"
            "Cross-section = %{y:.4g} nb/(GeV/c)<br>"
            "Bin = %{customdata[0]:.2f}–"
            "%{customdata[1]:.2f} GeV/c<br>"
            "Uncertainty = ±%{customdata[2]:.4g}"
            "<extra></extra>"
        )
    ),
    row=1,
    col=2
)

# ---------------------------------------------------------
# RIGHT PANEL: PYTHIA CR OFF
# ---------------------------------------------------------

fig.add_trace(
    go.Scatter(
        x=croff_binned["pt"],
        y=croff_binned["value"],
        mode="markers",
        name="PYTHIA 8 — CR OFF + MPI OFF",
        legendgroup="CROFF",
        showlegend=True,
        marker=dict(
            symbol="square",
            size=13,
            color="black",
            line=dict(color="black", width=1)
        ),
        error_y=dict(
            type="data",
            array=croff_binned["error"],
            visible=True,
            color="black",
            thickness=1.3,
            width=3
        ),
        customdata=np.column_stack([
            croff_binned["error"]
        ]),
        hovertemplate=(
            "<b>PYTHIA 8 — CR OFF + MPI OFF</b><br>"
            "pT = %{x:.3f} GeV/c<br>"
            "Spectrum value = %{y:.4g}<br>"
            "Quoted statistical uncertainty = "
            "±%{customdata[0]:.4g}"
            "<extra></extra>"
        )
    ),
    row=1,
    col=2
)

# =========================================================

# =========================================================
# PUBLICATION-STYLE AXIS AND LAYOUT FORMATTING
# =========================================================

fig.update_layout(
    template="simple_white",
    height=650,
    autosize=True,

    paper_bgcolor="white",
    plot_bgcolor="white",

    font=dict(
        family="Times New Roman",
        size=16,
        color="black"
    ),

    margin=dict(
        l=105,
        r=45,
        t=125,
        b=95
    ),

    legend=dict(
        orientation="h",
        x=0.5,
        xanchor="center",
        y=1.13,
        yanchor="bottom",
        font=dict(
            family="Times New Roman",
            size=15,
            color="black"
        ),
        bgcolor="rgba(255,255,255,0)",
        borderwidth=0,
        itemsizing="constant",
        tracegroupgap=12
    ),

    hovermode="closest"
)

# PANEL TITLES
fig.update_annotations(
    y=1.025,
    font=dict(
        family="Times New Roman",
        size=19,
        color="black"
    )
)

# X AXES
for col in (1, 2):
    fig.update_xaxes(
        title_text=r"$p_T$ (GeV/$c$)",
        range=[0, 8],
        tickmode="array",
        tickvals=[0, 2, 4, 6, 8],
        ticktext=["0", "2", "4", "6", "8"],

        tickfont=dict(
            family="Times New Roman",
            size=16,
            color="black"
        ),
        title_font=dict(
            family="Times New Roman",
            size=18,
            color="black"
        ),
        title_standoff=15,

        showline=True,
        linewidth=1.4,
        linecolor="black",
        mirror=True,

        ticks="inside",
        ticklen=7,
        tickwidth=1.3,

        minor=dict(
            ticks="inside",
            ticklen=3,
            tickwidth=0.9,
            showgrid=False
        ),

        showgrid=False,
        zeroline=False,
        automargin=True,
        row=1,
        col=col
    )

# LEFT Y AXIS
fig.update_yaxes(
    title_text=r"$d^2\\sigma/(dp_T\\,dy)$ [nb/(GeV/$c$)]",
    type="log",
    range=[0, 4],
    tickmode="array",
    tickvals=[1, 10, 100, 1000, 10000],
    ticktext=["1", "10", "100", "1,000", "10,000"],

    tickfont=dict(
        family="Times New Roman",
        size=15,
        color="black"
    ),
    title_font=dict(
        family="Times New Roman",
        size=17,
        color="black"
    ),
    title_standoff=18,

    showline=True,
    linewidth=1.4,
    linecolor="black",
    mirror=True,

    ticks="inside",
    ticklen=7,
    tickwidth=1.3,

    minor=dict(
        ticks="inside",
        ticklen=3,
        tickwidth=0.9,
        showgrid=False
    ),

    showgrid=False,
    zeroline=False,
    automargin=True,
    row=1,
    col=1
)

# RIGHT Y AXIS
fig.update_yaxes(
    title_text="",
    type="log",
    range=[0, 4],
    tickmode="array",
    tickvals=[1, 10, 100, 1000, 10000],
    ticktext=["1", "10", "100", "1,000", "10,000"],

    tickfont=dict(
        family="Times New Roman",
        size=15,
        color="black"
    ),

    showline=True,
    linewidth=1.4,
    linecolor="black",
    mirror=True,

    ticks="inside",
    ticklen=7,
    tickwidth=1.3,

    minor=dict(
        ticks="inside",
        ticklen=3,
        tickwidth=0.9,
        showgrid=False
    ),

    showgrid=False,
    zeroline=False,
    automargin=True,
    row=1,
    col=2
)

# DISPLAY INTERACTIVE FIGURE
# =========================================================

st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displayModeBar": True,
        "scrollZoom": True,
        "displaylogo": False,
        "responsive": True,
        "toImageButtonOptions": {
            "format": "png",
            "filename": "Jpsi_Figure4_Transverse_Momentum",
            "scale": 3
        }
    }
)

st.caption(
    "Hover over any measurement to inspect its numerical value "
    "and uncertainty. Zoom, pan and export the figure using "
    "the interactive toolbar."
)

# =========================================================
# NUMERICAL DATA
# =========================================================

with st.expander("View numerical datasets"):

    st.subheader("ALICE experimental data")
    st.dataframe(alice, use_container_width=True)

    st.subheader("PYTHIA — CR ON + MPI ON")
    st.dataframe(cron, use_container_width=True)

    st.subheader("PYTHIA — CR OFF + MPI OFF (pre-binned)")
    st.dataframe(croff_binned, use_container_width=True)

    st.subheader("CR OFF event-level sample")

    st.write(
        f"Accepted event-level candidates in selected region: "
        f"{len(croff_event):,}"
    )

    st.download_button(
        "Download ALICE data",
        alice.to_csv(index=False),
        file_name="alice_pt_processed.csv",
        mime="text/csv"
    )

    st.download_button(
        "Download CR ON spectrum",
        cron.to_csv(index=False),
        file_name="pythia_cron_pt.csv",
        mime="text/csv"
    )

    st.download_button(
        "Download CR OFF pre-binned spectrum",
        croff_binned.to_csv(index=False),
        file_name="pythia_croff_binned_pt.csv",
        mime="text/csv"
    )

