"""Shared fixtures for the plot_atlas_fp test suite."""
import logging
import os
import sys

import pytest

# MAKE THE SCRIPT IMPORTABLE - IT LIVES AT THE REPO ROOT, NOT IN A PACKAGE
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

FIXTURE_DIR = os.path.join(REPO_ROOT, "tests", "fixtures")

# FIXTURE FILES
JOB00030 = os.path.join(FIXTURE_DIR, "job00030.txt")
AMDO_2025 = os.path.join(FIXTURE_DIR, "2025amdo_4405290_diff.txt")
SYNTHETIC_IBAND = os.path.join(FIXTURE_DIR, "synthetic_iband.txt")
UNSUPPORTED_PIPE_TABLE = os.path.join(
    FIXTURE_DIR, "AT2026oro_lightcurve_20260624t133608.txt")


@pytest.fixture
def log():
    """A quiet logger - the plotter only ever writes to it."""
    logger = logging.getLogger("plot_atlas_fp_tests")
    logger.addHandler(logging.NullHandler())
    logger.setLevel(logging.CRITICAL)
    return logger


@pytest.fixture
def make_plotter(log, tmp_path):
    """Build a plotter writing any output into a per-test temp directory."""
    def _make(resultFilePaths=None, **kwargs):
        from plot_atlas_fp import plotter
        return plotter(
            log=log,
            resultFilePaths=resultFilePaths or [JOB00030],
            outputDirectory=str(tmp_path),
            **kwargs
        )
    return _make


def filter_counts(epochs):
    """Count epochs per filter."""
    counts = {}
    for epoch in epochs:
        counts[epoch["F"]] = counts.get(epoch["F"], 0) + 1
    return counts


# THE COLUMNS OF A NATIVE ATLAS FP RESULTS FILE, IN ORDER
RESULTS_HEADER = ("###MJD m dm uJy duJy F err chi/N RA Dec x y maj min phi "
                  "apfit mag5sig Sky Obs")


def build_row(mjd, uJy, duJy, fil, chiN=1.0):
    """Build one results-file row. Only the columns the reader uses vary."""
    return (f"{mjd:.6f} -20.0 0.5 {uJy:.0f} {duJy:.0f} {fil} 0 {chiN:.2f} "
            "214.83749 35.08910 100.00 100.00 3.0 2.5 40.0 -0.4 19.0 18.8 "
            "05r61130o1427o")


def write_results_file(path, rows):
    """Write a results file from ``build_row`` output, returning its path."""
    with open(str(path), "w") as writeFile:
        writeFile.write(RESULTS_HEADER + "\n")
        writeFile.write("\n".join(rows) + "\n")
    return str(path)

