"""Tests for stacking same-filter photometry into time bins."""
import math
import os

from conftest import JOB00030


def build_magnitudes(**perFilter):
    """Build a magnitudes dict of the shape stack_photometry expects."""
    from plot_atlas_fp import FILTERS
    magnitudes = {}
    for fil in FILTERS:
        mjds, mags, magErrs = perFilter.get(fil, ([], [], []))
        magnitudes[fil] = {
            "mjds": list(mjds), "mags": list(mags), "magErrs": list(magErrs)}
    return magnitudes


def test_stacks_w_band_points_within_a_bin(make_plotter, tmp_path):
    # ARRANGE
    myplotter = make_plotter(stackBinSize=1.)
    magnitudes = build_magnitudes(
        w=([59000.1, 59000.4, 59000.7], [10., 20., 30.], [1., 1., 1.]))

    # ACT
    stacked = myplotter.stack_photometry(
        magnitudes, fpFile=str(tmp_path / "obj.txt"), binningDays=1.)

    # ASSERT - THREE POINTS IN ONE NIGHT BECOME ONE STACKED POINT
    assert len(stacked["w"]["mjds"]) == 1
    assert stacked["w"]["mags"][0] == 20.
    assert stacked["w"]["n"][0] == 3


def test_stacks_i_band_points_within_a_bin(make_plotter, tmp_path):
    # ARRANGE
    myplotter = make_plotter(stackBinSize=1.)
    magnitudes = build_magnitudes(I=([59000.1, 59000.6], [4., 6.], [2., 2.]))

    # ACT
    stacked = myplotter.stack_photometry(
        magnitudes, fpFile=str(tmp_path / "obj.txt"), binningDays=1.)

    # ASSERT
    assert stacked["I"]["mags"] == [5.]
    assert stacked["I"]["n"] == [2]


def test_never_stacks_points_across_different_filters(make_plotter, tmp_path):
    # ARRANGE - SAME NIGHT, THREE DIFFERENT FILTERS
    myplotter = make_plotter(stackBinSize=1.)
    magnitudes = build_magnitudes(
        o=([59000.1], [10.], [1.]),
        c=([59000.2], [20.], [1.]),
        w=([59000.3], [30.], [1.]))

    # ACT
    stacked = myplotter.stack_photometry(
        magnitudes, fpFile=str(tmp_path / "obj.txt"), binningDays=1.)

    # ASSERT - EACH FILTER KEEPS ITS OWN SINGLE POINT
    assert stacked["o"]["mags"] == [10.]
    assert stacked["c"]["mags"] == [20.]
    assert stacked["w"]["mags"] == [30.]


def test_separates_points_falling_into_different_bins(make_plotter, tmp_path):
    # ARRANGE
    myplotter = make_plotter(stackBinSize=1.)
    magnitudes = build_magnitudes(
        w=([59000.1, 59000.2, 59002.5], [10., 20., 99.], [1., 1., 1.]))

    # ACT
    stacked = myplotter.stack_photometry(
        magnitudes, fpFile=str(tmp_path / "obj.txt"), binningDays=1.)

    # ASSERT
    assert sorted(stacked["w"]["n"]) == [1, 2]


def test_combines_errors_in_quadrature_over_the_number_of_points(make_plotter, tmp_path):
    # ARRANGE
    myplotter = make_plotter(stackBinSize=1.)
    magErrs = [3., 4.]
    magnitudes = build_magnitudes(w=([59000.1, 59000.2], [10., 20.], magErrs))

    # ACT
    stacked = myplotter.stack_photometry(
        magnitudes, fpFile=str(tmp_path / "obj.txt"), binningDays=1.)

    # ASSERT
    expected = math.sqrt(3. ** 2 + 4. ** 2) / 2
    assert stacked["w"]["magErrs"][0] == expected


def test_writes_w_band_rows_into_the_stacked_photometry_file(make_plotter, tmp_path):
    # ARRANGE
    myplotter = make_plotter(stackBinSize=1.)
    magnitudes = build_magnitudes(
        o=([59000.1], [10.], [1.]), w=([59000.3], [30.], [1.]))

    # ACT
    myplotter.stack_photometry(
        magnitudes, fpFile=str(tmp_path / "obj.txt"), binningDays=1.)

    # ASSERT
    outputPath = os.path.join(
        str(tmp_path), "obj_atlas_fp_stacked_1.0_days.txt")
    with open(outputPath) as readFile:
        content = readFile.read()
    assert ",w," in content
    assert ",o," in content


def test_returns_empty_filter_sets_untouched(make_plotter, tmp_path):
    # ARRANGE - NO DATA AT ALL
    myplotter = make_plotter(stackBinSize=1.)
    magnitudes = build_magnitudes()

    # ACT
    stacked = myplotter.stack_photometry(
        magnitudes, fpFile=str(tmp_path / "obj.txt"), binningDays=1.)

    # ASSERT
    assert all(not stacked[fil]["mjds"] for fil in stacked)


def test_stacks_real_w_band_data_read_from_a_results_file(make_plotter, tmp_path):
    """End-to-end over the reader: real w-band epochs reach the stacker."""
    # ARRANGE
    from plot_atlas_fp import FILTERS
    myplotter = make_plotter(stackBinSize=1.)
    epochs = myplotter.read_and_sigma_clip_data(JOB00030)
    magnitudes = {fil: {"mjds": [], "mags": [], "magErrs": []}
                  for fil in FILTERS}
    for epoch in epochs:
        magnitudes[epoch["F"]]["mjds"].append(epoch["MJD"])
        magnitudes[epoch["F"]]["mags"].append(epoch["uJy"])
        magnitudes[epoch["F"]]["magErrs"].append(epoch["duJy"])

    # ACT
    stacked = myplotter.stack_photometry(
        magnitudes, fpFile=str(tmp_path / "job00030.txt"), binningDays=1.)

    # ASSERT
    assert len(stacked["w"]["mjds"]) > 0
    assert all(n >= 1 for n in stacked["w"]["n"])
