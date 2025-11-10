#!/bin/bash
set -e ### stop the script if it encounters errors

### go to the right directory relative to this script's location
PROJECT_ROOT="/global/cfs/cdirs/m3246/mpettee/hep/particlemind"
cd "$PROJECT_ROOT/data/raw/"

if [ -f "p8_ee_tt_ecm365_rootfiles.tgz" ]; then
    echo ".tgz file already exists."
fi

if [ ! -f "p8_ee_tt_ecm365_rootfiles.tgz" ]; then
    echo "Downloading data..."
    wget https://zenodo.org/records/14930758/files/p8_ee_tt_ecm365_rootfiles.tgz?download=1 -O p8_ee_tt_ecm365_rootfiles.tgz
fi

echo "Extracting files..."
tar xf p8_ee_tt_ecm365_rootfiles.tgz

echo "Cleaning up..."
mv p8_ee_tt_ecm365_rootfiles p8_ee_tt_ecm365
rm -f p8_ee_tt_ecm365_rootfiles.tgz

echo "Done!"
