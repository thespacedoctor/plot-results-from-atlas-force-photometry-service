# Plot Results from ATLAS Force Photometry Service

- [x] move repo in Tower to the gist folder
- [ ] add code file(s) to the gist folder and push to github (via Tower)
- [ ] complete this README file (below the line)
- [ ] remove these tasks
- [ ] push changes to github
- [ ] make gist public/private (via Edit button)
- [ ] share gist where needed
- [ ] copy and paste the contents of this README into drafts and push into my zettelkasten archive

---

The [gist containing this content and be found here](https://gist.github.com/86777fa5a9567b7939e8d84fd8cf6a76).

Use this script to plot the output returned from the [ATLAS forced photometry service](https://fallingstar-data.com/forcedphot/). You will find an example output file here for testing purposes (`job01088.txt`); this is forced photometry generated at the location of object `ATLAS20bdvs` == `AT2020wol` (RA=29.86137, DEC=+30.72675).

The script will perform sigma-clipping of the data for you to remove rogue data points. You can also optionally 'stack' single-filter photometry from individual nights. Files produced are date-stamped.
 
## Installation

```bash
git clone https://gist.github.com/86777fa5a9567b7939e8d84fd8cf6a76.git atlas-fp
cd atlas-fp
chmod 777 plot-atlas-fp.py 
conda create -n atlas-fp python=3.7 pip numpy matplotlib
conda activate atlas-fp
pip install fundamentals astrocalc
```

To make the script available system wide (*OPTIONAL*):

```bash
chmod 777 <<<>>>.py
sudo ln -s $PWD/plot-atlas-fp.py /usr/local/bin/plot-atlas-fp
```

*Note you will have to install all dependencies into the native python version site-packages for this to work.*

## Usage

```bash
Usage:
    plot-atlas-fp <fpFile> [-s <objectName>]

Options:
    fpFile                path to the results file returned by the ATLAS FP service
    objectName            give a name for the object you are plotting (for plot title and filename)
    -h, --help            show this help message
    -s, --stacked         stack photometry from the smae night (and same filter)
```

To plot the non-stacked data:

```bash
> plot-atlas-fp.py job01088.txt
The plot can be found at `atlas_fp_lightcurve_20201203t155951.pdf`
```

This produces the following plot:

[![](https://live.staticflickr.com/65535/50676025996_8995a4345d_z.png)](https://live.staticflickr.com/65535/50676025996_8995a4345d_o.png)

To stack the intra-night data and give the plot and file the name of the source you're plotting:

```bash
> plot-atlas-fp.py job01088.txt -s ATLAS20bdvs
The plot can be found at `ATLAS20bdvs_atlas_fp_lightcurve_20201203t160321.pdf`
```

And here is the stacked-photometry plot produced:

[![](https://live.staticflickr.com/65535/50676033766_361b8c1f59_z.png)](https://live.staticflickr.com/65535/50676033766_361b8c1f59_o.png)
