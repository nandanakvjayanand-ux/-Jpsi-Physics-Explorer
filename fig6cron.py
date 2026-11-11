import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# FILES
# ============================================================

# ============================================================
# FILES
# ============================================================

FILE_111 = '/Users/nandanajayanand/Desktop/WEB-APP SIMLATION FILE /alice_meanpt_spherocity_13tev_CRON_111.txt.gz'
FILE_112 = '/Users/nandanajayanand/Desktop/WEB-APP SIMLATION FILE /alice_meanpt_spherocity_13tev_CRON_112.txt.gz'


# ============================================================
# ALICE FILES
# ============================================================

ALICE_TABLE7 = '/Users/nandanajayanand/Desktop/WEB APP ALICE:LHCB DATA FILE /Table7.csv'
ALICE_TABLE8 = '/Users/nandanajayanand/Desktop/WEB APP ALICE:LHCB DATA FILE /Table8.csv'
ALICE_TABLE17 = '/Users/nandanajayanand/Desktop/WEB APP ALICE:LHCB DATA FILE /Table17.csv'


# ============================================================
# SETTINGS
# ============================================================

DELTA_ETA = 1.6

MIN_EVENTS = 50

CHUNK_SIZE = 500_000

# ------------------------------------------------------------
# IMPORTANT:
# Remove the low-multiplicity region from the PLOT ONLY.
# The analysis itself still uses the complete dataset.
# ------------------------------------------------------------

PLOT_MIN_DNDeta = 10.0

# PYTHIA marker size
PYTHIA_MARKER_SIZE = 13


# ============================================================
# READ ALICE
# ============================================================

def read_alice(filename):

    print("\nReading ALICE:")
    print(filename)

    if not os.path.exists(filename):

        raise FileNotFoundError(
            f"\nALICE file not found:\n{filename}"
        )

    df = pd.read_csv(
        filename,
        skiprows=12
    )

    print(
        "Columns:",
        list(df.columns)
    )

    return df


# ============================================================
# ALICE DATA EXTRACTION
# ============================================================

def prepare_alice(df):

    # --------------------------------------------------------
    # X
    # --------------------------------------------------------

    x = pd.to_numeric(
        df["<dNch/dEta>"],
        errors="coerce"
    ).to_numpy()


    # --------------------------------------------------------
    # Y
    # --------------------------------------------------------

    y = pd.to_numeric(
        df["<pT> [GEV/C]"],
        errors="coerce"
    ).to_numpy()


    # --------------------------------------------------------
    # STATISTICAL UNCERTAINTY
    # --------------------------------------------------------

    stat_plus = pd.to_numeric(
        df["stat +"],
        errors="coerce"
    ).to_numpy()

    stat_minus = pd.to_numeric(
        df["stat -"],
        errors="coerce"
    ).to_numpy()

    stat = np.maximum(
        np.abs(stat_plus),
        np.abs(stat_minus)
    )


    # --------------------------------------------------------
    # SYSTEMATIC UNCERTAINTY
    # --------------------------------------------------------

    sys_plus = pd.to_numeric(
        df["sys,total +"],
        errors="coerce"
    ).to_numpy()

    sys_minus = pd.to_numeric(
        df["sys,total -"],
        errors="coerce"
    ).to_numpy()

    syst = np.maximum(
        np.abs(sys_plus),
        np.abs(sys_minus)
    )


    # --------------------------------------------------------
    # REMOVE INVALID ROWS
    # --------------------------------------------------------

    mask = (

        np.isfinite(x)
        &
        np.isfinite(y)
        &
        np.isfinite(stat)
        &
        np.isfinite(syst)

    )


    return (
        x[mask],
        y[mask],
        stat[mask],
        syst[mask]
    )


# ============================================================
# LOAD ALICE
# ============================================================

alice_all = read_alice(
    ALICE_TABLE7
)

alice_jet = read_alice(
    ALICE_TABLE8
)

alice_iso = read_alice(
    ALICE_TABLE17
)


alice_all_x, alice_all_y, \
alice_all_stat, alice_all_sys = \
    prepare_alice(alice_all)


alice_jet_x, alice_jet_y, \
alice_jet_stat, alice_jet_sys = \
    prepare_alice(alice_jet)


alice_iso_x, alice_iso_y, \
alice_iso_stat, alice_iso_sys = \
    prepare_alice(alice_iso)


# ============================================================
# DETERMINE MULTIPLICITY BIN EDGES
# ============================================================

def make_bin_edges(alice_x):

    edges = np.zeros(
        len(alice_x) + 1
    )


    # --------------------------------------------------------
    # INTERIOR EDGES
    # --------------------------------------------------------

    for i in range(
        len(alice_x) - 1
    ):

        edges[i + 1] = (
            alice_x[i] +
            alice_x[i + 1]
        ) / 2.0


    # --------------------------------------------------------
    # FIRST EDGE
    # --------------------------------------------------------

    first_width = (
        alice_x[1] -
        alice_x[0]
    )

    edges[0] = (
        alice_x[0] -
        first_width / 2.0
    )


    # --------------------------------------------------------
    # LAST EDGE
    # --------------------------------------------------------

    last_width = (
        alice_x[-1] -
        alice_x[-2]
    )

    edges[-1] = (
        alice_x[-1] +
        last_width / 2.0
    )


    return edges


# ============================================================
# CREATE BIN EDGES
# ============================================================

edges_all = make_bin_edges(
    alice_all_x
)

edges_jet = make_bin_edges(
    alice_jet_x
)

edges_iso = make_bin_edges(
    alice_iso_x
)


# ============================================================
# PYTHIA STORAGE
# ============================================================

S0_BINS = 10000

S0_EDGES = np.linspace(
    0.0,
    1.0,
    S0_BINS + 1
)


# ============================================================
# FUNCTION TO CREATE ACCUMULATORS
# ============================================================

def create_accumulators(nbins):

    accum = {

        "count":
            np.zeros(
                nbins,
                dtype=np.int64
            ),

        "sum_pt":
            np.zeros(
                nbins,
                dtype=np.float64
            ),

        "sum_pt2":
            np.zeros(
                nbins,
                dtype=np.float64
            ),

        "sum_dndeta":
            np.zeros(
                nbins,
                dtype=np.float64
            ),

        "s0_hist":
            np.zeros(
                (nbins, S0_BINS),
                dtype=np.int64
            )

    }

    return accum


# ============================================================
# ACCUMULATORS
# ============================================================

acc_all = create_accumulators(
    len(alice_all_x)
)

acc_jet = create_accumulators(
    len(alice_jet_x)
)

acc_iso = create_accumulators(
    len(alice_iso_x)
)


# ============================================================
# PROCESS ONE FILE
# ============================================================

def process_file(
    filename,
    acc_all,
    acc_jet,
    acc_iso
):

    print("\n============================================")
    print("PROCESSING PYTHIA FILE")
    print("============================================")
    print(filename)


    total_rows = 0
    valid_rows = 0


    reader = pd.read_csv(

        filename,

        sep=r"\s+",

        header=None,

        names=[
            "dNchdEta",
            "Nch",
            "meanPt",
            "S0"
        ],

        chunksize=CHUNK_SIZE,

        dtype=np.float64
    )


    # ========================================================
    # LOOP OVER CHUNKS
    # ========================================================

    for chunk in reader:

        total_rows += len(chunk)


        dndeta = chunk[
            "dNchdEta"
        ].to_numpy()

        meanpt = chunk[
            "meanPt"
        ].to_numpy()

        s0 = chunk[
            "S0"
        ].to_numpy()


        # ----------------------------------------------------
        # BASIC VALIDITY
        # ----------------------------------------------------

        valid = (

            np.isfinite(dndeta)
            &
            np.isfinite(meanpt)
            &
            np.isfinite(s0)

            &
            (dndeta >= 0)

            &
            (meanpt > 0)

            &
            (s0 >= 0)

            &
            (s0 <= 1)

        )


        dndeta = dndeta[valid]

        meanpt = meanpt[valid]

        s0 = s0[valid]


        valid_rows += len(
            dndeta
        )


        # ====================================================
        # 0-100%
        # ====================================================

        bin_index = np.searchsorted(
            edges_all,
            dndeta,
            side="right"
        ) - 1


        good = (

            (bin_index >= 0)
            &
            (bin_index < len(alice_all_x))

        )


        b = bin_index[good]

        pt = meanpt[good]

        dn = dndeta[good]

        s = s0[good]


        np.add.at(
            acc_all["count"],
            b,
            1
        )

        np.add.at(
            acc_all["sum_pt"],
            b,
            pt
        )

        np.add.at(
            acc_all["sum_pt2"],
            b,
            pt ** 2
        )

        np.add.at(
            acc_all["sum_dndeta"],
            b,
            dn
        )


        # ----------------------------------------------------
        # S0 HISTOGRAM — 0-100%
        # ----------------------------------------------------

        sbin = np.searchsorted(
            S0_EDGES,
            s,
            side="right"
        ) - 1


        good_s = (

            (sbin >= 0)
            &
            (sbin < S0_BINS)

        )


        np.add.at(

            acc_all["s0_hist"],

            (
                b[good_s],
                sbin[good_s]
            ),

            1

        )


        # ====================================================
        # 0-10%
        # ====================================================

        bin_index = np.searchsorted(
            edges_jet,
            dndeta,
            side="right"
        ) - 1


        good = (

            (bin_index >= 0)
            &
            (bin_index < len(alice_jet_x))

        )


        b = bin_index[good]

        pt = meanpt[good]

        dn = dndeta[good]

        s = s0[good]


        np.add.at(
            acc_jet["count"],
            b,
            1
        )

        np.add.at(
            acc_jet["sum_pt"],
            b,
            pt
        )

        np.add.at(
            acc_jet["sum_pt2"],
            b,
            pt ** 2
        )

        np.add.at(
            acc_jet["sum_dndeta"],
            b,
            dn
        )


        sbin = np.searchsorted(
            S0_EDGES,
            s,
            side="right"
        ) - 1


        good_s = (

            (sbin >= 0)
            &
            (sbin < S0_BINS)

        )


        np.add.at(

            acc_jet["s0_hist"],

            (
                b[good_s],
                sbin[good_s]
            ),

            1

        )


        # ====================================================
        # 90-100%
        # ====================================================

        bin_index = np.searchsorted(
            edges_iso,
            dndeta,
            side="right"
        ) - 1


        good = (

            (bin_index >= 0)
            &
            (bin_index < len(alice_iso_x))

        )


        b = bin_index[good]

        pt = meanpt[good]

        dn = dndeta[good]

        s = s0[good]


        np.add.at(
            acc_iso["count"],
            b,
            1
        )

        np.add.at(
            acc_iso["sum_pt"],
            b,
            pt
        )

        np.add.at(
            acc_iso["sum_pt2"],
            b,
            pt ** 2
        )

        np.add.at(
            acc_iso["sum_dndeta"],
            b,
            dn
        )


        sbin = np.searchsorted(
            S0_EDGES,
            s,
            side="right"
        ) - 1


        good_s = (

            (sbin >= 0)
            &
            (sbin < S0_BINS)

        )


        np.add.at(

            acc_iso["s0_hist"],

            (
                b[good_s],
                sbin[good_s]
            ),

            1

        )


        # ----------------------------------------------------
        # PROGRESS
        # ----------------------------------------------------

        if (
            total_rows // 5_000_000
            !=
            (total_rows - len(chunk)) // 5_000_000
        ):

            print(
                f"Processed "
                f"{total_rows:,} rows"
            )


    print(
        "\nTotal rows:",
        f"{total_rows:,}"
    )

    print(
        "Valid rows:",
        f"{valid_rows:,}"
    )


# ============================================================
# PROCESS FILE 111
# ============================================================

process_file(

    FILE_111,

    acc_all,

    acc_jet,

    acc_iso

)


# ============================================================
# PROCESS FILE 112
# ============================================================

process_file(

    FILE_112,

    acc_all,

    acc_jet,

    acc_iso

)


# ============================================================
# CALCULATE ORDINARY 0-100% PYTHIA
# ============================================================

def calculate_all_results(
    acc,
    alice_x
):

    x_values = []
    y_values = []
    errors = []


    for i in range(
        len(alice_x)
    ):

        n = acc["count"][i]


        if n < MIN_EVENTS:

            continue


        mean_pt = (
            acc["sum_pt"][i]
            /
            n
        )


        variance = (

            acc["sum_pt2"][i]
            -
            n * mean_pt**2

        ) / (n - 1)


        variance = max(
            variance,
            0.0
        )


        std = np.sqrt(
            variance
        )


        error = (
            std
            /
            np.sqrt(n)
        )


        x_values.append(
            alice_x[i]
        )

        y_values.append(
            mean_pt
        )

        errors.append(
            error
        )


    return (

        np.array(x_values),

        np.array(y_values),

        np.array(errors)

    )


# ============================================================
# SPHEROcity PERCENTILE
# ============================================================

def histogram_percentile(
    histogram,
    percentile
):

    total = histogram.sum()


    if total == 0:

        return np.nan


    target = (
        percentile / 100.0
    ) * total


    cumulative = np.cumsum(
        histogram
    )


    index = np.searchsorted(
        cumulative,
        target
    )


    index = min(
        index,
        len(histogram) - 1
    )


    return (

        S0_EDGES[index]

        +

        S0_EDGES[index + 1]

    ) / 2.0


# ============================================================
# SPHEROcity THRESHOLDS
# ============================================================

def get_spherocity_thresholds(

    acc,

    n_bins

):

    low_thresholds = np.full(
        n_bins,
        np.nan
    )

    high_thresholds = np.full(
        n_bins,
        np.nan
    )


    for i in range(
        n_bins
    ):

        histogram = acc[
            "s0_hist"
        ][i]


        if histogram.sum() == 0:

            continue


        low_thresholds[i] = \
            histogram_percentile(
                histogram,
                10
            )


        high_thresholds[i] = \
            histogram_percentile(
                histogram,
                90
            )


    return (
        low_thresholds,
        high_thresholds
    )


# ============================================================
# THRESHOLDS
# ============================================================

jet_low_s0, jet_high_s0 = \
    get_spherocity_thresholds(
        acc_jet,
        len(alice_jet_x)
    )

iso_low_s0, iso_high_s0 = \
    get_spherocity_thresholds(
        acc_iso,
        len(alice_iso_x)
    )


# ============================================================
# SECOND PASS:
# SPHEROcity-SELECTED MEAN pT
# ============================================================

def second_pass_spherocity(

    filename,

    acc,

    alice_x,

    edges,

    percentile_type

):

    n_bins = len(
        alice_x
    )


    sum_pt = np.zeros(
        n_bins,
        dtype=np.float64
    )

    sum_pt2 = np.zeros(
        n_bins,
        dtype=np.float64
    )

    count = np.zeros(
        n_bins,
        dtype=np.int64
    )


    reader = pd.read_csv(

        filename,

        sep=r"\s+",

        header=None,

        names=[
            "dNchdEta",
            "Nch",
            "meanPt",
            "S0"
        ],

        chunksize=CHUNK_SIZE,

        dtype=np.float64

    )


    for chunk in reader:

        dndeta = chunk[
            "dNchdEta"
        ].to_numpy()

        meanpt = chunk[
            "meanPt"
        ].to_numpy()

        s0 = chunk[
            "S0"
        ].to_numpy()


        valid = (

            np.isfinite(dndeta)
            &
            np.isfinite(meanpt)
            &
            np.isfinite(s0)

            &
            (dndeta >= 0)

            &
            (meanpt > 0)

            &
            (s0 >= 0)

            &
            (s0 <= 1)

        )


        dndeta = dndeta[valid]

        meanpt = meanpt[valid]

        s0 = s0[valid]


        bin_index = np.searchsorted(

            edges,

            dndeta,

            side="right"

        ) - 1


        good = (

            (bin_index >= 0)
            &
            (bin_index < n_bins)

        )


        b = bin_index[good]

        pt = meanpt[good]

        s = s0[good]


        for ibin in np.unique(b):

            mask_bin = (
                b == ibin
            )

            s_values = s[
                mask_bin
            ]

            pt_values = pt[
                mask_bin
            ]


            if percentile_type == "jet":

                threshold = \
                    jet_low_s0[ibin]

                if not np.isfinite(
                    threshold
                ):

                    continue

                selected = (
                    s_values <= threshold
                )


            else:

                threshold = \
                    iso_high_s0[ibin]

                if not np.isfinite(
                    threshold
                ):

                    continue

                selected = (
                    s_values >= threshold
                )


            selected_pt = pt_values[
                selected
            ]


            if len(
                selected_pt
            ) == 0:

                continue


            sum_pt[ibin] += \
                selected_pt.sum()

            sum_pt2[ibin] += \
                np.sum(
                    selected_pt ** 2
                )

            count[ibin] += \
                len(selected_pt)


    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    x_values = []
    y_values = []
    errors = []


    for i in range(
        n_bins
    ):

        n = count[i]


        if n < 10:

            continue


        mean = (
            sum_pt[i]
            /
            n
        )


        variance = (

            sum_pt2[i]
            -
            n * mean**2

        ) / (n - 1)


        variance = max(
            variance,
            0.0
        )


        std = np.sqrt(
            variance
        )


        error = (
            std
            /
            np.sqrt(n)
        )


        x_values.append(
            alice_x[i]
        )

        y_values.append(
            mean
        )

        errors.append(
            error
        )


    return (

        np.array(x_values),

        np.array(y_values),

        np.array(errors)

    )


# ============================================================
# COMPLETE-SAMPLE THRESHOLDS
# ============================================================

jet_low_s0, _ = \
    get_spherocity_thresholds(
        acc_jet,
        len(alice_jet_x)
    )

_, iso_high_s0 = \
    get_spherocity_thresholds(
        acc_iso,
        len(alice_iso_x)
    )


# ============================================================
# SECOND PASS — FILE 111
# ============================================================

jet_x1, jet_y1, jet_e1 = \
    second_pass_spherocity(

        FILE_111,

        acc_jet,

        alice_jet_x,

        edges_jet,

        "jet"

    )


iso_x1, iso_y1, iso_e1 = \
    second_pass_spherocity(

        FILE_111,

        acc_iso,

        alice_iso_x,

        edges_iso,

        "iso"

    )


# ============================================================
# SECOND PASS — FILE 112
# ============================================================

jet_x2, jet_y2, jet_e2 = \
    second_pass_spherocity(

        FILE_112,

        acc_jet,

        alice_jet_x,

        edges_jet,

        "jet"

    )


iso_x2, iso_y2, iso_e2 = \
    second_pass_spherocity(

        FILE_112,

        acc_iso,

        alice_iso_x,

        edges_iso,

        "iso"

    )


# ============================================================
# COMBINE RESULTS
# ============================================================

def combine_results(
    x1,
    y1,
    e1,
    x2,
    y2,
    e2
):

    if len(x1) == 0:
        return x2, y2, e2

    if len(x2) == 0:
        return x1, y1, e1


    common_x = []
    combined_y = []
    combined_e = []


    for i, x in enumerate(x1):

        matches = np.where(
            np.isclose(
                x2,
                x,
                atol=1e-8
            )
        )[0]


        if len(matches) == 0:
            continue


        j = matches[0]


        if e1[i] > 0 and e2[j] > 0:

            w1 = 1.0 / e1[i]**2
            w2 = 1.0 / e2[j]**2

            y = (
                w1 * y1[i]
                +
                w2 * y2[j]
            ) / (
                w1 + w2
            )

            e = 1.0 / np.sqrt(
                w1 + w2
            )

        else:

            y = (
                y1[i] +
                y2[j]
            ) / 2.0

            e = (
                e1[i] +
                e2[j]
            ) / 2.0


        common_x.append(x)

        combined_y.append(y)

        combined_e.append(e)


    return (

        np.array(common_x),

        np.array(combined_y),

        np.array(combined_e)

    )


# ============================================================
# COMBINED SPHEROcity RESULTS
# ============================================================

jet_x, jet_y, jet_err = \
    combine_results(

        jet_x1,
        jet_y1,
        jet_e1,

        jet_x2,
        jet_y2,
        jet_e2

    )


iso_x, iso_y, iso_err = \
    combine_results(

        iso_x1,
        iso_y1,
        iso_e1,

        iso_x2,
        iso_y2,
        iso_e2

    )


# ============================================================
# 0-100% PYTHIA
# ============================================================

py_all_x, py_all_y, py_all_err = \
    calculate_all_results(

        acc_all,

        alice_all_x

    )


# ============================================================
# PUBLICATION STYLE
# ============================================================

plt.rcParams.update({

    "font.family": "serif",

    "mathtext.fontset": "stix",

    "font.size": 18,

    "axes.labelsize": 22,

    "axes.titlesize": 20,

    "xtick.labelsize": 17,

    "ytick.labelsize": 17,

    "legend.fontsize": 15,

    "axes.linewidth": 2.0,

    "xtick.major.width": 2.0,

    "ytick.major.width": 2.0,

    "xtick.minor.width": 1.4,

    "ytick.minor.width": 1.4,

    "xtick.major.size": 9,

    "ytick.major.size": 9,

    "xtick.minor.size": 5,

    "ytick.minor.size": 5

})


# ============================================================
# PANEL FUNCTION
# ============================================================

def make_panel(

    ax,

    alice_x,

    alice_y,

    alice_stat,

    alice_sys,

    py_x,

    py_y,

    py_err,

    label

):

    # ========================================================
    # PLOT CUT
    #
    # Only points with dNch/deta >= 10 are displayed.
    # The underlying analysis remains unchanged.
    # ========================================================

    alice_mask = (
        alice_x >= PLOT_MIN_DNDeta
    )

    py_mask = (
        py_x >= PLOT_MIN_DNDeta
    )


    # Apply the cut

    plot_alice_x = alice_x[
        alice_mask
    ]

    plot_alice_y = alice_y[
        alice_mask
    ]

    plot_alice_stat = alice_stat[
        alice_mask
    ]

    plot_alice_sys = alice_sys[
        alice_mask
    ]


    plot_py_x = py_x[
        py_mask
    ]

    plot_py_y = py_y[
        py_mask
    ]

    plot_py_err = py_err[
        py_mask
    ]


    # ========================================================
    # ALICE SYSTEMATIC
    # ========================================================

    ax.errorbar(

        plot_alice_x,

        plot_alice_y,

        yerr=plot_alice_sys,

        fmt="none",

        ecolor="red",

        elinewidth=1.4,

        capsize=3,

        alpha=0.9

    )


    # ========================================================
    # ALICE STATISTICAL
    # ========================================================

    ax.errorbar(

        plot_alice_x,

        plot_alice_y,

        yerr=plot_alice_stat,

        fmt="o",

        markersize=6,

        markerfacecolor="white",

        markeredgecolor="red",

        markeredgewidth=1.8,

        ecolor="red",

        elinewidth=1.4,

        capsize=3,

        linestyle="none",

        label="ALICE"

    )


    # ========================================================
    # PYTHIA
    # ========================================================

    ax.errorbar(

        plot_py_x,

        plot_py_y,

        yerr=plot_py_err,

        fmt="o",

        markersize=PYTHIA_MARKER_SIZE,

        markerfacecolor="black",

        markeredgecolor="black",

        markeredgewidth=1.8,

        ecolor="black",

        elinewidth=1.4,

        capsize=3,

        linestyle="none",

        label="PYTHIA 8 (CR + MPI ON)"

    )


    # ========================================================
    # PANEL LABEL
    # ========================================================

    ax.text(

        0.06,

        0.91,

        label,

        transform=ax.transAxes,

        fontsize=19

    )


    # ========================================================
    # AXES
    # ========================================================

    ax.set_xlabel(
        r"$dN_{\rm ch}/d\eta$"
    )

    ax.set_ylabel(
        r"$\langle p_T\rangle$ (GeV/$c$)"
    )


    # ========================================================
    # TICKS
    # ========================================================

    ax.tick_params(

        axis="both",

        which="major",

        direction="in",

        top=True,

        right=True,

        length=9,

        width=2

    )


    ax.tick_params(

        axis="both",

        which="minor",

        direction="in",

        top=True,

        right=True,

        length=5,

        width=1.4

    )


    ax.minorticks_on()

    ax.grid(False)


    # ========================================================
    # LEGEND
    # ========================================================

    ax.legend(

        frameon=False,

        loc="lower right",

        handlelength=1.5,

        handletextpad=0.5

    )


# ============================================================
# CREATE FIGURE
# ============================================================

fig, axes = plt.subplots(

    1,

    3,

    figsize=(18, 6.2)

)


# ============================================================
# PANEL 1 — 0-100%
# ============================================================

make_panel(

    axes[0],

    alice_all_x,

    alice_all_y,

    alice_all_stat,

    alice_all_sys,

    py_all_x,

    py_all_y,

    py_all_err,

    r"$0-100\%$"

)


# ============================================================
# PANEL 2 — 0-10%
# ============================================================

make_panel(

    axes[1],

    alice_jet_x,

    alice_jet_y,

    alice_jet_stat,

    alice_jet_sys,

    jet_x,

    jet_y,

    jet_err,

    r"$0-10\%$"

)


# ============================================================
# PANEL 3 — 90-100%
# ============================================================

make_panel(

    axes[2],

    alice_iso_x,

    alice_iso_y,

    alice_iso_stat,

    alice_iso_sys,

    iso_x,

    iso_y,

    iso_err,

    r"$90-100\%$"

)


# ============================================================
# AXIS LIMITS
#
# LOW-MULTIPLICITY REGION REMOVED FROM DISPLAY
# ============================================================

axes[0].set_xlim(
    10,
    45
)

axes[1].set_xlim(
    10,
    45
)

axes[2].set_xlim(
    10,
    45
)


axes[0].set_ylim(
    0.60,
    0.90
)

axes[1].set_ylim(
    0.60,
    1.10
)

axes[2].set_ylim(
    0.60,
    0.90
)



# ============================================================
# EXPORT NUMERICAL DATA FOR STREAMLIT
# ============================================================

from pathlib import Path

EXPORT_DIR = Path(__file__).resolve().parent / "data" / "mean_pt"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def export_panel_data(
    name,
    alice_x,
    alice_y,
    alice_stat,
    alice_sys,
    py_x,
    py_y,
    py_err
):
    # Preserve the original display cut.
    alice_mask = alice_x >= PLOT_MIN_DNDeta
    py_mask = py_x >= PLOT_MIN_DNDeta

    alice_df = pd.DataFrame({
        "dNch_deta": alice_x[alice_mask],
        "mean_pt": alice_y[alice_mask],
        "stat_error": alice_stat[alice_mask],
        "sys_error": alice_sys[alice_mask]
    })

    pythia_df = pd.DataFrame({
        "dNch_deta": py_x[py_mask],
        "mean_pt": py_y[py_mask],
        "stat_error": py_err[py_mask]
    })

    alice_df.to_csv(
        EXPORT_DIR / f"{name}_alice.csv",
        index=False
    )

    pythia_df.to_csv(
        EXPORT_DIR / f"{name}_pythia.csv",
        index=False
    )

    print(
        f"Exported {name}: "
        f"{len(alice_df)} ALICE points, "
        f"{len(pythia_df)} PYTHIA points"
    )


export_panel_data(
    "inclusive",
    alice_all_x, alice_all_y,
    alice_all_stat, alice_all_sys,
    py_all_x, py_all_y, py_all_err
)

export_panel_data(
    "jet_like",
    alice_jet_x, alice_jet_y,
    alice_jet_stat, alice_jet_sys,
    jet_x, jet_y, jet_err
)

export_panel_data(
    "isotropic",
    alice_iso_x, alice_iso_y,
    alice_iso_stat, alice_iso_sys,
    iso_x, iso_y, iso_err
)

print("All six mean-pT CSV files exported to:", EXPORT_DIR)


# ============================================================
# LAYOUT
# ============================================================

plt.tight_layout()


# ============================================================
# SAVE
# ============================================================

plt.savefig(

    "ALICE_PYTHIA_CRON_Fig4_reproduced_no_low_mult.png",

    dpi=600,

    bbox_inches="tight"

)


plt.savefig(

    "ALICE_PYTHIA_CRON_Fig4_reproduced_no_low_mult.pdf",

    format="pdf",

    bbox_inches="tight"

)


# ============================================================
# SHOW
# ============================================================

plt.show()
