
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

st.set_page_config(
    page_title="Charged-Particle Mean pT | J/ψ Physics Explorer",
    page_icon="⚛️",
    layout="wide"
)

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "mean_pt"

# ---------------------------------------------------------
# PAGE STYLE
# ---------------------------------------------------------

st.markdown("""
<style>
.stApp {
    background-color: #0b0f19;
    color: #e6eaf2;
}

.block-container {
    max-width: 1450px;
    padding-top: 2.5rem;
    padding-bottom: 4rem;
}

h1, h2, h3, p, label {
    color: #e6eaf2;
}

.hero-card {
    background: linear-gradient(120deg, #151e2e, #1b2639);
    border: 1px solid #34445f;
    border-radius: 14px;
    padding: 25px 30px;
    margin-bottom: 22px;
}

.hero-card p {
    color: #c4cede;
    font-size: 16px;
    line-height: 1.7;
}

.section-card {
    background: #151e2e;
    border: 1px solid #34445f;
    border-radius: 12px;
    padding: 18px 22px;
    margin-top: 28px;
    margin-bottom: 10px;
}

div[data-testid="stMetric"] {
    background: #151e2e;
    border: 1px solid #34445f;
    border-radius: 10px;
    padding: 15px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("Charged-Particle Mean Transverse Momentum")

st.markdown("""
<div class="hero-card">
<p>
<strong>Physics observable:</strong> Mean charged-particle transverse
momentum as a function of charged-particle multiplicity density.
</p>
<p>
<strong>Collision system:</strong> pp collisions at √s = 13 TeV<br>
<strong>Simulation:</strong> PYTHIA 8 — Colour Reconnection ON + MPI ON<br>
<strong>Experimental reference:</strong> ALICE
</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

panels = [
    ("Inclusive", "inclusive", "0–100%", [0.60, 0.90]),
    ("Jet-like", "jet_like", "0–10%", [0.60, 1.10]),
    ("Isotropic", "isotropic", "90–100%", [0.60, 0.90])
]

datasets = {}

try:
    for title, key, percentile, yrange in panels:
        datasets[key] = {
            "alice": pd.read_csv(
                DATA_DIR / f"{key}_alice.csv"
            ),
            "pythia": pd.read_csv(
                DATA_DIR / f"{key}_pythia.csv"
            )
        }

except FileNotFoundError as error:
    st.error(f"Missing numerical dataset: {error}")
    st.stop()

# ---------------------------------------------------------
# SUMMARY METRICS
# ---------------------------------------------------------

total_alice = sum(
    len(datasets[key]["alice"])
    for _, key, _, _ in panels
)

total_pythia = sum(
    len(datasets[key]["pythia"])
    for _, key, _, _ in panels
)

c1, c2, c3 = st.columns(3)

c1.metric("Spherocity classes", "3")
c2.metric("ALICE measurements", f"{total_alice:,}")
c3.metric("PYTHIA measurements", f"{total_pythia:,}")

st.divider()

# ---------------------------------------------------------

# ---------------------------------------------------------
# THREE INDIVIDUAL SCIENTIFIC GRAPHS
# ---------------------------------------------------------

st.header("ALICE–PYTHIA comparison")

st.caption(
    "Mean charged-particle transverse momentum versus multiplicity "
    "density for three transverse-spherocity classes."
)


def make_mean_pt_figure(alice, pythia, y_range, filename):

    fig = go.Figure()

    # ALICE systematic uncertainty
    fig.add_trace(
        go.Scatter(
            x=alice["dNch_deta"],
            y=alice["mean_pt"],
            mode="markers",
            name="ALICE systematic uncertainty",
            showlegend=False,
            marker=dict(
                size=0,
                color="rgba(0,0,0,0)"
            ),
            error_y=dict(
                type="data",
                array=alice["sys_error"],
                visible=True,
                color="rgba(214,39,40,0.38)",
                thickness=1.5,
                width=0
            ),
            hoverinfo="skip"
        )
    )

    # ALICE statistical uncertainty
    fig.add_trace(
        go.Scatter(
            x=alice["dNch_deta"],
            y=alice["mean_pt"],
            mode="markers",
            name="ALICE",
            marker=dict(
                symbol="circle",
                size=8,
                color="white",
                line=dict(
                    color="#C62828",
                    width=1.8
                )
            ),
            error_y=dict(
                type="data",
                array=alice["stat_error"],
                visible=True,
                color="#C62828",
                thickness=1.3,
                width=3
            ),
            customdata=np.column_stack([
                alice["stat_error"],
                alice["sys_error"]
            ]),
            hovertemplate=(
                "<b>ALICE</b><br>"
                "dNch/dη = %{x:.2f}<br>"
                "Mean pT = %{y:.5f} GeV/c<br>"
                "Statistical uncertainty = ±%{customdata[0]:.5f}<br>"
                "Systematic uncertainty = ±%{customdata[1]:.5f}"
                "<extra></extra>"
            )
        )
    )

    # PYTHIA
    fig.add_trace(
        go.Scatter(
            x=pythia["dNch_deta"],
            y=pythia["mean_pt"],
            mode="markers",
            name="PYTHIA 8 — CR + MPI ON",
            marker=dict(
                symbol="circle",
                size=7,
                color="black",
                line=dict(
                    color="black",
                    width=0.8
                )
            ),
            error_y=dict(
                type="data",
                array=pythia["stat_error"],
                visible=True,
                color="black",
                thickness=1.2,
                width=3
            ),
            customdata=pythia["stat_error"],
            hovertemplate=(
                "<b>PYTHIA 8 — CR + MPI ON</b><br>"
                "dNch/dη = %{x:.2f}<br>"
                "Mean pT = %{y:.5f} GeV/c<br>"
                "Statistical uncertainty = ±%{customdata:.5f}"
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(
        template="simple_white",
        height=440,
        autosize=True,
        paper_bgcolor="white",
        plot_bgcolor="white",

        font=dict(
            family="Times New Roman",
            size=14,
            color="#202020"
        ),

        margin=dict(
            l=95,
            r=35,
            t=85,
            b=85
        ),

        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=1.16,
            yanchor="top",
            font=dict(
                family="Times New Roman",
                size=13,
                color="#202020"
            ),
            bgcolor="rgba(255,255,255,0)",
            borderwidth=0,
            itemsizing="constant"
        ),

        hovermode="closest"
    )

    fig.update_xaxes(
        title_text="Charged-particle multiplicity density, dNch/dη",
        range=[10, 45],
        tickmode="array",
        tickvals=[10, 15, 20, 25, 30, 35, 40, 45],
        tickfont=dict(
            family="Times New Roman",
            size=13,
            color="#202020"
        ),
        title_font=dict(
            family="Times New Roman",
            size=15,
            color="#202020"
        ),
        showline=True,
        linewidth=1.2,
        linecolor="#333333",
        mirror=True,
        ticks="outside",
        ticklen=5,
        tickwidth=1,
        showgrid=False,
        zeroline=False,
        automargin=True
    )

    fig.update_yaxes(
        title_text="Mean transverse momentum, ⟨pT⟩ (GeV/c)",
        range=y_range,
        tickfont=dict(
            family="Times New Roman",
            size=13,
            color="#202020"
        ),
        title_font=dict(
            family="Times New Roman",
            size=15,
            color="#202020"
        ),
        showline=True,
        linewidth=1.2,
        linecolor="#333333",
        mirror=True,
        ticks="outside",
        ticklen=5,
        tickwidth=1,
        showgrid=True,
        gridcolor="#E8E8E8",
        gridwidth=0.7,
        zeroline=False,
        automargin=True
    )

    return fig


# ---------------------------------------------------------
# INCLUSIVE
# ---------------------------------------------------------

st.markdown("""
<div class="section-card">
<h3>01 &nbsp; Inclusive events</h3>
<p>Transverse-spherocity selection: 0–100%</p>
</div>
""", unsafe_allow_html=True)

fig_inclusive = make_mean_pt_figure(
    datasets["inclusive"]["alice"],
    datasets["inclusive"]["pythia"],
    [0.60, 0.90],
    "inclusive"
)

st.plotly_chart(
    fig_inclusive,
    use_container_width=True,
    config={
        "displayModeBar": True,
        "scrollZoom": True,
        "displaylogo": False,
        "responsive": True,
        "toImageButtonOptions": {
            "format": "png",
            "filename": "Mean_pT_Inclusive",
            "scale": 3
        }
    }
)

# ---------------------------------------------------------
# JET-LIKE
# ---------------------------------------------------------

st.markdown("""
<div class="section-card">
<h3>02 &nbsp; Jet-like events</h3>
<p>Transverse-spherocity selection: 0–10%</p>
</div>
""", unsafe_allow_html=True)

fig_jet = make_mean_pt_figure(
    datasets["jet_like"]["alice"],
    datasets["jet_like"]["pythia"],
    [0.60, 1.10],
    "jet_like"
)

st.plotly_chart(
    fig_jet,
    use_container_width=True,
    config={
        "displayModeBar": True,
        "scrollZoom": True,
        "displaylogo": False,
        "responsive": True,
        "toImageButtonOptions": {
            "format": "png",
            "filename": "Mean_pT_Jet_Like",
            "scale": 3
        }
    }
)

# ---------------------------------------------------------
# ISOTROPIC
# ---------------------------------------------------------

st.markdown("""
<div class="section-card">
<h3>03 &nbsp; Isotropic events</h3>
<p>Transverse-spherocity selection: 90–100%</p>
</div>
""", unsafe_allow_html=True)

fig_iso = make_mean_pt_figure(
    datasets["isotropic"]["alice"],
    datasets["isotropic"]["pythia"],
    [0.60, 0.90],
    "isotropic"
)

st.plotly_chart(
    fig_iso,
    use_container_width=True,
    config={
        "displayModeBar": True,
        "scrollZoom": True,
        "displaylogo": False,
        "responsive": True,
        "toImageButtonOptions": {
            "format": "png",
            "filename": "Mean_pT_Isotropic",
            "scale": 3
        }
    }
)

st.caption(
    "ALICE statistical uncertainties are shown with red error bars; "
    "systematic uncertainties are shown separately in lighter red. "
    "PYTHIA statistical uncertainties are shown in black."
)


# NUMERICAL DATA
# ---------------------------------------------------------

st.divider()
st.header("Numerical datasets")

for title, key, percentile, yrange in panels:

    with st.expander(f"{title} — {percentile}"):

        alice = datasets[key]["alice"]
        pythia = datasets[key]["pythia"]

        st.subheader("ALICE experimental data")
        st.dataframe(alice, use_container_width=True)

        st.download_button(
            f"Download ALICE — {title}",
            alice.to_csv(index=False),
            file_name=f"{key}_alice_mean_pt.csv",
            mime="text/csv",
            key=f"alice_{key}"
        )

        st.subheader("PYTHIA 8 — CR + MPI ON")
        st.dataframe(pythia, use_container_width=True)

        st.download_button(
            f"Download PYTHIA — {title}",
            pythia.to_csv(index=False),
            file_name=f"{key}_pythia_mean_pt.csv",
            mime="text/csv",
            key=f"pythia_{key}"
        )

st.divider()

st.caption(
    "ALICE statistical and systematic uncertainties are retained separately. "
    "PYTHIA statistical uncertainties are shown. "
    "The displayed multiplicity region follows the original analysis selection."
)
