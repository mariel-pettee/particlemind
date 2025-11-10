#!/bin/bash

### go to the right directory relative to this script's location
PROJECT_ROOT="/global/cfs/cdirs/m3246/mpettee/hep/particlemind"

uv run python $PROJECT_ROOT/src/particlemind/training/train_vqvae.py --train_embedder