J/psi Physics Explorer — event-topology comparison update

This update adds one Streamlit multipage module and the 12 event-level datasets used by it.

INSTALL INTO YOUR EXISTING PROJECT
1. Copy pages/08_Event_Topology_CR_MPI.py into your project's pages/ folder.
2. Copy the entire data/topology/ folder into your project's data/ folder.
3. Keep the existing app and other pages unchanged.
4. Refresh the Streamlit browser tab. The new page appears in the sidebar as “08 Event Topology CR MPI”.

The page combines seeds 103 and 104, applies selectable pT and rapidity cuts, and plots unit-area pT distributions for integrated, jetty and isotropic classes. It deliberately does not claim absolute cross sections because the matching generated-event totals and sigmaGen values were not supplied with these event-level files.

Dependencies: streamlit, numpy, pandas, plotly.
