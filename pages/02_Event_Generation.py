import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Event Generation",
    page_icon="⚛️",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: #0b0f19;
    color: #e7eaf2;
}
h1, h2, h3, p, li {
    color: #e7eaf2;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}
.section-card {
    background: #151e2e;
    border: 1px solid #405777;
    border-radius: 12px;
    padding: 22px;
    margin: 10px 0;
}
.metric-card {
    background: #151e2e;
    border: 1px solid #405777;
    border-radius: 12px;
    padding: 22px;
    min-height: 160px;
}
.metric-label {
    color: #aebbd0;
    font-size: 0.95rem;
    margin-bottom: 20px;
}
.metric-value {
    color: #f0f2f7;
    font-size: 2rem;
    font-weight: 650;
    line-height: 1.2;
}
.metric-description {
    color: #8fa7ca;
    font-size: 0.9rem;
    margin-top: 10px;
}
.config-card {
    background: #151e2e;
    border: 1px solid #405777;
    border-radius: 12px;
    padding: 24px;
    min-height: 185px;
}
.config-card h3 {
    margin-top: 0;
}
.config-card p {
    color: #b5c3d8;
}
.small-note {
    color: #aebbd0;
    font-size: 0.95rem;
}
.explanation-card {
    background: #151e2e;
    border: 1px solid #405777;
    border-radius: 12px;
    padding: 22px;
    height: 100%;
}
.explanation-card p {
    color: #c3cee0;
    line-height: 1.7;
}
</style>
""", unsafe_allow_html=True)


st.title("Event Generation")

st.write(
    "Explore the Monte Carlo event-generation framework "
    "used in this research."
)

st.divider()


# 01 — Collision configuration
st.header("01 | Collision Configuration")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Collision system</div>
        <div class="metric-value">pp</div>
        <div class="metric-description">
            Proton–proton collisions
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Centre-of-mass energy</div>
        <div class="metric-value">13 TeV</div>
        <div class="metric-description">
            √s = 13 TeV
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Event generator</div>
        <div class="metric-value">PYTHIA 8.317</div>
        <div class="metric-description">
            Monte Carlo event simulation
        </div>
    </div>
    """, unsafe_allow_html=True)


st.divider()


# 02 — Generator configuration
st.header("02 | Generator Configuration")

st.write(
    "The event samples are generated using PYTHIA 8.317 "
    "with the following settings."
)

settings = [
    ("Tune:pp", "5", "PYTHIA proton–proton tune"),
    ("HardQCD:all", "on", "Hard QCD processes enabled"),
    ("Charmonium:all", "on", "Charmonium production processes enabled"),
]

for name, value, description in settings:
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(f"**{name}**")
    with c2:
        st.markdown(f"`{value}` — {description}")


st.divider()


# 03 — MPI and colour reconnection
st.header("03 | MPI and Colour Reconnection")

st.write(
    "The study compares two configurations in which multiparton "
    "interactions (MPI) and colour reconnection (CR) are switched "
    "on or off together."
)

configuration = st.radio(
    "Select the configuration",
    ["MPI + CR ON", "MPI + CR OFF"],
    horizontal=True
)

if configuration == "MPI + CR ON":
    st.markdown("""
    <div class="config-card" style="border-color:#4388c5;">
        <h3>MPI + CR ON</h3>
        <p>Multiparton interactions are enabled.</p>
        <p>Colour reconnection is enabled.</p>
        <p class="small-note">
            This configuration includes additional partonic
            interactions and colour reconnection before hadronisation.
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="config-card" style="border-color:#a94f4f;">
        <h3>MPI + CR OFF</h3>
        <p>Multiparton interactions are disabled.</p>
        <p>Colour reconnection is disabled.</p>
        <p class="small-note">
            This configuration provides the comparison sample
            without MPI and colour reconnection.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.info(
    "MPI and colour reconnection are varied simultaneously. "
    "Their individual contributions cannot be isolated from "
    "this comparison alone."
)


st.divider()


# 04 — Event selection
st.header("04 | Event Selection")

st.write("The analysis considers:")

for item in [
    "Proton–proton collisions at √s = 13 TeV.",
    "Inclusive J/ψ production.",
    "Forward and midrapidity regions.",
    "Charged-particle multiplicity.",
    "Transverse spherocity event classification.",
]:
    st.markdown(f"- {item}")


st.divider()


# 05 — Kinematic selections
st.header("05 | Kinematic Selections")

forward, middle = st.columns(2)

with forward:
    st.markdown("""
    <div class="section-card">
        <h3>Forward dimuon analysis</h3>
        <p>Rapidity selection</p>
        <h2>2.5 &lt; |y| &lt; 4.0</h2>
        <p>J/ψ → μ⁺ μ⁻</p>
    </div>
    """, unsafe_allow_html=True)

with middle:
    st.markdown("""
    <div class="section-card">
        <h3>Midrapidity dielectron analysis</h3>
        <p>Rapidity selection</p>
        <h2>|y| &lt; 0.9</h2>
        <p>J/ψ → e⁺ e⁻</p>
    </div>
    """, unsafe_allow_html=True)

st.write(
    "The reconstructed dilepton four-momentum is used to obtain "
    "the kinematic properties of the J/ψ candidate."
)


st.divider()


# 06 — Transverse spherocity
st.header("06 | Transverse Spherocity")

st.markdown("""
Transverse spherocity is an event-shape observable used to describe
the azimuthal distribution of particles in the plane transverse
to the beam direction.

It helps distinguish events with a strongly preferred direction
from events in which particles are distributed more uniformly.
""")

st.subheader("Visual interpretation")

components.html("""
<div style="
    width:100%;
    background:#101827;
    border:1px solid #405777;
    border-radius:16px;
    padding:18px 12px 14px 12px;
    box-sizing:border-box;
    font-family:Arial,sans-serif;
    color:#e7eaf2;
">
<svg viewBox="0 0 1000 465" width="100%"
     xmlns="http://www.w3.org/2000/svg"
     role="img" aria-label="Comparison of jetty and isotropic events">

<defs>
    <marker id="redArrow" markerWidth="8" markerHeight="8"
            refX="6" refY="3" orient="auto">
        <path d="M0,0 L6,3 L0,6" fill="#ff7777"/>
    </marker>
    <marker id="blueArrow" markerWidth="8" markerHeight="8"
            refX="6" refY="3" orient="auto">
        <path d="M0,0 L6,3 L0,6" fill="#72baff"/>
    </marker>
    <marker id="greenArrow" markerWidth="8" markerHeight="8"
            refX="6" refY="3" orient="auto">
        <path d="M0,0 L6,3 L0,6" fill="#68d6a0"/>
    </marker>
</defs>

<!-- Panel backgrounds -->
<rect x="10" y="10" width="475" height="440" rx="14"
      fill="#172235" stroke="#a94f4f" stroke-width="1.5"/>
<rect x="515" y="10" width="475" height="440" rx="14"
      fill="#172235" stroke="#397db5" stroke-width="1.5"/>

<!-- Panel headings -->
<text x="247" y="48" text-anchor="middle"
      font-size="25" font-weight="bold" fill="#ff9292">
    JETTY EVENT
</text>
<text x="752" y="48" text-anchor="middle"
      font-size="25" font-weight="bold" fill="#86c5ff">
    ISOTROPIC EVENT
</text>

<text x="247" y="75" text-anchor="middle"
      font-size="15" fill="#c5cfdf">
    Particles concentrated along a preferred direction
</text>
<text x="752" y="75" text-anchor="middle"
      font-size="15" fill="#c5cfdf">
    Particles distributed more uniformly in azimuth
</text>

<!-- Left event coordinate system -->
<g stroke="#65758d" stroke-width="1.5">
    <line x1="90" y1="230" x2="405" y2="230"/>
    <line x1="247" y1="105" x2="247" y2="355"/>
</g>
<text x="411" y="235" font-size="13" fill="#aebbd0">x</text>
<text x="254" y="110" font-size="13" fill="#aebbd0">y</text>

<!-- Jet cone -->
<path d="M247 230 L105 178 L105 282 Z"
      fill="#e65e5e" opacity="0.13"/>
<path d="M247 230 L105 178 M247 230 L105 282"
      stroke="#e87979" stroke-width="1.5" stroke-dasharray="5 5"/>

<!-- Jet particles and momentum arrows -->
<g fill="#ff7777" stroke="#ffb1b1" stroke-width="1">
    <circle cx="215" cy="218" r="5"/>
    <circle cx="185" cy="222" r="5"/>
    <circle cx="155" cy="213" r="5"/>
    <circle cx="125" cy="205" r="5"/>
    <circle cx="177" cy="241" r="5"/>
    <circle cx="145" cy="250" r="5"/>
    <circle cx="112" cy="260" r="5"/>
    <circle cx="198" cy="208" r="4"/>
    <circle cx="165" cy="230" r="4"/>
    <circle cx="132" cy="222" r="4"/>
</g>

<g stroke="#ff7777" stroke-width="2.8" marker-end="url(#redArrow)">
    <line x1="215" y1="218" x2="125" y2="185"/>
    <line x1="185" y1="222" x2="108" y2="198"/>
    <line x1="177" y1="241" x2="112" y2="263"/>
    <line x1="155" y1="213" x2="90" y2="190"/>
</g>

<!-- Jet spherocity axis -->
<line x1="247" y1="230" x2="100" y2="230"
      stroke="#68d6a0" stroke-width="3"
      marker-end="url(#greenArrow)"/>
<text x="112" y="215" font-size="16" fill="#68d6a0"
      font-weight="bold">n̂</text>

<text x="247" y="385" text-anchor="middle"
      font-size="19" font-weight="bold" fill="#ff9292">
    S₀ → 0
</text>
<text x="247" y="410" text-anchor="middle"
      font-size="14" fill="#c5cfdf">
    Strongly collimated event
</text>

<!-- Right event coordinate system -->
<g stroke="#65758d" stroke-width="1.5">
    <line x1="595" y1="230" x2="910" y2="230"/>
    <line x1="752" y1="105" x2="752" y2="355"/>
</g>
<text x="916" y="235" font-size="13" fill="#aebbd0">x</text>
<text x="759" y="110" font-size="13" fill="#aebbd0">y</text>

<!-- Isotropic particles -->
<g fill="#72baff" stroke="#b4dcff" stroke-width="1">
    <circle cx="810" cy="145" r="5"/>
    <circle cx="862" cy="180" r="5"/>
    <circle cx="875" cy="245" r="5"/>
    <circle cx="835" cy="300" r="5"/>
    <circle cx="760" cy="325" r="5"/>
    <circle cx="685" cy="292" r="5"/>
    <circle cx="640" cy="240" r="5"/>
    <circle cx="665" cy="165" r="5"/>
    <circle cx="730" cy="135" r="5"/>
    <circle cx="790" cy="205" r="5"/>
    <circle cx="710" cy="260" r="5"/>
    <circle cx="820" cy="265" r="5"/>
</g>

<!-- Isotropic momentum arrows -->
<g stroke="#72baff" stroke-width="2.5" marker-end="url(#blueArrow)">
    <line x1="810" y1="145" x2="845" y2="112"/>
    <line x1="862" y1="180" x2="900" y2="160"/>
    <line x1="875" y1="245" x2="915" y2="250"/>
    <line x1="835" y1="300" x2="860" y2="338"/>
    <line x1="760" y1="325" x2="760" y2="365"/>
    <line x1="685" y1="292" x2="655" y2="330"/>
    <line x1="640" y1="240" x2="600" y2="240"/>
    <line x1="665" y1="165" x2="630" y2="135"/>
    <line x1="730" y1="135" x2="720" y2="98"/>
    <line x1="790" y1="205" x2="830" y2="195"/>
    <line x1="710" y1="260" x2="680" y2="280"/>
    <line x1="820" y1="265" x2="850" y2="290"/>
</g>

<!-- Isotropic reference axis -->
<line x1="752" y1="230" x2="900" y2="230"
      stroke="#68d6a0" stroke-width="3"
      marker-end="url(#greenArrow)"/>
<text x="885" y="215" font-size="16" fill="#68d6a0"
      font-weight="bold">n̂</text>

<text x="752" y="385" text-anchor="middle"
      font-size="19" font-weight="bold" fill="#86c5ff">
    S₀ → 1
</text>
<text x="752" y="410" text-anchor="middle"
      font-size="14" fill="#c5cfdf">
    Nearly uniform azimuthal distribution
</text>

<!-- Bottom legend -->
<circle cx="355" cy="435" r="5" fill="#ff7777"/>
<text x="367" y="440" font-size="12" fill="#c5cfdf">Jetty particles</text>
<circle cx="520" cy="435" r="5" fill="#72baff"/>
<text x="532" y="440" font-size="12" fill="#c5cfdf">Isotropic particles</text>
<line x1="685" y1="435" x2="715" y2="435"
      stroke="#68d6a0" stroke-width="3"/>
<text x="723" y="440" font-size="12" fill="#c5cfdf">Reference axis n̂</text>

</svg>
</div>
""", height=490, scrolling=False)


st.subheader("How is transverse spherocity defined?")

st.markdown("""
The transverse spherocity is calculated using the transverse
momenta of the final-state particles. The axis is chosen to
minimise the sum of the momentum components perpendicular to it.
""")

st.latex(
    r"S_0 = \frac{\pi^2}{4}"
    r"\left("
    r"\frac{\sum_i |\vec{p}_{T,i}\times\hat{n}|}"
    r"{\sum_i p_{T,i}}"
    r"\right)^2"
)

st.markdown("""
Here:

- **\\(\\vec{p}_{T,i}\\)** is the transverse momentum vector of particle \\(i\\).
- **\\(p_{T,i}\\)** is the magnitude of that transverse momentum.
- **\\(\\hat{n}\\)** is the transverse unit vector defining the spherocity axis.
- The minimisation selects the axis that gives the smallest perpendicular momentum contribution.
""")

st.divider()

st.subheader("Understanding the two event classes")

jetty_col, isotropic_col = st.columns(2)

with jetty_col:
    st.markdown("""
    <div class="explanation-card" style="border-top:4px solid #e87979;">
        <h3 style="color:#ff9292;">Jetty events</h3>
        <h2 style="color:#ff9292;">S₀ → 0</h2>
        <p>
        The transverse momenta of particles are concentrated
        around a preferred direction. Their components
        perpendicular to the spherocity axis are relatively small.
        </p>
        <p>
        This produces a low transverse-spherocity value and
        corresponds to a more collimated event topology.
        </p>
    </div>
    """, unsafe_allow_html=True)

with isotropic_col:
    st.markdown("""
    <div class="explanation-card" style="border-top:4px solid #72baff;">
        <h3 style="color:#86c5ff;">Isotropic events</h3>
        <h2 style="color:#86c5ff;">S₀ → 1</h2>
        <p>
        The transverse momenta are distributed more uniformly
        in azimuth, without one strongly preferred direction.
        </p>
        <p>
        This produces a high transverse-spherocity value and
        corresponds to a more isotropic event topology.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.info(
    "In this analysis, transverse spherocity is used to classify "
    "the generated events according to their azimuthal topology. "
    "The J/ψ observables can then be studied separately for "
    "jetty and isotropic event classes."
)


st.divider()


# 07 — Analysis framework
st.header("07 | Analysis Framework")

st.markdown("""
<div class="section-card">
    <h3>Generated events</h3>
    <p>
    PYTHIA generates the proton–proton collision events and
    their final-state particles. The selected J/ψ candidates
    are then used for the subsequent analysis.
    </p>
</div>

<div class="section-card">
    <h3>Observables</h3>
    <p>
    The generated samples are studied through transverse momentum,
    rapidity, charged-particle multiplicity and transverse spherocity.
    </p>
</div>

<div class="section-card">
    <h3>Experimental comparison</h3>
    <p>
    The simulated production distributions are compared with
    the corresponding ALICE measurements.
    </p>
</div>
""", unsafe_allow_html=True)
