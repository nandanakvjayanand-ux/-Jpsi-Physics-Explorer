import streamlit as st

st.set_page_config(
    page_title="Underlying Event Effects and Event-Topology Dependence",
    page_icon="⚛️",
    layout="wide"
)

# --------------------------------------------------
# GLOBAL DESIGN
# --------------------------------------------------

st.markdown("""
<style>
.stApp {
    background: #0b0f19;
    color: #e7eaf2;
}

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Main research title */
.hero {
    background: linear-gradient(120deg, #151e32, #202b42);
    border: 1px solid #405777;
    border-radius: 16px;
    padding: 38px 42px;
    margin-bottom: 22px;
}

.kicker {
    color: #91a9d0;
    font-size: 0.78rem;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    margin-bottom: 16px;
}

.hero h1 {
    color: #f4f6fb;
    font-size: clamp(1.8rem, 3.2vw, 2.7rem);
    line-height: 1.25;
    font-weight: 750;
    margin-bottom: 0;
}

.hero-description {
    color: #b7c4d9;
    font-size: 1.02rem;
    line-height: 1.7;
    margin-top: 17px;
    max-width: 1000px;
}

/* Researcher and advisor: compact cards */
.person-card {
    background: #151e2e;
    border: 1px solid #405777;
    border-radius: 11px;
    padding: 13px 18px;
    min-height: 88px;
}

.person-label {
    color: #91a9d0;
    font-size: 0.68rem;
    letter-spacing: 1.4px;
    text-transform: uppercase;
    margin-bottom: 7px;
}

.person-name {
    color: #f0f2f7;
    font-size: 0.96rem;
    font-weight: 600;
    line-height: 1.4;
}

/* Section headings */
.section-heading {
    color: #e7eaf2;
    font-size: 1.55rem;
    font-weight: 700;
    margin-top: 2.2rem;
    margin-bottom: 1rem;
}

/* Collision framework cards */
.info-card {
    background: #151e2e;
    border: 1px solid #405777;
    border-radius: 12px;
    padding: 19px 20px;
    min-height: 135px;
}

.info-label {
    color: #91a9d0;
    font-size: 0.78rem;
    letter-spacing: 1px;
    margin-bottom: 13px;
}

.info-value {
    color: #f0f2f7;
    font-size: 1.65rem;
    font-weight: 700;
    line-height: 1.3;
}

.info-description {
    color: #91a9d0;
    font-size: 0.83rem;
    margin-top: 7px;
}

/* Research overview */
.overview {
    color: #c4ccda;
    font-size: 1rem;
    line-height: 1.85;
}

/* Generator configuration cards */
.config-card {
    background: #151e2e;
    border: 1px solid #405777;
    border-radius: 12px;
    padding: 20px 23px;
    min-height: 135px;
}

.config-card h3 {
    color: #f0f2f7;
    font-size: 1.2rem;
    margin-bottom: 12px;
}

.config-card p {
    color: #b7c4d9;
    font-size: 0.95rem;
    line-height: 1.7;
}

/* Analysis objectives */
.objective {
    color: #c4ccda;
    font-size: 0.98rem;
    line-height: 1.7;
    padding: 5px 0;
}

/* Remove unnecessary Streamlit decoration */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# RESEARCH TITLE
# --------------------------------------------------

st.html("""
<div class="hero">

    <div class="kicker">
        Monte Carlo Research Project
    </div>

    <h1>
        Underlying Event Effects and Event-Topology
        Dependence of Inclusive J/ψ Production
        in pp Collisions at √s = 13 TeV
    </h1>

    <div class="hero-description">
        A Monte Carlo study of inclusive charmonium production
        investigating the influence of multiparton interactions,
        colour reconnection, charged-particle multiplicity and
        transverse event topology.
    </div>

</div>
""")


# --------------------------------------------------
# RESEARCHER AND ADVISOR — single compact credit box
st.markdown("""
<div class="person-card" style="
    padding: 17px 24px;
    min-height: 0;
    height: auto;
    margin: 0 0 24px 0;
">
    <div style="
        color: #b7c4d9;
        font-size: 1rem;
        line-height: 1.7;
        text-align: left;
    ">
        By
        <span style="color:#f0f2f7;font-weight:650;">
            Nandana Jayanand Kallari Vattath
        </span>
        <span style="color:#91a9d0;padding:0 9px;">·</span>
        Supervised by
        <span style="color:#f0f2f7;font-weight:650;">
            Bibhuti Parida
        </span>
    </div>
</div>
"""

, unsafe_allow_html=True)


# COLLISION FRAMEWORK
# --------------------------------------------------

st.markdown(
    '<div class="section-heading">Collision Framework</div>',
    unsafe_allow_html=True
)

a, b, c = st.columns(3, gap="medium")

framework = [
    (a, "Collision system", "pp", "Proton–proton collisions"),
    (b, "Centre-of-mass energy", "13 TeV", "√s = 13 TeV"),
    (c, "Event generator", "PYTHIA 8.317", "Monte Carlo simulation")
]

for column, label, value, description in framework:
    with column:
        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">{label}</div>
            <div class="info-value">{value}</div>
            <div class="info-description">{description}</div>
        </div>
        """, unsafe_allow_html=True)


# --------------------------------------------------
# RESEARCH OVERVIEW
# --------------------------------------------------

st.markdown(
    '<div class="section-heading">Research Overview</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="overview">

Inclusive J/ψ production in high-energy proton–proton collisions
provides a way to investigate heavy-quark production and
hadronisation in a complex event environment.

<br><br>

This study compares two PYTHIA configurations in which
multiparton interactions (MPI) and colour reconnection (CR)
are varied simultaneously. Their influence is examined through
kinematic distributions, charged-particle multiplicity and
transverse-spherocity-based event classification.

<br><br>

The simulated results are compared with experimental measurements
from ALICE.

</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# GENERATOR CONFIGURATIONS
# --------------------------------------------------

st.markdown(
    '<div class="section-heading">Generator Configurations</div>',
    unsafe_allow_html=True
)

g1, g2 = st.columns(2, gap="medium")

with g1:
    st.markdown("""
    <div class="config-card" style="border-left:3px solid #4388c5;">
        <h3>MPI + CR ON</h3>
        <p>
            Multiparton interactions enabled.<br>
            Colour reconnection enabled.
        </p>
    </div>
    """, unsafe_allow_html=True)

with g2:
    st.markdown("""
    <div class="config-card" style="border-left:3px solid #a94f4f;">
        <h3>MPI + CR OFF</h3>
        <p>
            Multiparton interactions disabled.<br>
            Colour reconnection disabled.
        </p>
    </div>
    """, unsafe_allow_html=True)


# --------------------------------------------------
# ANALYSIS OBJECTIVES
# --------------------------------------------------

st.markdown(
    '<div class="section-heading">Analysis Objectives</div>',
    unsafe_allow_html=True
)

objectives = [
    "Inclusive J/ψ transverse-momentum distributions.",
    "Rapidity-dependent production characteristics.",
    "Charged-particle multiplicity dependence.",
    "Transverse spherocity and event topology.",
    "Comparison of jetty and isotropic events.",
    "Comparison with ALICE experimental measurements."
]

for item in objectives:
    st.markdown(
        f'<div class="objective">• {item}</div>',
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

st.caption(
    "PYTHIA 8.317 · pp collisions · √s = 13 TeV · "
    "Experimental reference: ALICE"
)

