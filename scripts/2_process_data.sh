#!/bin/bash

### go to the right directory relative to this script's location
PROJECT_ROOT="/global/cfs/cdirs/m3246/mpettee/hep/particlemind"

### run the Python script to turn ROOT files --> Parquet
### (note: use --parallel flag to turn on parallel processing, otherwise files are processed one at a time, i.e. veeeery slowly.)
uv run python $PROJECT_ROOT/src/particlemind/data/root_to_parquet.py --parallel -i $PROJECT_ROOT/data/raw/p8_ee_tt_ecm365_rootfiles/ -o $PROJECT_ROOT/data/processed/p8_ee_tt_ecm365/
