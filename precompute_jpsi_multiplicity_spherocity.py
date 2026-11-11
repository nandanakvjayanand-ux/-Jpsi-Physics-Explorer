from pathlib import Path
import numpy as np
import pandas as pd

# Run ONCE from Terminal, outside Streamlit. This creates compact CSVs for the app.
BASE = Path.home() / "Desktop" / "WEB-APP SIMLATION FILE "
FILE_ON = BASE / "jpsi_spherocity_multiplicity_CRon_MPIon_101.txt"
FILE_OFF = BASE / "jpsi_spherocity_multiplicity_CRoff_MPIoff_101.txt"
OUT = Path.home() / "Desktop" / "Jpsi-Physics-Explorer" / "data" / "multiplicity_spherocity"
OUT.mkdir(parents=True, exist_ok=True)

CHUNK = 250_000
NBINS = 20

def process(path, label):
    print(f"\nProcessing {label}: {path}")
    if not path.is_file():
        raise FileNotFoundError(path)
    mult_sum, mult_count = {}, {}
    edges = np.linspace(0.0, 1.0, NBINS + 1)
    s0_sum = np.zeros(NBINS)
    s0_jpsi_sum = np.zeros(NBINS)
    s0_count = np.zeros(NBINS, dtype=np.int64)
    hist = np.zeros(NBINS, dtype=np.int64)
    total_rows = 0
    total_jpsi = 0

    reader = pd.read_csv(
        path, sep=r"\s+", comment="#", header=None,
        usecols=[0, 1, 2, 3],
        names=["EventID", "Nch", "S0", "NJpsi"],
        dtype={"EventID": "int64", "Nch": "int32", "S0": "float64", "NJpsi": "int32"},
        chunksize=CHUNK, engine="c"
    )
    for i, chunk in enumerate(reader, 1):
        chunk = chunk.replace([np.inf, -np.inf], np.nan).dropna(subset=["Nch", "S0", "NJpsi"])
        total_rows += len(chunk)
        total_jpsi += int(chunk["NJpsi"].sum())
        grouped = chunk.groupby("Nch")["NJpsi"].agg(["sum", "count"])
        for nch, row in grouped.iterrows():
            k = int(nch)
            mult_sum[k] = mult_sum.get(k, 0.0) + float(row["sum"])
            mult_count[k] = mult_count.get(k, 0) + int(row["count"])

        s0 = chunk["S0"].to_numpy()
        nj = chunk["NJpsi"].to_numpy(dtype=float)
        valid = (s0 >= 0) & (s0 <= 1)
        if valid.any():
            idx = np.minimum(np.searchsorted(edges, s0[valid], side="right") - 1, NBINS - 1)
            np.add.at(hist, idx, 1)
            np.add.at(s0_count, idx, 1)
            np.add.at(s0_sum, idx, s0[valid])
            np.add.at(s0_jpsi_sum, idx, nj[valid])
        print(f"  chunks: {i} | accepted rows read: {total_rows:,}", end="\r")

    keys = sorted(mult_sum)
    mult = pd.DataFrame({
        "configuration": label,
        "Nch": keys,
        "mean_NJpsi": [mult_sum[k] / mult_count[k] for k in keys],
        "events": [mult_count[k] for k in keys],
    })
    s0mean = np.divide(s0_sum, s0_count, out=np.full(NBINS, np.nan), where=s0_count > 0)
    s0yield = np.divide(s0_jpsi_sum, s0_count, out=np.full(NBINS, np.nan), where=s0_count > 0)
    spher = pd.DataFrame({
        "configuration": label, "mean_S0": s0mean, "mean_NJpsi": s0yield, "events": s0_count
    })
    distribution = pd.DataFrame({
        "configuration": label, "bin_left": edges[:-1], "bin_right": edges[1:],
        "events": hist, "probability_density": hist / max(hist.sum(), 1) / np.diff(edges)
    })
    summary = {
        "configuration": label, "accepted_events": total_rows, "total_Jpsi_candidates": total_jpsi,
        "source_file": path.name
    }
    print(f"\nCompleted {label}: {total_rows:,} rows; {total_jpsi:,} J/ψ candidates.")
    return mult, spher, distribution, summary

on = process(FILE_ON, "CR ON + MPI ON")
off = process(FILE_OFF, "CR OFF + MPI OFF")

pd.concat([on[0], off[0]], ignore_index=True).to_csv(OUT / "multiplicity_yield.csv", index=False)
pd.concat([on[1], off[1]], ignore_index=True).to_csv(OUT / "spherocity_yield.csv", index=False)
pd.concat([on[2], off[2]], ignore_index=True).to_csv(OUT / "spherocity_distribution.csv", index=False)
pd.DataFrame([on[3], off[3]]).to_csv(OUT / "sample_summary.csv", index=False)

print("\nAll compact result files saved to:")
print(OUT)
print("You can now open the Streamlit page. It will not process the original large files.")
