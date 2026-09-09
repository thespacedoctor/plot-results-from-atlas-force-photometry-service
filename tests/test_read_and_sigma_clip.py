"""Tests for reading and sigma-clipping ATLAS forced photometry results files."""
import pytest

from conftest import (AMDO_2025, JOB00030, SYNTHETIC_IBAND,
                      UNSUPPORTED_PIPE_TABLE, build_row, filter_counts,
                      write_results_file)


def test_reads_w_band_epochs_from_a_results_file(make_plotter):
    # ARRANGE
    myplotter = make_plotter()

    # ACT
    epochs = myplotter.read_and_sigma_clip_data(JOB00030)

    # ASSERT
    assert filter_counts(epochs).get("w", 0) > 0


def test_reads_i_band_epochs_from_a_results_file(make_plotter):
    # ARRANGE
    myplotter = make_plotter(resultFilePaths=[SYNTHETIC_IBAND])

    # ACT
    epochs = myplotter.read_and_sigma_clip_data(SYNTHETIC_IBAND)

    # ASSERT
    assert filter_counts(epochs).get("I", 0) > 0


def test_reads_every_supported_filter_present_in_the_file(make_plotter):
    # ARRANGE
    myplotter = make_plotter()

    # ACT
    epochs = myplotter.read_and_sigma_clip_data(JOB00030)

    # ASSERT
    assert set(filter_counts(epochs)) == {"c", "o", "w"}


def test_returns_only_the_filters_present_when_no_w_band_data_exists(make_plotter):
    # ARRANGE
    myplotter = make_plotter(resultFilePaths=[AMDO_2025])

    # ACT
    epochs = myplotter.read_and_sigma_clip_data(AMDO_2025)

    # ASSERT
    assert set(filter_counts(epochs)) == {"c", "o"}


def test_clips_each_filter_independently(make_plotter, tmp_path):
    """Outliers planted in one filter must not clip points in another.

    Two results files are built from the same clean c-band epochs. One of them
    also carries a set of wildly noisy o-band epochs. If clipping leaked across
    filters, the c-band epochs surviving the noisy file would differ from those
    surviving the clean one.
    """
    # ARRANGE - CLEAN c-BAND EPOCHS, SHARED BY BOTH FILES
    cleanRows = [build_row(mjd=59000. + i, uJy=100., duJy=5., fil="c")
                 for i in range(20)]
    # NOISY o-BAND EPOCHS - ALTERNATING WILD SWINGS AROUND ZERO
    noisyRows = [build_row(mjd=59000. + i, uJy=(9000. if i % 2 else -9000.),
                           duJy=5., fil="o")
                 for i in range(20)]

    cleanFile = write_results_file(tmp_path / "clean.txt", cleanRows)
    noisyFile = write_results_file(tmp_path / "noisy.txt", cleanRows + noisyRows)

    myplotter = make_plotter()

    # ACT
    fromClean = myplotter.read_and_sigma_clip_data(cleanFile)
    fromNoisy = myplotter.read_and_sigma_clip_data(noisyFile)

    # ASSERT - THE c-BAND SURVIVORS ARE IDENTICAL EITHER WAY
    cFromClean = [e["MJD"] for e in fromClean if e["F"] == "c"]
    cFromNoisy = [e["MJD"] for e in fromNoisy if e["F"] == "c"]
    assert cFromClean == cFromNoisy
    assert len(cFromClean) == 20


def test_clips_outliers_within_a_filter(make_plotter, tmp_path):
    """Sanity check on the arrangement above: the clipper does clip."""
    # ARRANGE - A TIGHT o-BAND SEQUENCE WITH ONE WILD POINT IN THE MIDDLE
    rows = [build_row(mjd=59000. + i, uJy=100., duJy=1., fil="o")
            for i in range(20)]
    rows[10] = build_row(mjd=59010., uJy=9000., duJy=1., fil="o")
    resultsFile = write_results_file(tmp_path / "outlier.txt", rows)
    myplotter = make_plotter()

    # ACT
    epochs = myplotter.read_and_sigma_clip_data(resultsFile)

    # ASSERT
    assert 9000. not in [e["uJy"] for e in epochs]
    assert len(epochs) == 19


def test_drops_epochs_with_very_high_flux_error(make_plotter):
    # ARRANGE
    myplotter = make_plotter()

    # ACT
    epochs = myplotter.read_and_sigma_clip_data(JOB00030)

    # ASSERT
    assert all(epoch["duJy"] <= 4000 for epoch in epochs)


def test_drops_epochs_with_poor_chi_squared(make_plotter):
    # ARRANGE
    myplotter = make_plotter()

    # ACT
    epochs = myplotter.read_and_sigma_clip_data(JOB00030)

    # ASSERT
    assert all(epoch["chi/N"] <= 100 for epoch in epochs)


def test_quality_cuts_apply_to_w_band_epochs_too(make_plotter):
    # ARRANGE
    myplotter = make_plotter()

    # ACT
    epochs = myplotter.read_and_sigma_clip_data(JOB00030)
    wEpochs = [epoch for epoch in epochs if epoch["F"] == "w"]

    # ASSERT
    assert len(wEpochs) > 0
    assert all(e["duJy"] <= 4000 and e["chi/N"] <= 100 for e in wEpochs)


def test_restricts_epochs_to_the_requested_mjd_window(make_plotter):
    # ARRANGE
    mjdMin, mjdMax = 61130.0, 61133.0
    myplotter = make_plotter(mjdMin=mjdMin, mjdMax=mjdMax)

    # ACT
    epochs = myplotter.read_and_sigma_clip_data(JOB00030)

    # ASSERT
    assert len(epochs) > 0
    assert all(mjdMin <= epoch["MJD"] <= mjdMax for epoch in epochs)


def test_mjd_window_applies_to_w_band_epochs_too(make_plotter):
    # ARRANGE
    mjdMin, mjdMax = 61130.0, 61131.0
    myplotter = make_plotter(mjdMin=mjdMin, mjdMax=mjdMax)

    # ACT
    epochs = myplotter.read_and_sigma_clip_data(JOB00030)
    wEpochs = [epoch for epoch in epochs if epoch["F"] == "w"]

    # ASSERT
    assert len(wEpochs) > 0
    assert all(mjdMin <= epoch["MJD"] <= mjdMax for epoch in wEpochs)


def test_sparse_filter_with_fewer_points_than_the_clipping_window(make_plotter):
    """CHARACTERISES CURRENT BEHAVIOUR - NOT AN ASSERTION OF CORRECTNESS.

    The rolling window is 11 points wide, but ``job00030.txt`` holds only 8
    c-band epochs. The clipper currently returns an all-False mask in that
    case, so every sparse-filter epoch survives unclipped. Documented here so
    the behaviour is visible rather than folklore; see the note in the README
    if this ever needs revisiting.
    """
    # ARRANGE
    myplotter = make_plotter()

    # ACT
    epochs = myplotter.read_and_sigma_clip_data(JOB00030)

    # ASSERT - ALL 8 RAW c EPOCHS SURVIVE
    assert filter_counts(epochs)["c"] == 8


def test_rejects_a_file_that_is_not_in_the_native_format(make_plotter):
    """CHARACTERISES CURRENT BEHAVIOUR - the pipe-delimited multi-survey export
    is not supported. It must fail loudly rather than yield garbage epochs."""
    # ARRANGE
    myplotter = make_plotter(resultFilePaths=[UNSUPPORTED_PIPE_TABLE])

    # ACT / ASSERT
    with pytest.raises(KeyError):
        myplotter.read_and_sigma_clip_data(UNSUPPORTED_PIPE_TABLE)
