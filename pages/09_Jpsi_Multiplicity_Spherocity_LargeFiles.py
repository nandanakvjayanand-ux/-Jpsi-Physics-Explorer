from pathlib import Path
import io
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="J/ψ yield vs transverse spherocity", layout="wide")

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "multiplicity_spherocity"
RESULTS_FILE = DATA / "spherocity_yield.csv"
SUMMARY_FILE = DATA / "sample_summary.csv"

st.title(r"$J/\psi$ yield vs transverse spherocity")
st.caption(
    r"Figure 9 · Mean number of $J/\psi$ candidates per selected event "
    r"as a function of transverse spherocity ($S_0$)"
)

# ---- Main, pre-analysed paper result ----
if not RESULTS_FILE.exists():
    st.error(f"Pre-analysed result file not found: {RESULTS_FILE}")
    st.stop()

df = pd.read_csv(RESULTS_FILE)
required = {"configuration", "mean_S0", "mean_NJpsi"}
missing = required.difference(df.columns)
if missing:
    st.error("The pre-analysed CSV is missing columns: " + ", ".join(sorted(missing)))
    st.stop()

df = df.dropna(subset=["mean_S0", "mean_NJpsi"]).copy()
df = df[(df["mean_S0"] >= 0) & (df["mean_S0"] <= 1)]
df = df.sort_values(["configuration", "mean_S0"])

STYLES = {
    "CR ON + MPI ON": {"color": "#111111", "symbol": "circle"},
    "CR OFF + MPI OFF": {"color": "#e31a1c", "symbol": "square"},
}

def make_figure(frame, title=None):
    fig = go.Figure()
    for config in ("CR ON + MPI ON", "CR OFF + MPI OFF"):
        part = frame[frame["configuration"] == config].sort_values("mean_S0")
        if part.empty:
            continue
        style = STYLES.get(config, {"color": "#2166ac", "symbol": "diamond"})
        custom = part["events"].to_numpy() if "events" in part.columns else None
        fig.add_trace(go.Scatter(
            x=part["mean_S0"],
            y=part["mean_NJpsi"],
            mode="lines+markers",
            name=config,
            line=dict(color=style["color"], width=1.8),
            marker=dict(
                color=style["color"], symbol=style["symbol"], size=8,
                line=dict(color=style["color"], width=1)
            ),
            customdata=custom,
            hovertemplate=(
                "S₀ = %{x:.3f}<br>"
                "Mean J/ψ candidates per selected event = %{y:.6g}<br>"
                "Events in bin = %{customdata:,.0f}"
                "<extra>%{fullData.name}</extra>"
            ) if custom is not None else (
                "S₀ = %{x:.3f}<br>"
                "Mean J/ψ candidates per selected event = %{y:.6g}"
                "<extra>%{fullData.name}</extra>"
            )
        ))

    fig.update_layout(
        template="plotly_white",
        title=title,
        height=590,
        autosize=True,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(family="Times New Roman, Times, serif", size=15, color="#111111"),
        margin=dict(l=100, r=35, t=65 if title else 35, b=85),
        legend=dict(
            title=None, orientation="h", x=0.02, y=1.02,
            xanchor="left", yanchor="bottom",
            bgcolor="rgba(255,255,255,0.9)",
            font=dict(color="#111111")
        ),
        hovermode="closest",
        dragmode="zoom",
        xaxis=dict(
            title=r"Transverse spherocity ($S_0$)",
            range=[0, 1], autorange=False,
            showline=True, mirror=True, linecolor="#111111",
            ticks="inside", tickcolor="#111111", tickfont=dict(color="#111111"),
            showgrid=True, gridcolor="#e5e5e5", zeroline=False,
            title_font=dict(color="#111111")
        ),
        yaxis=dict(
            title=r"Mean number of $J/\psi$ candidates per selected event",
            rangemode="tozero",
            showline=True, mirror=True, linecolor="#111111",
            ticks="inside", tickcolor="#111111", tickfont=dict(color="#111111"),
            showgrid=True, gridcolor="#e5e5e5", zeroline=False,
            title_font=dict(color="#111111")
        )
    )
    return fig

st.plotly_chart(
    make_figure(df),
    use_container_width=True,
    theme=None,
    config={
        "displaylogo": False,
        "scrollZoom": True,
        "modeBarButtonsToRemove": ["select2d", "lasso2d"],
        "toImageButtonOptions": {
            "format": "png",
            "filename": "jpsi_yield_vs_transverse_spherocity",
            "height": 700, "width": 1100, "scale": 2
        }
    }
)

if SUMMARY_FILE.exists():
    summary = pd.read_csv(SUMMARY_FILE)
    with st.expander("Pre-analysed sample statistics"):
        st.dataframe(summary, hide_index=True, use_container_width=True)

st.caption(
    "This is the pre-analysed Figure 9 result. Hover for values, use the legend to toggle "
    "configurations, zoom or pan, and export the graph using the toolbar."
)

# ---- Optional user exploration: one graph only ----
with st.expander("Explore with your own event-level dataset", expanded=False):
    st.write(
        "Upload one or two smaller event-level TXT/CSV files to calculate the same "
        "J/ψ-yield-versus-spherocity observable. Expected columns are EventID, Nch, S0, NJpsi "
        "followed optionally by additional pT columns. The original pre-analysed Figure 9 above "
        "remains unchanged."
    )
    st.warning(
        "For very large multi-GB datasets, do not use this browser uploader. "
        "It is intended for manageable files; process very large files locally in chunks first."
    )

    uploaded_on = st.file_uploader(
        "CR ON + MPI ON dataset (optional)",
        type=["txt", "csv"],
        key="user_on"
    )
    uploaded_off = st.file_uploader(
        "CR OFF + MPI OFF dataset (optional)",
        type=["txt", "csv"],
        key="user_off"
    )
    bins = st.selectbox("Spherocity bins", [10, 20, 25, 50], index=1, key="user_bins")

    def analyse_upload(upload, label, nbins):
        raw = pd.read_csv(
            io.BytesIO(upload.getvalue()),
            sep=r"\s+|,",
            engine="python",
            comment="#",
            header=None,
            usecols=[0, 1, 2, 3]
        )
        if raw.shape[1] < 4:
            raise ValueError(f"{upload.name}: expected at least four columns.")
        raw.columns = ["EventID", "Nch", "S0", "NJpsi"]
        for col in ("S0", "NJpsi"):
            raw[col] = pd.to_numeric(raw[col], errors="coerce")
        raw = raw.dropna(subset=["S0", "NJpsi"])
        raw = raw[(raw["S0"] >= 0) & (raw["S0"] <= 1)]
        edges = np.linspace(0, 1, nbins + 1)
        raw["s0_bin"] = pd.cut(raw["S0"], bins=edges, include_lowest=True, labels=False)
        grouped = raw.groupby("s0_bin", observed=False).agg(
            mean_S0=("S0", "mean"),
            mean_NJpsi=("NJpsi", "mean"),
            events=("NJpsi", "size")
        ).dropna().reset_index(drop=True)
        grouped["configuration"] = label
        return grouped[["configuration", "mean_S0", "mean_NJpsi", "events"]]

    if st.button("Generate my Figure 9 graph", type="primary"):
        if uploaded_on is None and uploaded_off is None:
            st.error("Upload at least one event-level dataset.")
        else:
            try:
                frames = []
                if uploaded_on is not None:
                    frames.append(analyse_upload(uploaded_on, "CR ON + MPI ON", int(bins)))
                if uploaded_off is not None:
                    frames.append(analyse_upload(uploaded_off, "CR OFF + MPI OFF", int(bins)))
                user_df = pd.concat(frames, ignore_index=True)
                st.subheader("Your interactive J/ψ-yield-versus-spherocity graph")
                st.plotly_chart(
                    make_figure(user_df),
                    use_container_width=True,
                    theme=None,
                    config={"displaylogo": False, "scrollZoom": True}
                )
                st.download_button(
                    "Download analysed points (CSV)",
                    user_df.to_csv(index=False).encode("utf-8"),
                    file_name="my_jpsi_yield_vs_spherocity.csv",
                    mime="text/csv"
                )
            except Exception as exc:
                st.error(f"Could not analyse the uploaded dataset: {exc}")
