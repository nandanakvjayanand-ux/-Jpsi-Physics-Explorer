from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

st.set_page_config(
    page_title="Spherocity: CR ON vs CR OFF",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
<style>
.block-container {max-width: 1450px; padding-top: 1.5rem; padding-bottom: 3rem;}
h1,h2,h3,p,label,div,span {font-family: "Times New Roman", serif;}
</style>
""", unsafe_allow_html=True)

st.title("Transverse Spherocity: Colour Reconnection ON vs OFF")
st.markdown(r"### $pp$ collisions at $\sqrt{s}=13$ TeV")
st.write(
    "Interactive comparison of the original research distributions. "
    "Explore the five charged-particle multiplicity intervals and compare "
    "the effects of colour reconnection."
)

# ---------------------------------------------------------------------
# INPUT FILES
# CR ON: the original 400M event-level file.
# CR OFF: combine the four original MPI-off samples.
# Deliberately do NOT use spherocity_fig4_13tev_CROFF_400MIL.txt.
# ---------------------------------------------------------------------
HOME = Path.home()
SEARCH_DIRS = [
    HOME / "Downloads",
    HOME / "Downloads" / "pythia8317" / "examples",
    HOME / "Desktop" / "WEB-APP SIMLATION FILE ",
    HOME / "Desktop" / "simulation file ",
]

def locate_file(filename):
    for folder in SEARCH_DIRS:
        candidate = folder / filename
        if candidate.is_file():
            return candidate
    return None

cr_on_candidates = [
    "spherocity_fig4_13tev_CRON_400MIL.txt",
    "spherocity_fig4_13tev_CRON_400MIL.txt.gz",
]

cr_on_file = next((locate_file(n) for n in cr_on_candidates if locate_file(n)), None)

cr_off_names = [
    "spherocity_fig4_13tev_mpi0ff_102.txt",
    "spherocity_fig4_13tev_mpi0ff_105.txt",
    "spherocity_fig4_13tev_mpi0ff_109.txt",
    "spherocity_fig4_13tev_mpi0ff_110.txt",
]

cr_off_files = []
missing_off = []
for name in cr_off_names:
    found = locate_file(name)
    if found is None:
        found = locate_file(name + ".gz")
    if found is None:
        missing_off.append(name + " (or .gz)")
    else:
        cr_off_files.append(found)

# Keep local file paths private: the page reports only whether the research
# datasets are available, never their machine-specific locations.
if cr_on_file is None or missing_off:
    st.error(
        "The research datasets could not all be found. Use the optional upload "
        "section at the bottom of this page, or restore the original datasets."
    )
    st.stop()

# Explicit safeguard against accidentally selecting the unwanted file.
if cr_on_file.name == "spherocity_fig4_13tev_CROFF_400MIL.txt":
    st.error("Incorrect CR ON input selected. Stopping to prevent a false comparison.")
    st.stop()
if any(f.name == "spherocity_fig4_13tev_CROFF_400MIL.txt" for f in cr_off_files):
    st.error("The unwanted CROFF_400MIL file was selected. Stopping.")
    st.stop()

# Five multiplicity intervals shown in the user's reference figures.
CLASSES = [
    ("5 ≤ Nch < 10", 5, 10),
    ("10 ≤ Nch < 15", 10, 15),
    ("20 ≤ Nch < 25", 20, 25),
    ("25 ≤ Nch < 30", 25, 30),
    ("30 ≤ Nch < 150", 30, 150),
]

BINS = np.linspace(0.0, 1.0, 101)
CENTRES = 0.5 * (BINS[:-1] + BINS[1:])

def empty_histograms():
    return (
        {label: np.zeros(100, dtype=np.int64) for label, _, _ in CLASSES},
        {label: 0 for label, _, _ in CLASSES},
        0,
    )

@st.cache_data(show_spinner=False)
def process_one_file(path_string, file_size, modified_time):
    """Stream one two-column Nch, S0 file and return per-class histograms."""
    counts, totals, rows_read = empty_histograms()
    for chunk in pd.read_csv(
        path_string,
        sep=r"\s+",
        header=None,
        comment="#",
        usecols=[0, 1],
        names=["Nch", "S0"],
        chunksize=1_000_000,
        engine="c",
        compression="infer",
        on_bad_lines="skip",
    ):
        nch = pd.to_numeric(chunk["Nch"], errors="coerce").to_numpy()
        s0 = pd.to_numeric(chunk["S0"], errors="coerce").to_numpy()
        valid = np.isfinite(nch) & np.isfinite(s0) & (nch >= 0) & (s0 >= 0) & (s0 <= 1)
        nch = nch[valid]
        s0 = s0[valid]
        rows_read += len(nch)

        for label, low, high in CLASSES:
            selected = (nch >= low) & (nch < high)
            counts[label] += np.histogram(s0[selected], bins=BINS)[0]
            totals[label] += int(np.count_nonzero(selected))

    return counts, totals, rows_read

def process_file_list(files, label):
    combined_counts, combined_totals, combined_rows = empty_histograms()
    progress = st.progress(0, text=f"Processing {label}…")
    for index, file_path in enumerate(files, start=1):
        stat = file_path.stat()
        with st.spinner(f"{label}: processing {file_path.name} ({index}/{len(files)})"):
            counts, totals, rows = process_one_file(
                str(file_path), stat.st_size, stat.st_mtime
            )
        for class_label, _, _ in CLASSES:
            combined_counts[class_label] += counts[class_label]
            combined_totals[class_label] += totals[class_label]
        combined_rows += rows
        progress.progress(index / len(files), text=f"{label}: processed {index}/{len(files)} files")
    progress.empty()
    return combined_counts, combined_totals, combined_rows

with st.spinner("Reading the original CR ON event sample…"):
    on_counts, on_totals, on_rows = process_file_list([cr_on_file], "CR ON")

off_counts, off_totals, off_rows = process_file_list(cr_off_files, "CR OFF (four-file combination)")

st.success("Original CR ON sample and combined four-file CR OFF sample processed.")

m1, m2, m3 = st.columns(3)
m1.metric("CR ON rows read", f"{on_rows:,}")
m2.metric("CR OFF rows read (4 files)", f"{off_rows:,}")
m3.metric("CR OFF files combined", "4")

st.caption(
    r"Per-bin probability: $P(S_0)=N_{\rm bin}/N_{\rm class}$. "
    r"Poisson uncertainty: $\sigma_P=\sqrt{N_{\rm bin}}/N_{\rm class}$. "
    "Each configuration is normalised independently within each multiplicity interval."
)

layout_choice = st.radio(
    "Graph layout",
    ["All five intervals", "Choose one interval"],
    horizontal=True,
)
if layout_choice == "Choose one interval":
    selected = st.selectbox("Multiplicity interval", [item[0] for item in CLASSES])
    shown_classes = [item for item in CLASSES if item[0] == selected]
else:
    shown_classes = CLASSES

fig = make_subplots(
    rows=len(shown_classes),
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.055 if len(shown_classes) > 1 else 0,
    subplot_titles=[item[0] for item in shown_classes] if len(shown_classes) > 1 else None,
)

# Draw red squares first and black circles second, as in the reference plots.
# Both use the exact same S0 bin centres: no artificial x displacement.
for row, (label, low, high) in enumerate(shown_classes, start=1):
    for cfg, counts_map, totals_map, colour, symbol in [
        ("CR OFF", off_counts, off_totals, "#e60000", "square"),
        ("CR ON", on_counts, on_totals, "#000000", "circle"),
    ]:
        n_class = totals_map[label]
        bin_counts = counts_map[label]
        if n_class:
            probability = bin_counts / n_class
            uncertainty = np.sqrt(bin_counts) / n_class
        else:
            probability = np.zeros(100)
            uncertainty = np.zeros(100)

        fig.add_trace(
            go.Scatter(
                x=CENTRES,
                y=probability,
                mode="markers",
                name=cfg,
                legendgroup=cfg,
                showlegend=(row == 1),
                marker=dict(
                    symbol=symbol,
                    size=8,
                    color="white",
                    line=dict(color=colour, width=2),
                ),
                error_y=dict(
                    type="data",
                    array=uncertainty,
                    visible=True,
                    color=colour,
                    thickness=1.25,
                    width=3,
                ),
                customdata=np.column_stack((bin_counts, np.full(100, n_class), uncertainty)),
                hovertemplate=(
                    "S₀ = %{x:.2f}<br>"
                    "P(S₀) = %{y:.5f}<br>"
                    "Bin entries = %{customdata[0]:,.0f}<br>"
                    "Class events = %{customdata[1]:,.0f}<br>"
                    "Poisson uncertainty = %{customdata[2]:.5f}"
                    f"<extra>{cfg}</extra>"
                ),
            ),
            row=row,
            col=1,
        )

    fig.add_annotation(
        x=0.985,
        y=0.97,
        xref="x domain" if row == 1 else f"x{row} domain",
        yref="y domain" if row == 1 else f"y{row} domain",
        text=(
            f"N(CR ON) = {on_totals[label]:,}"
            f"<br>N(CR OFF) = {off_totals[label]:,}"
        ),
        showarrow=False,
        xanchor="right",
        yanchor="top",
        align="right",
        font=dict(family="Times New Roman", size=14, color="#111111"),
        bgcolor="rgba(255,255,255,0.88)",
    )

fig.update_layout(
    template="plotly_white",
    height=max(650, 470 * len(shown_classes)),
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(family="Times New Roman", size=17, color="#111111"),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.015,
        xanchor="right",
        x=1,
        font=dict(family="Times New Roman", size=18, color="#111111"),
        bgcolor="white",
    ),
    margin=dict(l=95, r=45, t=95, b=85),
    hoverlabel=dict(font=dict(family="Arial", size=13), bgcolor="#222222"),
)

for r in range(1, len(shown_classes) + 1):
    fig.update_xaxes(
        range=[0, 1],
        dtick=0.2,
        title_text="Transverse spherocity, S₀" if r == len(shown_classes) else None,
        title_font=dict(family="Times New Roman", size=24, color="#111111"),
        tickfont=dict(family="Times New Roman", size=17, color="#111111"),
        ticks="inside",
        mirror=True,
        showline=True,
        linecolor="black",
        linewidth=1.5,
        showgrid=False,
        zeroline=False,
        row=r,
        col=1,
    )
    fig.update_yaxes(
        title_text="P(S₀)",
        title_font=dict(family="Times New Roman", size=22, color="#111111"),
        tickfont=dict(family="Times New Roman", size=16, color="#111111"),
        rangemode="tozero",
        ticks="inside",
        mirror=True,
        showline=True,
        linecolor="black",
        linewidth=1.5,
        showgrid=False,
        zeroline=False,
        row=r,
        col=1,
    )

fig.update_annotations(font=dict(family="Times New Roman", size=19, color="#111111"))

st.plotly_chart(
    fig,
    use_container_width=True,
    theme=None,
    config={
        "displaylogo": False,
        "scrollZoom": True,
        "toImageButtonOptions": {
            "format": "png",
            "filename": "spherocity_original_CR_ON_vs_four_file_CR_OFF",
        },
    },
)

# Event-count table and downloadable numerical histograms.
summary = []
export = []
for label, low, high in CLASSES:
    summary.append({
        "Multiplicity interval": label,
        "CR ON events": on_totals[label],
        "CR OFF events (four files)": off_totals[label],
    })
    for i, centre in enumerate(CENTRES):
        export.append({
            "Multiplicity interval": label,
            "S0 bin centre": centre,
            "CR ON bin count": int(on_counts[label][i]),
            "CR ON probability": on_counts[label][i] / on_totals[label] if on_totals[label] else 0,
            "CR ON uncertainty": np.sqrt(on_counts[label][i]) / on_totals[label] if on_totals[label] else 0,
            "CR OFF bin count": int(off_counts[label][i]),
            "CR OFF probability": off_counts[label][i] / off_totals[label] if off_totals[label] else 0,
            "CR OFF uncertainty": np.sqrt(off_counts[label][i]) / off_totals[label] if off_totals[label] else 0,
        })

with st.expander("Event counts in each multiplicity interval", expanded=True):
    st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)

st.download_button(
    "Download five binned distributions (CSV)",
    data=pd.DataFrame(export).to_csv(index=False).encode("utf-8"),
    file_name="spherocity_CR_ON_vs_four_file_CR_OFF.csv",
    mime="text/csv",
)



# ---------------------------------------------------------------------
# Optional user upload workflow. Kept below the research results so the
# main purpose of the page remains the visual presentation of the findings.
# ---------------------------------------------------------------------
with st.expander("Try the analysis with your own simulation files", expanded=False):
    st.write(
        "Upload one CR ON event-level file and one or more CR OFF files. "
        "The app will calculate and display the same five distributions."
    )
    upload_left, upload_right = st.columns(2)
    with upload_left:
        user_on = st.file_uploader(
            "CR ON data (.txt or .txt.gz)",
            type=["txt", "gz"],
            key="user_spherocity_cr_on",
        )
    with upload_right:
        user_off = st.file_uploader(
            "CR OFF data files (.txt or .txt.gz)",
            type=["txt", "gz"],
            accept_multiple_files=True,
            key="user_spherocity_cr_off",
        )

    st.caption(
        "Expected columns: charged-particle multiplicity Nch first, "
        "transverse spherocity S0 second. Whitespace-separated; lines "
        "beginning with # are treated as comments."
    )
    user_run = st.button(
        "Calculate uploaded data",
        type="primary",
        disabled=(user_on is None or not user_off),
        key="run_user_spherocity",
    )

    def read_uploaded_histograms(uploaded):
        import gzip
        import io

        raw = uploaded.getvalue()
        if uploaded.name.lower().endswith(".gz"):
            raw = gzip.decompress(raw)
        stream = io.BytesIO(raw)
        counts, totals, rows = empty_histograms()
        for chunk in pd.read_csv(
            stream,
            sep=r"\s+",
            header=None,
            comment="#",
            usecols=[0, 1],
            names=["Nch", "S0"],
            chunksize=500_000,
            engine="c",
            on_bad_lines="skip",
        ):
            nch = pd.to_numeric(chunk["Nch"], errors="coerce").to_numpy()
            s0 = pd.to_numeric(chunk["S0"], errors="coerce").to_numpy()
            valid = np.isfinite(nch) & np.isfinite(s0) & (nch >= 0) & (s0 >= 0) & (s0 <= 1)
            nch, s0 = nch[valid], s0[valid]
            rows += len(nch)
            for label, low, high in CLASSES:
                selected = (nch >= low) & (nch < high)
                counts[label] += np.histogram(s0[selected], bins=BINS)[0]
                totals[label] += int(np.count_nonzero(selected))
        return counts, totals, rows

    if user_run:
        with st.spinner("Calculating uploaded distributions…"):
            user_on_counts, user_on_totals, user_on_rows = read_uploaded_histograms(user_on)
            user_off_counts, user_off_totals, user_off_rows = empty_histograms()
            for uploaded in user_off:
                cts, tots, nrows = read_uploaded_histograms(uploaded)
                for label, _, _ in CLASSES:
                    user_off_counts[label] += cts[label]
                    user_off_totals[label] += tots[label]
                user_off_rows += nrows

        st.success("Your uploaded datasets have been analysed.")
        u1, u2 = st.columns(2)
        u1.metric("CR ON events read", f"{user_on_rows:,}")
        u2.metric("CR OFF events read", f"{user_off_rows:,}")

        user_fig = make_subplots(
            rows=len(CLASSES),
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.055,
            subplot_titles=[item[0] for item in CLASSES],
        )
        for row, (label, low, high) in enumerate(CLASSES, start=1):
            for cfg, counts_map, totals_map, colour, symbol in [
                ("CR OFF", user_off_counts, user_off_totals, "#e60000", "square"),
                ("CR ON", user_on_counts, user_on_totals, "#000000", "circle"),
            ]:
                n_class = totals_map[label]
                bin_counts = counts_map[label]
                probability = bin_counts / n_class if n_class else np.zeros(100)
                uncertainty = np.sqrt(bin_counts) / n_class if n_class else np.zeros(100)
                user_fig.add_trace(
                    go.Scatter(
                        x=CENTRES,
                        y=probability,
                        mode="markers",
                        name=cfg,
                        legendgroup=cfg,
                        showlegend=(row == 1),
                        marker=dict(
                            symbol=symbol,
                            size=8,
                            color="white",
                            line=dict(color=colour, width=2),
                        ),
                        error_y=dict(
                            type="data",
                            array=uncertainty,
                            visible=True,
                            color=colour,
                            thickness=1.25,
                            width=3,
                        ),
                        hovertemplate=(
                            "S₀ = %{x:.2f}<br>P(S₀) = %{y:.5f}"
                            f"<extra>{cfg}</extra>"
                        ),
                    ),
                    row=row,
                    col=1,
                )

        user_fig.update_layout(
            template="plotly_white",
            height=2350,
            paper_bgcolor="white",
            plot_bgcolor="white",
            font=dict(family="Times New Roman", size=17, color="#111111"),
            legend=dict(orientation="h", y=1.015, x=1, xanchor="right"),
            margin=dict(l=95, r=45, t=95, b=85),
            hoverlabel=dict(font=dict(family="Arial", size=13), bgcolor="#222222"),
        )
        for r in range(1, len(CLASSES) + 1):
            user_fig.update_xaxes(
                range=[0, 1],
                dtick=0.2,
                title_text="Transverse spherocity, S₀" if r == len(CLASSES) else None,
                title_font=dict(family="Times New Roman", size=24),
                tickfont=dict(family="Times New Roman", size=17),
                ticks="inside",
                mirror=True,
                showline=True,
                linecolor="black",
                showgrid=False,
                row=r,
                col=1,
            )
            user_fig.update_yaxes(
                title_text="P(S₀)",
                title_font=dict(family="Times New Roman", size=22),
                tickfont=dict(family="Times New Roman", size=16),
                rangemode="tozero",
                ticks="inside",
                mirror=True,
                showline=True,
                linecolor="black",
                showgrid=False,
                row=r,
                col=1,
            )
        user_fig.update_annotations(font=dict(family="Times New Roman", size=19))
        st.plotly_chart(
            user_fig,
            use_container_width=True,
            theme=None,
            config={"displaylogo": False, "scrollZoom": True},
        )

        user_export = []
        for label, low, high in CLASSES:
            for i, centre in enumerate(CENTRES):
                item = {"Multiplicity interval": label, "S0 bin centre": centre}
                for cfg, counts_map, totals_map in [
                    ("CR ON", user_on_counts, user_on_totals),
                    ("CR OFF", user_off_counts, user_off_totals),
                ]:
                    n_class = totals_map[label]
                    n_bin = int(counts_map[label][i])
                    item[f"{cfg} bin count"] = n_bin
                    item[f"{cfg} probability"] = n_bin / n_class if n_class else 0
                    item[f"{cfg} uncertainty"] = np.sqrt(n_bin) / n_class if n_class else 0
                user_export.append(item)
        st.download_button(
            "Download uploaded-data results (CSV)",
            data=pd.DataFrame(user_export).to_csv(index=False).encode("utf-8"),
            file_name="uploaded_spherocity_CR_comparison.csv",
            mime="text/csv",
        )
