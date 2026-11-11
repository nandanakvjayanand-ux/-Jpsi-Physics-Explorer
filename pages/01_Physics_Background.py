import streamlit as st

st.set_page_config(
    page_title="Physics Background",
    page_icon="⚛️",
    layout="wide"
)

st.title("Physics Background")

st.markdown("""
An introduction to the physical processes behind inclusive
J/ψ production and the underlying event in high-energy
proton–proton collisions.
""")

st.divider()

# 01 Charmonium production
st.header("01 | Charmonium Production")

st.markdown("""
The J/ψ meson is a charmonium state consisting of a charm quark
and an anti-charm quark. It is a useful probe of heavy-quark
production and hadronisation in high-energy collisions.
""")

st.latex(r"J/\psi = c\bar{c}")

with st.expander("For readers new to particle physics"):
    st.markdown("""
    Protons are not elementary particles. They contain quarks and
    gluons, collectively called partons.

    During a high-energy collision, these constituents can interact
    and produce new particles. A charm quark and an anti-charm quark
    can form a bound state called charmonium. The J/ψ is one such state.

    It is reconstructed experimentally through its decay into
    a pair of oppositely charged leptons, such as muons or electrons.
    """)

st.divider()

# 02 MPI
st.header("02 | Multiparton Interactions")

st.markdown("""
Multiparton interactions (MPI) describe additional parton–parton
interactions occurring within the same proton–proton collision.

Alongside the primary hard scattering, these interactions contribute
to the underlying event and influence the production of final-state
particles.
""")

with st.expander("For readers new to particle physics"):
    st.markdown("""
    A proton–proton collision is not necessarily just one interaction
    between two individual constituents.

    Several partons from the incoming protons may participate in
    interactions during the same collision. These additional
    interactions contribute particles to the final state.

    This activity is called the underlying event.
    """)

st.divider()

# 03 CR
st.header("03 | Colour Reconnection")

st.markdown("""
Colour reconnection (CR) describes changes in the colour connections
between partons before hadronisation.

In the PYTHIA framework, colour reconnection can affect how partons
are connected into colour structures and consequently influence
the properties of the produced hadronic final state.
""")

with st.expander("For readers new to particle physics"):
    st.markdown("""
    Quarks and gluons carry a property called colour charge.

    They cannot normally be observed as isolated particles.
    Instead, they form colour-neutral hadrons.

    Colour reconnection is a modelling mechanism that changes
    the connections between partons before they form hadrons.
    """)

st.divider()

# 04 Research questions
st.header("04 | Research Questions")

st.markdown("""
This project investigates:
""")

for item in [
    "The combined effect of MPI and CR on inclusive J/ψ production.",
    "Changes in transverse-momentum distributions.",
    "Multiplicity-dependent J/ψ production.",
    "Event-shape dependence using transverse spherocity.",
    "Differences between jetty and isotropic events.",
    "Comparison of simulated production trends with ALICE measurements."
]:
    st.markdown(f"- {item}")

st.info(
    "MPI and colour reconnection are switched on or off together "
    "in the main comparison. Their individual contributions cannot "
    "be isolated from these two configurations alone."
)

st.divider()

# 05 Decay channels
st.header("05 | J/ψ Decay Channels")

st.markdown("""
The analysis uses dilepton decay channels to reconstruct
J/ψ candidates in different rapidity regions.
""")

forward, middle = st.columns(2)

with forward:
    st.subheader("Forward rapidity")
    st.latex(r"J/\psi \rightarrow \mu^+ + \mu^-")
    st.metric("Rapidity selection", r"2.5 < |y| < 4.0")
    st.markdown("""
    The dimuon channel is used for the forward-rapidity analysis
    and comparison with experimental measurements.
    """)

with middle:
    st.subheader("Midrapidity")
    st.latex(r"J/\psi \rightarrow e^+ + e^-")
    st.metric("Rapidity selection", r"|y| < 0.9")
    st.markdown("""
    The dielectron channel is considered for the midrapidity analysis.
    """)

st.divider()

# 06 Kinematic selections
st.header("06 | Kinematic Selections")

st.subheader("Forward dimuon analysis")
st.latex(r"2.5 < |y| < 4.0")
st.latex(r"J/\psi \rightarrow \mu^+ \mu^-")

st.subheader("Midrapidity dielectron analysis")
st.latex(r"|y| < 0.9")
st.latex(r"J/\psi \rightarrow e^+ e^-")

st.markdown("""
The reconstructed dilepton four-momentum is used to obtain
the kinematic properties of the J/ψ candidate.
""")

st.divider()

# 07 Spherocity
st.header("07 | Transverse Spherocity")

st.markdown("""
Transverse spherocity characterises the topology of the final
state in the transverse plane. It distinguishes events with a
jet-like momentum distribution from events with a more uniform
azimuthal distribution.
""")

st.latex(r"""
S_0 = \frac{\pi^2}{4}
\left(
\frac{\min_{\hat{n}}\sum_i
|\vec{p}_{T,i}\times\hat{n}|}
{\sum_i p_{T,i}}
\right)^2
""")

st.markdown("""
Here, the minimisation is performed over the unit vector
in the transverse plane. The observable ranges from zero
to one.
""")

st.subheader("Charged-particle selection")

p1, p2, p3 = st.columns(3)

with p1:
    st.metric("Transverse momentum", "pT ≥ 0.15 GeV/c")

with p2:
    st.metric("Pseudorapidity", "|η| ≤ 1.0")

with p3:
    st.metric("Multiplicity requirement", "Nch ≥ 5")

st.markdown("""
Events containing fewer than five selected charged particles
are excluded from the spherocity analysis.
""")

st.subheader("Event topology")

jetty, isotropic = st.columns(2)

with jetty:
    st.markdown("### Jetty events")
    st.latex(r"S_0 \rightarrow 0")
    st.markdown("""
    Transverse momentum is concentrated preferentially
    along a particular direction in the transverse plane.
    """)
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Jet_event.svg/512px-Jet_event.svg.png",
        caption="Illustration of a jet-like event topology.",
        use_container_width=True
    )

with isotropic:
    st.markdown("### Isotropic events")
    st.latex(r"S_0 \rightarrow 1")
    st.markdown("""
    Transverse momentum is distributed more uniformly
    in azimuth around the beam axis.
    """)

st.divider()

# 08 Research interpretation
st.header("08 | Physical Interpretation")

st.markdown("""
The comparison of the two generator configurations allows
the study of how the combined MPI and CR settings influence
inclusive J/ψ production and the properties of the underlying event.

The kinematic distributions and event-shape observables provide
complementary ways to examine these effects.
""")

st.divider()

# 09 Limitations
st.header("09 | Scope of the Comparison")

st.markdown("""
The principal comparison changes MPI and colour reconnection
simultaneously. Consequently, differences between the configurations
represent the combined response to these generator settings.

Separating the individual effects would require additional
simulations in which MPI and CR are varied independently.
""")

st.divider()

# 10 | The Entire Project in One Picture
st.header("10 | The Entire Project in One Picture")

st.markdown("""
The following sequence summarises the logic of the research,
from the initial collision to the final comparison.
""")

st.markdown("---")

st.markdown("### Proton–Proton Collision")
st.latex(r"pp \qquad \sqrt{s}=13\ \mathrm{TeV}")

steps = [
    ("01", "Partonic Interactions",
     "Hard scattering + underlying event",
     "The incoming protons interact through their constituent quarks and gluons."),

    ("02", "MPI and Colour Reconnection",
     "Two combined generator configurations",
     "MPI and CR are switched on together or off together."),

    ("03", "Hadronisation and J/ψ Production",
     "Charmonium formation and final-state particles",
     "Partons evolve into hadrons, including reconstructed J/ψ candidates."),

    ("04", "Kinematic and Event-Shape Analysis",
     "pT · Rapidity · Multiplicity · Spherocity",
     "Generated events are studied using kinematic and event-topology observables."),

    ("05", "Comparison with ALICE Measurements",
     "Experimental reference",
     "Simulated production trends are compared with ALICE measurements.")
]

for number, title, subtitle, explanation in steps:
    st.markdown(f"#### {number} | {title}")
    with st.container(border=True):
        st.markdown(f"**{title}**")
        st.caption(subtitle)
        st.write(explanation)

    if number != "05":
        st.markdown(
            "<div style='text-align:center;color:#8FA7CA;font-size:1.5rem;'>↓</div>",
            unsafe_allow_html=True
        )

st.success("End of the research overview.")
