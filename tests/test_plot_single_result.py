"""Tests for drawing a single result file onto the shared figure."""
import os

import pytest

from conftest import AMDO_2025, JOB00030, build_row, write_results_file


@pytest.fixture
def canvas():
    """The figure, axes and mjd converter that plot() would normally build."""
    import matplotlib.pyplot as plt
    from astrocalc.times import conversions
    import logging

    log = logging.getLogger("plot_atlas_fp_tests")
    fig = plt.figure(num=None, figsize=(10, 10), dpi=100, frameon=True)
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=False, frameon=True)
    ax.twinx()
    ax.twiny()
    yield fig, ax, conversions(log=log)
    plt.close(fig)


def plotted_filters(ax):
    """The filter labels of the artists on the axes, in wavelength order.

    The script builds its legend from these same artists, in this same order,
    but draws it with the global ``plt.legend()``, which attaches the legend to
    whichever figure pyplot considers current - not reliably the figure under
    test. So assert on the artists the legend is built from rather than on
    pyplot's global state.
    """
    return [container.get_label() for container in reversed(ax.containers)]


def drawn_artist_count(ax):
    """How many artists are still attached to the axes.

    ``ax.containers`` keeps stale entries after a container is removed, so
    count the artists that would actually render instead.
    """
    return len(ax.lines) + len(ax.collections)


def test_draws_an_artist_for_every_populated_filter(make_plotter, canvas):
    # ARRANGE
    fig, ax, converter = canvas
    myplotter = make_plotter()

    # ACT
    myplotter.plot_single_result(
        fpFile=JOB00030, fig=fig, converter=converter, ax=ax)

    # ASSERT - job00030 CARRIES c, o AND w, IN WAVELENGTH ORDER
    assert plotted_filters(ax) == ['c-band mag ', 'o-band mag ', 'w-band mag ']


def test_omits_filters_with_no_data(make_plotter, canvas):
    # ARRANGE - THIS FILE HAS NO w AND NO I EPOCHS
    fig, ax, converter = canvas
    myplotter = make_plotter(resultFilePaths=[AMDO_2025])

    # ACT
    myplotter.plot_single_result(
        fpFile=AMDO_2025, fig=fig, converter=converter, ax=ax)

    # ASSERT
    assert plotted_filters(ax) == ['c-band mag ', 'o-band mag ']


def test_draws_shorter_wavelength_filters_on_top(make_plotter, canvas):
    """c must be drawn after o, so cyan sits over orange where they overlap."""
    # ARRANGE
    fig, ax, converter = canvas
    myplotter = make_plotter()

    # ACT
    myplotter.plot_single_result(
        fpFile=JOB00030, fig=fig, converter=converter, ax=ax)

    # ASSERT - CONTAINERS ARE IN DRAW ORDER; c IS ADDED LAST
    drawOrder = [container.get_label() for container in ax.containers]
    assert drawOrder.index('c-band mag ') > drawOrder.index('o-band mag ')


def test_removes_its_points_so_they_do_not_bleed_into_the_next_plot(make_plotter, canvas):
    """The figure is reused across files - nothing may survive a plot call."""
    # ARRANGE
    fig, ax, converter = canvas
    myplotter = make_plotter(resultFilePaths=[JOB00030, AMDO_2025])

    # ACT
    myplotter.plot_single_result(
        fpFile=JOB00030, fig=fig, converter=converter, ax=ax)
    afterFirst = drawn_artist_count(ax)
    myplotter.plot_single_result(
        fpFile=AMDO_2025, fig=fig, converter=converter, ax=ax)

    # ASSERT - EACH CALL LEAVES THE SHARED AXES EMPTY AGAIN
    assert afterFirst == 0
    assert drawn_artist_count(ax) == 0


def test_returns_none_when_the_file_holds_no_usable_data(make_plotter, canvas, tmp_path):
    # ARRANGE - EVERY EPOCH FAILS THE CHI-SQUARED CUT
    fig, ax, converter = canvas
    rows = [build_row(mjd=59000. + i, uJy=100., duJy=5., fil="o", chiN=999.)
            for i in range(5)]
    resultsFile = write_results_file(tmp_path / "unusable.txt", rows)
    myplotter = make_plotter(resultFilePaths=[resultsFile])

    # ACT
    filePath = myplotter.plot_single_result(
        fpFile=resultsFile, fig=fig, converter=converter, ax=ax)

    # ASSERT - NO PLOT, AND NOTHING LEFT ON THE SHARED AXES
    assert filePath is None
    assert drawn_artist_count(ax) == 0


def test_writes_a_plot_file_named_after_the_results_file(make_plotter, canvas, tmp_path):
    # ARRANGE
    fig, ax, converter = canvas
    myplotter = make_plotter()

    # ACT
    filePath = myplotter.plot_single_result(
        fpFile=JOB00030, fig=fig, converter=converter, ax=ax)

    # ASSERT
    assert os.path.basename(filePath) == "job00030_atlas_fp_lightcurve.png"
    assert os.path.exists(filePath)
