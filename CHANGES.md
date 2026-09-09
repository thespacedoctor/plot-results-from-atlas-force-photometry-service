## Release Notes

**v1.1.0 - September 9, 2026**

- **ENHANCEMENT** - w-band (and I-band) photometry is now read, clipped, stacked and plotted
- **REFACTOR** - filter handling is driven from a single `FILTERS` constant rather than duplicated per filter
- **TEST** - added a pytest suite covering the results-file reader and the photometry stacker

**v1.0.1 - April 16, 2024**

- **FIXED** - small bug in stacked error combination
