#!/bin/bash

### go to the right directory relative to this script's location
PROJECT_ROOT="/global/cfs/cdirs/m3246/mpettee/hep/particlemind"
cd "$PROJECT_ROOT/data/raw/"

### run the Python script to turn ROOT files --> Parquet
python $PROJECT_ROOT/src/particlemind/data/cld_root2parquet_parallel.py -i /mnt/ceph/users/ewulff/data/cld/ -o /mnt/ceph/users/ewulff/data/cld/processed/parquet
