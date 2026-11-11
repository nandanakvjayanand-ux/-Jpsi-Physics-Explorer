from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

st.set_page_config(page_title="Event Topology | J/ψ Explorer", page_icon="⚛️", layout="wide")
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "topology"

st.markdown("""
<style>
.stApp {background:#0b0f19;color:#e6eaf2}
.block-container {max-width:1250px;padding-top:2.2rem}
.small-note {color:#aebbd0;font-size:.9rem}
</style>
""", unsafe_allow_html=True)

st.title("J/ψ transverse-momentum spectra by event topology")
st.markdown("**PYTHIA 8.317 · pp collisions · √s = 13 TeV · pT > 5 GeV/c generation selection**")
st.write("Compare the CR+MPI ON and CR+MPI OFF samples for integrated, jetty and isotropic event classes. Runs with seeds 103 and 104 are combined within each configuration.")
st.info("The uploaded files contain event-level (pT, y) pairs. Since generated-event counts and per-run σgen values are not supplied with this dataset, the plots show unit-area, shape-normalised pT probability densities—not absolute cross sections or yields.")

configs = {"CR + MPI ON": "on", "CR + MPI OFF": "off"}
topologies = [("Integrated", "integrated"), ("Jetty (S₀ < 0.37)", "jetty"), ("Isotropic (S₀ > 0.71)", "isotropic")]

@st.cache_data
def load_sample(topology, config):
    parts=[]
    for seed in (103,104):
        path=DATA/f"{topology}_cr_{config}_{seed}.txt"
        if not path.exists():
            raise FileNotFoundError(f"Missing data file: {path.name}")
        arr=np.loadtxt(path, dtype=float, ndmin=2)
        if arr.shape[1] < 2:
            raise ValueError(f"{path.name} must have at least two columns: pT and rapidity.")
        arr=arr[:,:2]
        arr=arr[np.isfinite(arr).all(axis=1)]
        parts.append(arr)
    return np.vstack(parts)

pt_min=float(st.sidebar.number_input("Minimum pT (GeV/c)", min_value=0.0, max_value=20.0, value=5.0, step=0.5))
pt_max=float(st.sidebar.number_input("Maximum pT (GeV/c)", min_value=6.0, max_value=100.0, value=20.0, step=1.0))
bin_width=float(st.sidebar.selectbox("pT bin width (GeV/c)", [0.25,0.5,1.0], index=1))
ymin=float(st.sidebar.number_input("Minimum rapidity", value=2.5, step=0.1))
ymax=float(st.sidebar.number_input("Maximum rapidity", value=4.0, step=0.1))
if pt_max <= pt_min or ymax <= ymin:
    st.error("The upper pT and rapidity limits must be greater than their lower limits.")
    st.stop()
edges=np.arange(pt_min, pt_max+bin_width*1.0001, bin_width)
if edges[-1] > pt_max+1e-8: edges[-1]=pt_max

fig=make_subplots(rows=3,cols=1,shared_xaxes=True,vertical_spacing=0.07,
                  subplot_titles=[x[0] for x in topologies])
summary=[]
for row,(label,topology) in enumerate(topologies, start=1):
    for name,config in configs.items():
        arr=load_sample(topology,config)
        pt,y=arr[:,0],arr[:,1]
        sel=(pt>=pt_min)&(pt<=pt_max)&(y>=ymin)&(y<ymax)
        values=pt[sel]
        counts,_=np.histogram(values,bins=edges)
        widths=np.diff(edges)
        norm=counts.sum()
        density=counts/(norm*widths) if norm else np.zeros_like(counts,dtype=float)
        err=np.sqrt(counts)/(norm*widths) if norm else np.zeros_like(counts,dtype=float)
        centers=(edges[:-1]+edges[1:])/2
        color="#111111" if config=="on" else "#c43b3b"
        symbol="circle-open" if config=="on" else "square-open"
        fig.add_trace(go.Scatter(x=centers,y=density,mode="lines+markers",name=name,
            legendgroup=name,showlegend=(row==1),line=dict(color=color,width=1.5),
            marker=dict(color=color,symbol=symbol,size=6),
            error_y=dict(type="data",array=err,visible=True,color=color,thickness=1,width=0),
            customdata=np.column_stack((counts, np.full(len(counts),norm))),
            hovertemplate="pT=%{x:.2f} GeV/c<br>PDF=%{y:.4g} (GeV/c)⁻¹<br>entries=%{customdata[0]:.0f}<br>selected total=%{customdata[1]:.0f}<extra>%{fullData.name}</extra>"),row=row,col=1)
        summary.append({"Topology":label,"Configuration":name,"Loaded J/ψ candidates":len(arr),"Selected in cuts":int(norm),"Selected fraction":norm/len(arr) if len(arr) else 0})

fig.update_layout(height=950,template="plotly_white",font=dict(family="Times New Roman",size=15,color="black"),
    paper_bgcolor="#f7f7f7",plot_bgcolor="white",margin=dict(l=85,r=35,t=90,b=65),
    legend=dict(orientation="h",y=1.04,x=0.5,xanchor="center"),hovermode="x unified")
fig.update_yaxes(title_text="Unit-area density",showline=True,linecolor="black",mirror=True,zeroline=False)
fig.update_xaxes(title_text="Transverse momentum pT (GeV/c)",row=3,col=1,showline=True,linecolor="black",mirror=True)
st.plotly_chart(fig,use_container_width=True)

st.subheader("Sample statistics")
st.caption("Counts after the selected pT and rapidity cuts. The two seed files are combined for each row.")
df=pd.DataFrame(summary)
st.dataframe(df,hide_index=True,use_container_width=True)
st.download_button("Download sample statistics (CSV)",df.to_csv(index=False).encode(),"topology_sample_statistics.csv","text/csv")

st.subheader("Simulation definition")
st.markdown("""
- **CR + MPI ON:** colour-reconnection and multiparton-interaction configuration from the uploaded CR-on generator output.
- **CR + MPI OFF:** colour reconnection disabled and MPI switched off in the uploaded generator output.
- **Integrated:** all accepted events with Nch ≥ 5.
- **Jetty:** transverse spherocity S₀ < 0.37.
- **Isotropic:** transverse spherocity S₀ > 0.71.

The CR and MPI settings are changed together in these samples. Therefore, this page compares the two combined configurations and does not isolate the effect of CR from MPI.
""")
