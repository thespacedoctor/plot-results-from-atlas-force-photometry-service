# Plot Results from ATLAS Force Photometry Service

The [gist containing this content and be found here](https://gist.github.com/86777fa5a9567b7939e8d84fd8cf6a76).

Use this script to plot the output returned from the [ATLAS forced photometry service](https://fallingstar-data.com/forcedphot/). You will find an example output file here for testing purposes (`job01088.txt`); this is forced photometry generated at the location of object `ATLAS20bdvs` == `AT2020wol` (RA=29.86137, DEC=+30.72675).

The script will perform sigma-clipping of the data for you to remove rogue data points. You can also optionally 'stack' single-filter photometry across epochs.
 
## Installation

```bash
git clone https://gist.github.com/86777fa5a9567b7939e8d84fd8cf6a76.git atlas-fp
cd atlas-fp
chmod 777 plot_atlas_fp.py 
conda create -n atlas-fp python=3.7 pip numpy matplotlib multiprocess astropy unicodecsv
conda activate atlas-fp
pip install fundamentals astrocalc
```

To make the script available system wide (*OPTIONAL*):

```bash
sudo ln -s $PWD/plot_atlas_fp.py /usr/local/bin/plot_atlas_fp
```

*Note you will have to install all dependencies into the native python version site-packages for this to work.*

## A Note on Data Cleaning

The script uses a rolling-window to identify and clip rogue data-points from the photometry results file. For each and every data point in a given filter a median flux and median-absolute-distribution (MAD) value is calculated for a fixed number of neighbouring points either side of the data-point. If the data-point is found beyond a threshold number of MAD values from the median then it is clipped from the dataset and not included in the lightcurve plots or stacked photometry sets.

## Usage

```bash
Usage:
    plot_atlas_fp plot <resultsPath> [<mjdMin> <mjdMax> --n=<objectName> --o=<outputDirectory>]
    plot_atlas_fp stack <binDays> <resultsPath> [<mjdMin> <mjdMax> --n=<objectName> --o=<outputDirectory>]

Commands:
    plot                    plot the photometry
    stack                   stack photometry across epochs (and same filter) and plot

Options:
    resultsPath             path to results file or directory of results files returned by the ATLAS FP service
    mjdMin                  min mjd to plot
    mjdMax                  max mjd to plot
    binDays                 size bins to stack photometry within (days)

    --n=<objectName>        give a name for the object you are plotting (for plot title and filename). This is ignored if `resultsPath` is a directory
    --o=<outputDirectory>   path to the directory to output the plots to. Default is CWD.

    -h, --help              show this help message
```

### Plotting a Lightcurve

To plot a lightcurve of a single results file:

```bash
plot_atlas_fp.py plot job01088.txt
```

This produces the following plot:

[![](https://live.staticflickr.com/65535/50794382318_6798c70281_z.png)](https://live.staticflickr.com/65535/50794382318_6798c70281_o.png)

To add a title to plot:

```bash
plot_atlas_fp.py plot job01088.txt --n=ATLAS20bdvs
```

### Defining the Plot's Temporal-Range

To limit the data displayed in the plot use the `mjdMin` and `mjdMax` options:

```bash
plot_atlas_fp.py plot job01088.txt 59130 59200 --n=ATLAS20bdvs
```

[![](https://live.staticflickr.com/65535/50795187841_536a2ea050_z.png)](https://live.staticflickr.com/65535/50795187841_536a2ea050_o.png)

### Stacking Photometry

To stack the intra-night data use the `stack` command instead of `plot`:

```bash
plot_atlas_fp.py stack 1 job01088.txt --n=ATLAS20bdvs
```

[![](https://live.staticflickr.com/65535/50795202511_01f18d94cd_z.png)](https://live.staticflickr.com/65535/50795202511_01f18d94cd_o.png)

You can go further and stack data across multiple nights by increasing the `binDays` variable. For example let's stack the data in 7 day bins:

```bash
plot_atlas_fp.py stack 7 job01088.txt --n=ATLAS20bdvs
```

[![](https://live.staticflickr.com/65535/50795213046_97cb928fde_z.png)](https://live.staticflickr.com/65535/50795213046_97cb928fde_o.png)

If you are plotting the stacked photometry lightcurves, a txt file containing the calculated photometry is written beside the plot files. Here's the stacked photometry data generated for the example above:

```text
# MJD (average of the points included, after clipping)
# uJy (average of the points included after clipping)
# duJy (error on the average point after clipping)
# F (filter)
# n (number of points included in the stacked detection, after
# clipping)
MJD,uJy,duJy,F,n
59103.09,1.44,3.59,o,9
59107.55,1.50,4.62,c,4
59111.48,4.00,5.75,c,4
59112.62,-5.00,4.44,o,9
59115.61,-4.33,4.62,c,3
59118.93,1.53,3.65,o,15
59123.47,-7.50,19.09,o,2
59131.13,-0.50,4.24,o,10
59135.52,47.00,20.50,c,4
59139.47,144.50,5.50,c,4
59139.59,126.54,3.05,o,13
59143.39,161.60,18.78,c,5
59147.01,203.45,3.92,o,11
59161.10,204.90,5.38,o,10
59169.41,161.50,36.77,o,2
59182.28,129.55,7.02,o,11
59185.43,107.50,9.62,o,4
```

### Plotting a Directory of Result Files

If plotting a directory of result files simply pass in the path to the directory as the `resultsPath` variable alongside a path to an output directory:

```bash
plot_atlas_fp.py stack 1 /path/to/atlas_force_phot_result_set --o=~/Desktop/stacked
```

This will be a lot quicker than plotting the result files individually.
