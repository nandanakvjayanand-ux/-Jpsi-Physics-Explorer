from pathlib import Path
import re
import io

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from scipy.optimize import curve_fit

st.set_page_config(
    page_title="Invariant Mass | J/ψ Physics Explorer",
    page_icon="⚛️",
    layout="wide"
)

ROOT = Path(__file__).resolve().parents[1]
DATA_DIRS = [
    ROOT, ROOT / "data", ROOT / "assets", ROOT / "documentation",
    Path.home() / "Desktop" / "WEB-APP SIMLATION FILE ",
    Path.home() / "Desktop" / "WEB APP ALICE:LHCB DATA FILE "
]

st.markdown("""
<style>
.stApp {background:#0b0f19;color:#e6eaf2}
.block-container {max-width:1450px;padding-top:2rem;padding-bottom:4rem}
h1,h2,h3,p,label {color:#e6eaf2}
div[data-testid="stMetric"] {
 background:#151e2e;border:1px solid #34445f;border-radius:10px;padding:15px
}
</style>
""", unsafe_allow_html=True)

st.title("Invariant-Mass Reconstruction")
st.markdown("""
Interactive comparison of prompt and non-prompt dimuon invariant-mass
distributions using PYTHIA 8 and LHCb reference data.

**√s = 13 TeV** · **3 < |y| < 3.5** · **2 < pT < 3 GeV/c**
""")
st.divider()

def locate_file(name):
    for folder in DATA_DIRS:
        candidate = folder / name
        if candidate.exists():
            return candidate
    return None

required = [
    "jpsi_mass_level2_prompt.dat",
    "jpsi_mass_level2_fromb.dat",
    "jpsi_mass_level2_300m_prompt.dat",
    "jpsi_mass_level2_from_b_300m.dat",
    "Fig1a.C.txt"
]
paths = {name: locate_file(name) for name in required}
missing = [name for name, path in paths.items() if path is None]
if missing:
    st.error("Required input files are missing:")
    for name in missing:
        st.write(f"- `{name}`")
    st.info("Place the files in the project data folder or the existing Desktop data folders.")
    st.stop()

MASS_MIN, MASS_MAX, BIN_WIDTH = 2950.0, 3250.0, 5.0
BINS = np.arange(MASS_MIN, MASS_MAX + BIN_WIDTH, BIN_WIDTH)
CENTRES = (BINS[:-1] + BINS[1:]) / 2
MASS_GRID = np.linspace(MASS_MIN, MASS_MAX, 2000)

@st.cache_data
def read_mass_file(filename):
    return np.atleast_1d(np.loadtxt(filename)) * 1000.0

prompt_mass = np.concatenate([
    read_mass_file(str(paths["jpsi_mass_level2_prompt.dat"])),
    read_mass_file(str(paths["jpsi_mass_level2_300m_prompt.dat"]))
])
fromb_mass = np.concatenate([
    read_mass_file(str(paths["jpsi_mass_level2_fromb.dat"])),
    read_mass_file(str(paths["jpsi_mass_level2_from_b_300m.dat"]))
])
prompt_mass = prompt_mass[(prompt_mass >= MASS_MIN) & (prompt_mass <= MASS_MAX)]
fromb_mass = fromb_mass[(fromb_mass >= MASS_MIN) & (fromb_mass <= MASS_MAX)]
if not len(prompt_mass) or not len(fromb_mass):
    st.error("No PYTHIA candidates in the selected mass interval.")
    st.stop()

prompt_counts, _ = np.histogram(prompt_mass, bins=BINS)
fromb_counts, _ = np.histogram(fromb_mass, bins=BINS)

def gaussian(x, amplitude, mean, sigma):
    sigma = max(abs(float(sigma)), 1e-9)
    return amplitude * np.exp(-0.5 * ((x - mean) / sigma) ** 2)

def fit_gaussian(mass, counts):
    mask = counts > 0
    x, y = CENTRES[mask], counts[mask]
    if len(x) < 4:
        raise ValueError("Insufficient populated bins for Gaussian fitting.")
    errors = np.sqrt(y)
    initial = [float(y.max()), float(np.mean(mass)), max(float(np.std(mass)), 1.0)]
    parameters, covariance = curve_fit(
        gaussian, x, y, p0=initial, sigma=errors,
        absolute_sigma=True, maxfev=100000
    )
    amplitude, mean, sigma = parameters
    return float(amplitude), float(mean), abs(float(sigma)), covariance

try:
    prompt_A, prompt_mu, prompt_sigma, prompt_cov = fit_gaussian(prompt_mass, prompt_counts)
    fromb_A, fromb_mu, fromb_sigma, fromb_cov = fit_gaussian(fromb_mass, fromb_counts)
except Exception as exc:
    st.error(f"Gaussian fitting failed: {exc}")
    st.stop()

@st.cache_data
def read_lhcb_text(filename):
    return Path(filename).read_text()

lhcb_text = read_lhcb_text(str(paths["Fig1a.C.txt"]))

def extract_graph(text, graph_name):
    start = text.find(f'graph->SetName("{graph_name}")')
    if start == -1:
        raise RuntimeError(f"Could not find LHCb graph: {graph_name}")
    end = text.find("graph = new TGraph", start + 1)
    if end == -1:
        end = len(text)
    block = text[start:end]
    pattern = re.compile(
        r'graph->SetPoint\(\s*\d+\s*,\s*([-\d.eE+]+)\s*,\s*([-\d.eE+]+)\s*\);'
    )
    matches = pattern.findall(block)
    if not matches:
        raise RuntimeError(f"No points found for LHCb graph: {graph_name}")
    return np.array([float(a) for a, b in matches]), np.array([float(b) for a, b in matches])

prompt_graph = "tot_fun_all_Int[tz]_Norm[psi_MM,tz]_DataAvg[tze]_Comp[sig_tm_0]"
fromb_graph = "tot_fun_all_Int[tz]_Norm[psi_MM,tz]_DataAvg[tze]_Comp[sig_tm_b]"
try:
    lp_x, lp_y = extract_graph(lhcb_text, prompt_graph)
    lb_x, lb_y = extract_graph(lhcb_text, fromb_graph)
except Exception as exc:
    st.error(f"LHCb data extraction failed: {exc}")
    st.stop()

mp = (lp_x >= MASS_MIN) & (lp_x <= MASS_MAX)
mb = (lb_x >= MASS_MIN) & (lb_x <= MASS_MAX)
lp_x, lp_y = lp_x[mp], lp_y[mp]
lb_x, lb_y = lb_x[mb], lb_y[mb]
if not len(lp_y) or not len(lb_y):
    st.error("LHCb graphs contain no points in the selected mass interval.")
    st.stop()

lp_signal = np.maximum(lp_y - np.min(lp_y), 0)
lb_signal = np.maximum(lb_y - np.min(lb_y), 0)
lp_yield, lb_yield = np.sum(lp_signal), np.sum(lb_signal)
if lp_yield <= 0 or lb_yield <= 0:
    st.error("Extracted LHCb component yields are not positive.")
    st.stop()

prompt_norm = lp_yield / (prompt_A * prompt_sigma * np.sqrt(2*np.pi))
fromb_norm = lb_yield / (fromb_A * fromb_sigma * np.sqrt(2*np.pi))

# Summary
st.header("Reconstruction summary")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Prompt candidates", f"{len(prompt_mass):,}")
m2.metric("From-b candidates", f"{len(fromb_mass):,}")
m3.metric("Prompt fitted mean", f"{prompt_mu:.3f} MeV")
m4.metric("From-b fitted mean", f"{fromb_mu:.3f} MeV")

# Parameter controls
st.divider()
st.header("1. Gaussian fit parameter explorer")
st.caption("Change the PYTHIA fit parameters to see their effect on the displayed curves. Original fitted values are the defaults.")
with st.expander("Edit prompt and from-b parameters", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Prompt J/ψ")
        p_mu = st.number_input("Prompt mean (MeV/c²)", 3000.0, 3200.0, float(prompt_mu), 0.001, format="%.3f")
        p_sig = st.number_input("Prompt sigma (MeV/c²)", 0.1, 100.0, float(prompt_sigma), 0.001, format="%.3f")
        p_amp = st.number_input("Prompt amplitude", 0.001, 1e9, float(prompt_A), 0.1, format="%.3f")
        p_norm = st.number_input("Prompt normalisation", 0.000001, 1e9, float(prompt_norm), 0.0001, format="%.6f")
    with c2:
        st.subheader("Non-prompt J/ψ (from-b)")
        b_mu = st.number_input("From-b mean (MeV/c²)", 3000.0, 3200.0, float(fromb_mu), 0.001, format="%.3f")
        b_sig = st.number_input("From-b sigma (MeV/c²)", 0.1, 100.0, float(fromb_sigma), 0.001, format="%.3f")
        b_amp = st.number_input("From-b amplitude", 0.001, 1e9, float(fromb_A), 0.1, format="%.3f")
        b_norm = st.number_input("From-b normalisation", 0.000001, 1e9, float(fromb_norm), 0.0001, format="%.6f")

# Plot
st.divider()
st.header("2. Interactive invariant-mass distribution")
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=lp_x, y=lp_y, mode="lines", name="LHCb prompt J/ψ",
    line=dict(color="#D62728", width=2.5),
    hovertemplate="Mass: %{x:.2f} MeV/c²<br>Value: %{y:.3f}<extra>LHCb prompt</extra>"
))
fig.add_trace(go.Scatter(
    x=lb_x, y=lb_y, mode="lines", name="LHCb J/ψ from-b",
    line=dict(color="black", width=2.3, dash="dash"),
    hovertemplate="Mass: %{x:.2f} MeV/c²<br>Value: %{y:.3f}<extra>LHCb from-b</extra>"
))
fig.add_trace(go.Scatter(
    x=MASS_GRID, y=p_norm * gaussian(MASS_GRID, p_amp, p_mu, p_sig),
    mode="lines", name="PYTHIA 8 prompt J/ψ",
    line=dict(color="#D62728", width=2.5, dash="dot"),
    hovertemplate="Mass: %{x:.2f} MeV/c²<br>Value: %{y:.3f}<extra>PYTHIA prompt</extra>"
))
fig.add_trace(go.Scatter(
    x=MASS_GRID, y=b_norm * gaussian(MASS_GRID, b_amp, b_mu, b_sig),
    mode="lines", name="PYTHIA 8 J/ψ from-b",
    line=dict(color="black", width=2.5, dash="dashdot"),
    hovertemplate="Mass: %{x:.2f} MeV/c²<br>Value: %{y:.3f}<extra>PYTHIA from-b</extra>"
))
fig.update_layout(
    template="simple_white", height=650,
    paper_bgcolor="white", plot_bgcolor="white",
    font=dict(family="Arial, Helvetica, sans-serif", size=16, color="#111111"),
    margin=dict(l=105, r=45, t=115, b=105),
    autosize=True,
    title=None,
    legend=dict(
        orientation="h", x=0.5, xanchor="center", y=1.08,
        font=dict(family="Arial, Helvetica, sans-serif", size=14, color="#111111"),
        bgcolor="rgba(255,255,255,0)",
        itemsizing="constant"
    ),
    hovermode="closest",
    hoverlabel=dict(
        bgcolor="white", bordercolor="#444444",
        font=dict(family="Arial", size=12, color="#111111")
    )
)
fig.update_xaxes(
    title_text="Dimuon invariant mass, m(μ⁺μ⁻) [MeV/c²]",
    range=[MASS_MIN, MASS_MAX],
    tickvals=[2950, 3000, 3050, 3100, 3150, 3200, 3250],
    showline=True, linewidth=1.3, linecolor="black", mirror=True,
    ticks="inside", showgrid=False,
    title_font=dict(family="Arial, Helvetica, sans-serif", size=18, color="#111111"),
    tickfont=dict(family="Arial, Helvetica, sans-serif", size=15, color="#111111"),
    zeroline=False,
    color="#111111",
    title_standoff=18
)
fig.update_yaxes(
    title_text="Candidates per 5 MeV/c²",
    range=[0, 10500], showline=True, linewidth=1.3,
    linecolor="black", mirror=True, ticks="inside", showgrid=False,
    title_font=dict(family="Arial, Helvetica, sans-serif", size=18, color="#111111"),
    tickfont=dict(family="Arial, Helvetica, sans-serif", size=15, color="#111111"),
    zeroline=False,
    color="#111111",
    title_standoff=18
)
st.plotly_chart(fig, use_container_width=True, theme=None, config={
    "displayModeBar": True, "scrollZoom": True, "displaylogo": False,
    "responsive": True,
    "toImageButtonOptions": {"format": "png", "filename": "Jpsi_Invariant_Mass", "scale": 3}
})
st.caption("Use the legend to show or hide curves. Hover to inspect mass and distribution values.")

# Parameter summary and download
st.divider()
st.header("3. Current fit parameters")
fit_table = pd.DataFrame({
    "Parameter": ["Mean (MeV/c²)", "Sigma (MeV/c²)", "Amplitude", "Normalisation"],
    "Prompt J/ψ": [p_mu, p_sig, p_amp, p_norm],
    "J/ψ from-b": [b_mu, b_sig, b_amp, b_norm]
})
st.dataframe(fit_table, use_container_width=True, hide_index=True)
st.download_button("Download current fit parameters", fit_table.to_csv(index=False),
                   "jpsi_current_fit_parameters.csv", "text/csv")

# Fit diagnostics from original fits
st.divider()
st.header("4. Original Gaussian fit diagnostics")
def diagnostics(mass, counts, pars):
    amp, mean, sigma, cov = pars
    mask = counts > 0
    x, y = CENTRES[mask], counts[mask]
    err = np.sqrt(y)
    chi2 = np.sum(((y - gaussian(x, amp, mean, sigma))/err)**2)
    dof = max(len(y)-3, 1)
    perr = np.sqrt(np.maximum(np.diag(cov), 0))
    return chi2, dof, chi2/dof, perr

dp = diagnostics(prompt_mass, prompt_counts, (prompt_A, prompt_mu, prompt_sigma, prompt_cov))
db = diagnostics(fromb_mass, fromb_counts, (fromb_A, fromb_mu, fromb_sigma, fromb_cov))
diag_df = pd.DataFrame({
    "Quantity": ["Chi-square", "Degrees of freedom", "Reduced chi-square",
                 "Amplitude uncertainty", "Mean uncertainty (MeV/c²)", "Sigma uncertainty (MeV/c²)"],
    "Prompt": [dp[0], dp[1], dp[2], dp[3][0], dp[3][1], dp[3][2]],
    "From-b": [db[0], db[1], db[2], db[3][0], db[3][1], db[3][2]]
})
st.dataframe(diag_df, use_container_width=True, hide_index=True)
st.caption("Diagnostics refer to the original unscaled PYTHIA histogram fits, using Poisson uncertainties.")

# Upload numerical data
st.divider()
st.header("5. Upload and fit your own numerical data")
st.caption("Upload a one-column event-mass file or a two-column histogram (mass, counts). Masses in GeV are converted to MeV.")
upload = st.file_uploader("Upload CSV/TXT/DAT", type=["csv", "txt", "dat"], key="mass_data_upload")

if upload is not None:
    try:
        if upload.name.lower().endswith(".csv"):
            df = pd.read_csv(upload, header=None)
        else:
            df = pd.read_csv(upload, sep=r"\s+|,", engine="python", comment="#", header=None)
        numeric = df.apply(pd.to_numeric, errors="coerce").dropna()
        if numeric.empty:
            raise ValueError("No numerical values found.")
        if numeric.shape[1] == 1:
            values = numeric.iloc[:, 0].to_numpy(float)
            if np.nanmedian(values) < 100:
                values *= 1000
            values = values[(values >= MASS_MIN) & (values <= MASS_MAX)]
            counts, _ = np.histogram(values, bins=BINS)
            event_values = values
        else:
            masses = numeric.iloc[:, 0].to_numpy(float)
            counts_in = numeric.iloc[:, 1].to_numpy(float)
            if np.nanmedian(masses) < 100:
                masses *= 1000
            valid = np.isfinite(masses) & np.isfinite(counts_in) & (counts_in >= 0)
            masses, counts_in = masses[valid], counts_in[valid]
            rebinned = np.zeros(len(CENTRES))
            inds = np.digitize(masses, BINS) - 1
            for i, n in zip(inds, counts_in):
                if 0 <= i < len(rebinned):
                    rebinned[i] += n
            counts = rebinned
            event_values = np.repeat(masses[(masses >= MASS_MIN) & (masses <= MASS_MAX)],
                                     np.maximum(counts_in[(masses >= MASS_MIN) & (masses <= MASS_MAX)].astype(int), 0))
        if counts.sum() <= 0:
            raise ValueError("No data in the 2950–3250 MeV/c² mass interval.")
        mask = counts > 0
        x, y = CENTRES[mask], counts[mask]
        if len(x) < 4:
            raise ValueError("Insufficient populated bins for fitting.")
        pars, cov = curve_fit(gaussian, x, y, p0=[y.max(), x[np.argmax(y)], 10],
                              sigma=np.sqrt(y), absolute_sigma=True, maxfev=100000)
        amp, mean, sigma = pars
        errs = np.sqrt(np.maximum(np.diag(cov), 0))
        st.success("Gaussian fit completed.")
        a, b, c = st.columns(3)
        a.metric("Mean", f"{mean:.3f} MeV/c²")
        b.metric("Sigma", f"{abs(sigma):.3f} MeV/c²")
        c.metric("Amplitude", f"{amp:.3f}")
        uf = go.Figure()
        uf.add_trace(go.Bar(x=CENTRES, y=counts, name="Uploaded histogram", marker_color="lightgrey"))
        uf.add_trace(go.Scatter(x=MASS_GRID, y=gaussian(MASS_GRID, amp, mean, sigma),
                                mode="lines", name="Gaussian fit", line=dict(color="#D62728", width=2.5)))
        uf.update_layout(template="simple_white", height=460,
                         xaxis_title="Invariant mass (MeV/c²)", yaxis_title="Counts",
                         font=dict(family="Arial, Helvetica, sans-serif", size=15, color="#111111"))
        st.plotly_chart(uf, use_container_width=True)
        result = pd.DataFrame({"Parameter": ["Amplitude", "Mean (MeV/c²)", "Sigma (MeV/c²)"],
                               "Value": [amp, mean, abs(sigma)], "Uncertainty": errs})
        st.dataframe(result, use_container_width=True, hide_index=True)
        st.download_button("Download uploaded-data fit", result.to_csv(index=False),
                           "uploaded_mass_fit.csv", "text/csv")
    except Exception as exc:
        st.error(f"Could not fit uploaded data: {exc}")

# PDF text extraction
st.divider()
st.header("6. Research PDF parameter extraction")
st.caption("Extracts searchable PDF text and explicitly reported fit values. A graph-only PDF needs digitisation; its underlying points cannot be recovered reliably from text extraction.")
pdf_upload = st.file_uploader("Upload research PDF", type=["pdf"], key="mass_pdf_upload")
if pdf_upload is not None:
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_upload)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        st.success(f"Read {len(reader.pages)} pages.")
        if not text.strip():
            st.warning("No selectable text found. The PDF may be scanned or image-only.")
        else:
            patterns = {
                "Mean": r"mean\s*[:=]\s*([-+]?\d*\.?\d+)",
                "Sigma": r"sigma\s*[:=]\s*([-+]?\d*\.?\d+)",
                "Amplitude": r"amplitude\s*[:=]\s*([-+]?\d*\.?\d+)",
                "Normalisation": r"normalisation\s*[:=]\s*([-+]?\d*\.?\d+)"
            }
            found = {k: float(m.group(1)) for k, p in patterns.items()
                     if (m := re.search(p, text, re.IGNORECASE))}
            if found:
                st.subheader("Reported parameters detected")
                st.dataframe(pd.DataFrame(list(found.items()), columns=["Parameter", "Extracted value"]),
                             use_container_width=True, hide_index=True)
            else:
                st.info("No supported parameter labels found. Inspect the extracted text.")
            with st.expander("View extracted PDF text"):
                st.text_area("Extracted text", text, height=350)
            st.download_button("Download extracted text", text,
                               "research_pdf_extracted_text.txt", "text/plain")
        st.warning("Text extraction does not digitise graph images. For graph-only PDFs, upload underlying data or digitise the plotted points.")
    except Exception as exc:
        st.error(f"PDF extraction failed: {exc}")

# Numerical downloads
st.divider()
st.header("7. Download source datasets")
downloads = {
    "PYTHIA prompt histogram": pd.DataFrame({"mass_MeV": CENTRES, "counts": prompt_counts}),
    "PYTHIA from-b histogram": pd.DataFrame({"mass_MeV": CENTRES, "counts": fromb_counts}),
    "LHCb prompt": pd.DataFrame({"mass_MeV": lp_x, "LHCb_value": lp_y}),
    "LHCb from-b": pd.DataFrame({"mass_MeV": lb_x, "LHCb_value": lb_y})
}
cols = st.columns(2)
for i, (label, frame) in enumerate(downloads.items()):
    with cols[i % 2]:
        st.download_button(f"Download {label}", frame.to_csv(index=False),
                           f"{label.lower().replace(' ', '_')}.csv", "text/csv")

st.caption("PYTHIA prompt and from-b samples are fitted independently. LHCb reference curves are extracted from the supplied Fig1a.C.txt. PYTHIA curves are scaled using the original fit-based normalisation.")
